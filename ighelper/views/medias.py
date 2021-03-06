import json

from babel.dates import format_date

from ighelper.exceptions import InstagramMediaNotFoundException
from ighelper.models import Media

from .mixins import InstagramAjaxView, TemplateView


def get_medias(user, media_id=None):
    medias = user.medias.all()
    if media_id is not None:
        medias = medias.filter(id=media_id)
    medias_output = []
    for m in medias:
        media = {
            'noCaption': False,
            'noTags': False,
            'noLocation': False,
        }
        if not m.caption:
            media['noCaption'] = True
            media['noTags'] = True
        elif '#' not in m.caption:
            media['noTags'] = True
        if not m.location_name:
            media['noLocation'] = True
        media.update({
            'image': m.image,
            'imageSmall': m.image_small,
            'content': m.content,
            'id': m.id,
            'likes': m.likes_count,
            'views': m.views_count,
            'caption': m.caption_formatted,
            'location': m.location_formatted,
            'date': format_date(m.date, locale=user.language),
        })
        medias_output.append(media)
    return medias_output


class MediasView(TemplateView):
    template_name = 'medias.html'

    def get_context_data(self):
        medias = get_medias(self.request.user)
        return {'medias': json.dumps(medias)}


class LoadMediasView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        media_ids = self.user.medias.values_list('instagram_id', flat=True)
        medias = self.instagram.get_medias(media_ids)
        self.update_cache()
        for m in medias:
            Media.objects.create(user=self.user, **m)

        return self.success(medias=get_medias(self.user))


class UpdateMediasView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        instagram_medias = self.instagram.get_medias()
        self.update_cache()
        instagram_medias = {m['instagram_id']: m for m in instagram_medias}
        medias = self.user.medias.all()
        for media in medias:
            if media.instagram_id in instagram_medias:
                medias.filter(pk=media.instagram_id).update(**instagram_medias[media.instagram_id])
            else:
                media.delete()
        return self.success(medias=get_medias(self.user))


class MediaView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        media_id = kwargs['id']
        medias = self.user.medias.filter(pk=media_id)
        media = medias[0]
        instagram_media = self.instagram.get_media(media.instagram_id)
        self.update_cache()
        if instagram_media is None:
            media.delete()
            return self.fail()

        medias.update(**instagram_media)
        return self.success(media=get_medias(self.user, media_id)[0])

    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        media_id = kwargs['id']
        media = self.user.medias.get(pk=media_id)
        self.instagram.delete_media(media.instagram_id, media.media_type)
        self.update_cache()
        media.delete()
        return self.success()


class CaptionUpdateView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            caption = self.request.PUT['caption']
        except KeyError:
            return self.render_bad_request_response()

        self.get_data()
        media_id = kwargs['id']
        media = self.user.medias.get(pk=media_id)
        try:
            self.instagram.update_media_caption(media.instagram_id, caption)
            self.update_cache()
        except InstagramMediaNotFoundException:
            media.delete()
            self.update_cache()
            return self.fail()

        media.caption = caption
        media.save()
        return self.success()


class LoadViewsView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        videos = self.user.videos.all()
        for video in videos:
            instagram_media = self.instagram.get_media(video.instagram_id)
            self.update_cache()
            if instagram_media is None:
                video.delete()
                return self.fail()
            video.views_count = instagram_media['views_count']
            video.save()

        return self.success(medias=get_medias(self.user))
