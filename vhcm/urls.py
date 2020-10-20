from django.urls import path
from vhcm import views as root_view
from vhcm.biz.web.login import views as login_view
from vhcm.common.config.config_manager import add_system_settings


urlpatterns = [
    # Test API
    path('hello', root_view.HelloView.as_view(), name='hello'),
    # For authentication
    path('auth', login_view.login, name='auth'),
    path('refresh_token', login_view.request_refresh_token, name='refresh_token'),
    # System settings
    path('init_settings', add_system_settings, name='add_base_system_settings')
]
