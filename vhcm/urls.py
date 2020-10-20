from django.urls import path
from vhcm import views as root_view
from vhcm.biz.web.login import login_views as login_view
from vhcm.common.config.config_manager import add_system_settings
from vhcm.biz.web.knowledge_data import knowledge_data_views as knowledge_data_views


urlpatterns = [
    # Test API
    path('hello', root_view.HelloView.as_view(), name='hello'),
    # For authentication
    path('auth', login_view.login, name='auth'),
    path('refresh-token', login_view.request_refresh_token, name='refresh_token'),
    # System settings
    path('init-settings', add_system_settings, name='add_base_system_settings'),
    # Knowledge data processing
    path('knowledge-data/extract-sentence', knowledge_data_views.tokenize_sentences, name='add_base_system_settings')
]
