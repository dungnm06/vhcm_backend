from django.urls import path
from vhcm import views as root_view
from vhcm.biz.web.login import login_views
from vhcm.biz.web.logout import logout_views
from vhcm.common.config.config_manager import add_system_settings
from vhcm.biz.web.knowledge_data import knowledge_data_views
from vhcm.biz.web.synonym import synonym_views
from vhcm.biz.web.reference_document import reference_document_views
from vhcm.biz.web.user import user_views


urlpatterns = [
    # Test API
    path('hello', root_view.HelloView.as_view(), name='hello'),
    # For authentication
    path('auth', login_views.login, name='auth'),
    path('logout', logout_views.logout, name='logout'),
    # path('refresh-token', login_views.request_refresh_token, name='refresh_token'),
    # System settings
    path('init-settings', add_system_settings, name='add_base_system_settings'),
    # Knowledge data processing
    path('knowledge-data/extract-sentence', knowledge_data_views.tokenize_sentences, name='tokenize_sentence'),
    path('knowledge-data/add', knowledge_data_views.add, name='add_new_knowledge_data'),
    # User
    path('user/all', user_views.all, name='get_all_users'),
    path('user/get', user_views.get, name='get_user'),
    path('user/edit', user_views.edit, name='edit_user'),
    # Synonym
    path('synonym/all', synonym_views.get_all_synonyms, name='get_all_synonyms'),
    path('synonym/get', synonym_views.get, name='get_one_synonym'),
    path('synonym/add', synonym_views.add, name='add_synonym'),
    path('synonym/edit', synonym_views.edit, name='edit_synonym'),
    path('synonym/validate-delete', synonym_views.validate_delete, name='validate_synonym_before_delete'),
    path('synonym/delete', synonym_views.delete, name='delete_synonym'),
    # Reference document
    path('reference-document/all', reference_document_views.get_all_document, name='get_all_references'),
    path('reference-document/get', reference_document_views.get_document, name='get_reference'),
    path('reference-document/add', reference_document_views.AddNewReferenceDocument.as_view(), name='add-new-reference'),
    path('reference-document/edit', reference_document_views.EditReferenceDocument.as_view(), name='edit-reference'),
]

from django.conf.urls import handler404
from vhcm.views import error404
handler404 = error404
