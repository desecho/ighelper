"""URL Configuration."""
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from ighelper.views.ighelper import (
    FollowersView,
    HomeView,
    LoadFollowersView,
    LoadMediasView,
)
from ighelper.views.user import (
    PreferencesView,
    SavePreferencesView,
    logout_view,
)

admin.autodiscover()

urlpatterns = []

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += [
    # User
    path('login/', login, {'template_name': 'user/login.html'}, name='login'),
    path('logout/', logout_view, name='logout'),

    # Preferences
    path('preferences/', PreferencesView.as_view(), name='preferences'),
    path('save-preferences/', SavePreferencesView.as_view(), name='save_preferences'),

    # Services
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=('ighelper', ), domain='djangojs'), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('rosetta/', include('rosetta.urls')),
    # -------------------------------------------------------------------------------------------
    path('', HomeView.as_view(), name='home'),
    path('followers/', FollowersView.as_view(), name='followers'),
    path('followers/load/', LoadFollowersView.as_view(), name='load_followers'),
    path('load-medias/', LoadMediasView.as_view(), name='load_medias'),
]
