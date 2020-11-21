from django.urls import path
import vhcm.views as root_view
import vhcm.biz.web.login.views as login_views
import vhcm.biz.web.logout.views as logout_views
from vhcm.common.config.config_manager import add_system_settings
import vhcm.biz.web.setting.views as setting_views
import vhcm.biz.web.nlp.views as nlp_views
import vhcm.biz.web.knowledge_data.views as knowledge_data_views
import vhcm.biz.web.synonym.views as synonym_views
import vhcm.biz.web.reference_document.views as reference_document_views
import vhcm.biz.web.user.views as user_views
import vhcm.biz.web.train_data.views as train_data_views
import vhcm.biz.web.chat_history.views as chat_history_views


urlpatterns = [
    # Test API
    path('hello', root_view.HelloView.as_view(), name='hello'),
    # For authentication
    path('auth', login_views.login, name='auth'),
    path('logout', logout_views.logout, name='logout'),
    # path('refresh-token', login_views.request_refresh_token, name='refresh_token'),
    # System settings
    path('setting/init', add_system_settings, name='add_base_system_settings'),
    path('setting/all', setting_views.all, name='get_all_system_settings'),
    path('setting/update', setting_views.update, name='update_system_settings'),
    # NLP
    path('nlp/tokenize', nlp_views.tokenize_sentences, name='tokenize_sentence'),
    path('nlp/untokenize', nlp_views.untokenize_sentences, name='tokenize_sentence'),
    path('nlp/generate-similaries', nlp_views.generate_similaries, name='generate_similary_sentences'),
    # Knowledge data processing
    path('knowledge-data/all', knowledge_data_views.all, name='get_list_knowledge_data'),
    path('knowledge-data/all-trainable', knowledge_data_views.all_trainable, name='get_list_trainable_knowledge_data'),
    path('knowledge-data/get', knowledge_data_views.get, name='get_knowledge_data'),
    path('knowledge-data/add', knowledge_data_views.add, name='add_new_knowledge_data'),
    path('knowledge-data/edit', knowledge_data_views.edit, name='edit_knowledge_data'),
    # Knowledge data / Comment
    path('knowledge-data/all-comment', knowledge_data_views.all_comment, name='all_comments'),
    path('knowledge-data/post-comment', knowledge_data_views.post_comment, name='post_comment'),
    path('knowledge-data/edit-comment', knowledge_data_views.edit_comment, name='edit_comment'),
    path('knowledge-data/delete-comment', knowledge_data_views.delete_comment, name='delete_comment'),
    # Knowledge data / Review
    path('knowledge-data/all-reviews', knowledge_data_views.all_reviews, name='all_reviews'),
    path('knowledge-data/review', knowledge_data_views.review_data, name='review'),
    # User
    path('user/all', user_views.all, name='get_all_users'),
    path('user/get', user_views.get, name='get_user'),
    path('user/add', user_views.AddUser.as_view(), name='add_user'),
    path('user/edit', user_views.EditUser.as_view(), name='edit_user'),
    path('user/change-status', user_views.change_status, name='change_user_status'),
    path('user/update-password-first-login', user_views.update_password_first_login, name='first_time_login_update_password'),
    # Synonym
    path('synonym/all', synonym_views.get_all_synonyms, name='get_all_synonyms'),
    path('synonym/get', synonym_views.get, name='get_one_synonym'),
    path('synonym/add', synonym_views.add, name='add_synonym'),
    path('synonym/edit', synonym_views.edit, name='edit_synonym'),
    path('synonym/delete', synonym_views.delete, name='delete_synonym'),
    # Reference document
    path('reference-document/all', reference_document_views.get_all_document, name='get_all_references'),
    path('reference-document/get', reference_document_views.get_document, name='get_reference'),
    path('reference-document/add', reference_document_views.AddNewReferenceDocument.as_view(), name='add-new-reference'),
    path('reference-document/edit', reference_document_views.EditReferenceDocument.as_view(), name='edit-reference'),
    path('reference-document/delete', reference_document_views.delete, name='delete_document'),
    # Train data processing
    path('train-data/all', train_data_views.all, name='get available training data'),
    path('train-data/all-trainable', train_data_views.all_trainable, name='get trainable data'),
    path('train-data/all-deleted', train_data_views.all_deleted, name='get deleted training data'),
    path('train-data/toggle', train_data_views.on_off_data, name='toggle data trainable status'),
    path('train-data/add', train_data_views.add, name='create training data'),
    path('train-data/change-description', train_data_views.update_description, name='update training data description'),
    path('train-data/delete', train_data_views.delete, name='delete training data'),
    path('train-data/download', train_data_views.download, name='download training data'),
    # Chat history
    path('chat-history/all', chat_history_views.all, name='view all logged chat session'),
    path('chat-history/get', chat_history_views.get, name='get chat log details'),
    # Classifier training service
    # path('trainer/is-running', trainer_views.is_process_running, name='check_trainning_process'),
]
