import json
import time
from collections import defaultdict
from datetime import datetime

from django.conf import settings
from InstagramAPI import InstagramAPI

from ighelper.exceptions import (
    InstagramException,
    InstagramMediaNotFoundException,
)
from ighelper.helpers import FrozenDict
from ighelper.models import Media


class InstagramSession:
    def __init__(self):
        self.start = datetime.now()

    @property
    def is_expired(self):
        time_passed = datetime.now() - self.start
        return time_passed.seconds > settings.INSTAGRAM_SESSION_LIFETIME


class Instagram:
    _MESSAGE_MEDIA_NOT_FOUND = 'Media not found or unavailable'
    _MESSAGE_MEDIA_NOT_FOUND2 = 'You cannot edit this media'
    _MESSAGE_MEDIA_NOT_FOUND3 = 'Sorry, this photo has been deleted.'
    _session_real = None
    _session_fake = None

    def __init__(self, user_id_real, username_real, password_real, username_fake, password_fake):
        self._user_id_real = user_id_real
        self._username_real = username_real
        self._password_real = password_real
        self._username_fake = username_fake
        self._password_fake = password_fake
        self._api_fake = InstagramAPI(self._username_fake, self._password_fake)
        self._api_fake.setProxy(settings.PROXY)
        self._api_real = InstagramAPI(self._username_real, self._password_real)
        self._api_real.setProxy(settings.PROXY)

    def _login_fake(self):
        if self._session_fake is None:
            self._session_fake = InstagramSession()

        self._api_fake.login(self._session_fake.is_expired)
        # Slow down in attempt to avoid blocking by Instagram
        time.sleep(settings.INSTAGRAM_SLEEP)

    def _login_real(self):
        if self._session_real is None:
            self._session_real = InstagramSession()

        self._api_real.login(self._session_real.is_expired)
        # Slow down in attempt to avoid blocking by Instagram
        time.sleep(settings.INSTAGRAM_SLEEP)

    @staticmethod
    def _get_user_data(user):
        return {
            'instagram_id': user['pk'],
            'username': user['username'],
            'name': user['full_name'],
            'avatar': user['profile_pic_url']
        }

    def get_followers(self):
        self._login_real()
        # If we use a fake account we get only some of the followers.
        self._api_real.getSelfUserFollowers()
        response = self._api_real.LastJson
        if 'users' not in response:
            response = json.dumps(response)
            raise InstagramException(f'Incorrect response. API response - {response}')

        return [self._get_user_data(user) for user in response['users']]

    def get_likes_instagram_users_data_and_deleted_medias(self, medias_ids):
        """
        Get likes and deleted medias.

        Return a tuple - (likes, instagram_users, deleted_medias) - (dict of lists, list of dicts, list).

        Example:
        (
         'media_id': ['user_id']},
         [{
            'instagram_id': 'instagram_id',
            'username': 'username',
            'name': 'name',
            'avatar': 'avatar'}],
         ['media_id']
        )
        """
        self._login_fake()
        i = 0
        total_medias = len(medias_ids)
        likes = []
        medias_deleted = []
        likes = defaultdict(list)
        instagram_users = set()
        for media_id in medias_ids:
            i += 1
            success = self._api_fake.getMediaLikers(media_id)
            result = self._api_fake.LastJson
            if success:
                users = result['users']
                for user in users:
                    user_data = self._get_user_data(user)
                    user_data = FrozenDict(**user_data)
                    instagram_users.add(user_data)
                    likes[media_id].append(user_data['instagram_id'])
            else:
                if 'message' in result and result['message'] == self._MESSAGE_MEDIA_NOT_FOUND3:
                    medias_deleted.append(media_id)
                else:
                    api_response = json.dumps(result)
                    raise InstagramException(f'Error getting media likes. API response - {api_response}')
            # Slow down in attempt to avoid blocking by Instagram
            time.sleep(settings.INSTAGRAM_SLEEP)
            print(f'Loaded {i} / {total_medias}')

        instagram_users = [dict(u) for u in instagram_users]
        return likes, instagram_users, medias_deleted

    @staticmethod
    def _get_media_data(m):
        def get_video(media):
            if media['media_type'] == Media.MEDIA_TYPE_VIDEO:
                return media['video_versions'][0]['url']
            return None

        def get_location(media):
            if 'location' in media:
                return media['location']['name'], media['location']['city']
            return '', ''

        def get_caption(media):
            if 'caption' in media and media['caption']:
                return media['caption']['text']
            return ''

        def get_views_count(media):
            if 'view_count' in media:
                return media['view_count']
            return None

        location_name, city = get_location(m)
        images = m['image_versions2']['candidates']
        return {
            'instagram_id': m['id'],
            'media_type': m['media_type'],
            'date': datetime.fromtimestamp(m['taken_at']),
            'caption': get_caption(m),
            'location_name': location_name,
            'city': city,
            'image': images[0]['url'],
            'image_small': images[1]['url'],
            'video': get_video(m),
            'views_count': get_views_count(m),
        }

    def get_media(self, media_id):
        self._login_fake()
        success = self._api_fake.mediaInfo(media_id)
        result = self._api_fake.LastJson
        if success:
            return self._get_media_data(result['items'][0])

        if 'message' in result and result['message'] == self._MESSAGE_MEDIA_NOT_FOUND:
            return None
        else:
            api_response = json.dumps(result)
            raise InstagramException(f'Error getting media. API response - {api_response}')

    def get_medias(self, media_ids=None):  # pylint: disable=too-many-locals
        self._login_fake()
        if media_ids is None:
            media_ids = []
        self._api_fake.getUsernameInfo(self._user_id_real)
        response = self._api_fake.LastJson
        if 'user' not in response:
            response = json.dumps(response)
            raise InstagramException(f'Incorrect response. API response - {response}')

        media_number = response['user']['media_count']

        medias = []
        max_id = ''
        pages = media_number // settings.MEDIAS_PER_PAGE
        stop_loading = False
        for i in range(pages + 1):
            self._api_fake.getUserFeed(self._user_id_real, maxid=max_id)
            medias_on_page = self._api_fake.LastJson['items']
            for media in medias_on_page:
                media_id = media['id']
                if media_id in media_ids:
                    stop_loading = True
                    break
                medias.append(media)
            if not self._api_fake.LastJson['more_available']:
                stop_loading = True
            if stop_loading:
                break
            max_id = self._api_fake.LastJson['next_max_id']
            page = i + 1
            print(f'Loaded {page} / {pages}')
            # Slow down in attempt to avoid blocking by Instagram
            time.sleep(settings.INSTAGRAM_SLEEP)

        medias_output = []
        for m in medias:
            media = self._get_media_data(m)
            medias_output.append(media)

        return medias_output

    def get_followed(self):
        self._login_fake()
        self._api_fake.getUserFollowings(self._user_id_real)
        response = self._api_fake.LastJson
        if 'users' not in response:
            response = json.dumps(response)
            raise InstagramException(f'Incorrect response. API response - {response}')
        users = response['users']
        return [self._get_user_data(user) for user in users]

    def update_media_caption(self, media_id, caption):
        self._login_real()
        success = self._api_real.editMedia(media_id, caption)
        if not success:
            response = self._api_real.LastJson
            if 'message' in response and response['message'] == self._MESSAGE_MEDIA_NOT_FOUND2:
                raise InstagramMediaNotFoundException()
            response = json.dumps(response)
            raise InstagramException(f'Error updating media caption. API response - {response}')

    def follow(self, user_id):
        self._login_real()
        success = self._api_real.follow(user_id)
        if not success:
            response = json.dumps(self._api_real.LastJson)
            raise InstagramException(f'Error following a user. API response - {response}')

    def unfollow(self, user_id):
        self._login_real()
        success = self._api_real.unfollow(user_id)
        if not success:
            response = json.dumps(self._api_real.LastJson)
            raise InstagramException(f'Error unfollowing a user. API response - {response}')

    def block(self, user_id):
        self._login_real()
        success = self._api_real.block(user_id)
        if not success:
            response = json.dumps(self._api_real.LastJson)
            raise InstagramException(f'Error blocking a user. API response - {response}')

    def delete_media(self, media_id, media_type):
        self._login_real()
        success = self._api_real.deleteMedia(media_id, media_type)
        if not success:
            response = json.dumps(self._api_real.LastJson)
            raise InstagramException(f'Error deleting media caption. API response - {response}')
