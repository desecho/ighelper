from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver
from django.utils.translation import LANGUAGE_SESSION_KEY


def activate_user_language_preference(request, lang):
    request.session[LANGUAGE_SESSION_KEY] = lang


class User(AbstractUser):
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    instagram_id = models.CharField(max_length=255, null=True, blank=True)


class Media(models.Model):
    MEDIA_TYPE_IMAGE = 1
    MEDIA_TYPE_VIDEO = 2
    MEDIA_TYPES = (
        (MEDIA_TYPE_IMAGE, 'Image'),
        (MEDIA_TYPE_VIDEO, 'Video'),
    )

    user = models.ForeignKey(User, models.CASCADE, related_name='medias')
    instagram_id = models.CharField(max_length=255)
    date = models.DateTimeField()
    media_type = models.PositiveIntegerField(choices=MEDIA_TYPES)
    text = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    image = models.URLField()
    video = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.instagram_id}'

    @property
    def content(self):
        if self.video:
            return self.video
        return self.image


class Follower(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='followers')
    instagram_id = models.CharField(max_length=255)
    instagram_username = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.URLField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        if self.name:
            return self.name
        return self.instagram_username

    @property
    def profile(self):
        return f'{settings.INSTAGRAM_BASE_URL}/{self.instagram_username}/'


class Like(models.Model):
    media = models.ForeignKey(Media, models.CASCADE, related_name='likes')
    follower = models.ForeignKey(Follower, models.CASCADE, related_name='likes')

    def __str__(self):
        return self.name


@receiver(user_logged_in)
def lang(**kwargs):
    activate_user_language_preference(kwargs['request'], kwargs['user'].language)
