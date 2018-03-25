import json

from django.shortcuts import get_object_or_404

from ighelper.models import Follower, InstagramUser

from .mixins import AjaxView, InstagramAjaxView, TemplateView


class FollowersView(TemplateView):
    template_name = 'followers.html'

    def get_context_data(self):
        return {'followers': json.dumps(self.request.user.get_followers())}


class LoadFollowersView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        instagram_followers = self.instagram.get_followers()
        current_followers = self.user.followers.all()

        # Remove followers which have been deleted / have unfollowed
        followers_instagram_ids = [x['instagram_id'] for x in instagram_followers]
        for follower in current_followers:
            if follower.instagram_id not in followers_instagram_ids:
                follower.delete()

        for instagram_follower in instagram_followers:
            instagram_users = InstagramUser.objects.filter(instagram_id=instagram_follower['instagram_id'])
            if instagram_users.exists():
                instagram_users.update(**instagram_follower)
                instagram_user = instagram_users[0]
            else:
                instagram_user = InstagramUser.objects.create(**instagram_follower)

            if not current_followers.filter(instagram_user=instagram_user).exists():
                Follower.objects.create(user=self.user, instagram_user=instagram_user)

        return self.success(followers=self.user.get_followers())


class SetApprovedStatusView(AjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            status = json.loads(self.request.PUT['status'])
        except KeyError:
            return self.render_bad_request_response()

        follower = get_object_or_404(Follower, user=self.request.user, pk=kwargs['id'])
        follower.approved = status
        follower.save()
        return self.success()


class SetFollowedStatusView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            status = json.loads(self.request.PUT['status'])
        except KeyError:
            return self.render_bad_request_response()

        self.get_data()
        follower_id = kwargs['id']
        follower = get_object_or_404(Follower, user=self.request.user, pk=follower_id)
        if status:
            self.instagram.follow(follower.instagram_id)
        else:
            self.instagram.unfollow(follower.instagram_id)
        follower.followed = status
        follower.save()
        return self.success()


class BlockView(InstagramAjaxView):
    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        follower_id = kwargs['id']
        follower = get_object_or_404(Follower, user=self.request.user, pk=follower_id)
        self.instagram.block(follower.instagram_id)
        follower.delete()
        return self.success()
