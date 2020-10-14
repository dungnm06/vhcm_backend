from django.urls import path
from vhcm import views as root_view
from vhcm.biz.web.login import views as login_view


urlpatterns = [
    path('hello', root_view.HelloView.as_view(), name='hello'),
    path('profile', root_view.profile, name='profile'),
    path('auth', login_view.login, name='auth'),
    path('refresh_token', login_view.request_refresh_token, name='refresh_token')
]
