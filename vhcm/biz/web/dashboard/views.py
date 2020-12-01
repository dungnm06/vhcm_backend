from rest_framework.decorators import api_view
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.common.dao.native_query import execute_native_query
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.biz.web.dashboard.sql import *
from vhcm.common.config.config_manager import config_loader, MAXIMUM_REJECT
from vhcm.biz.nlu.vhcm_chatbot import system_bot_version, CURRENT_BOT_VERSION
import vhcm.models.knowledge_data as knowledge_data
import vhcm.models.knowledge_data_review as review
import vhcm.models.train_data as train_data


@api_view(['GET', 'POST'])
def dashboard_stats(request):
    response = Response()
    result = ResponseJSON()

    user = get_current_user(request)
    user_id = user.user_id
    maximum_reject = config_loader.get_setting_value_int(MAXIMUM_REJECT)

    # Bot version
    version = None
    current_version = system_bot_version[CURRENT_BOT_VERSION]
    if current_version != 0:
        bot_data = train_data.TrainData.objects.filter(id=current_version).first()
        if bot_data:
            version = {
                'id': current_version,
                'name': bot_data.filename,
                'cdate': bot_data.cdate
            }

    # Self-work stats
    intent_stats = execute_native_query(INTENT_STATS.format(user_id=user_id))
    done_intent_count = 0
    process_intent_count = 0
    reject_intent_count = 0
    for intent in intent_stats:
        if intent.status == knowledge_data.PROCESSING:
            process_intent_count += 1
        if intent.status == knowledge_data.DONE:
            done_intent_count += 1
            continue
        if intent.status == knowledge_data.PROCESSING and intent.review_status == review.REJECT and intent.review_count >= maximum_reject:
            reject_intent_count += 1
            continue
    draft_count = execute_native_query(DRAFT_COUNT.format(user_id=user_id))[0].draft_count

    # Global stat: intent done by last 6 months
    intent_done_last_6_months = execute_native_query(INTENT_DONE_BY_MONTH)
    intent_done_last_6_months_display = []
    for month in intent_done_last_6_months:
        intent_done_last_6_months_display.append({
            'time': month.month,
            'total_done': month.intent_done
        })

    # Global stat: number of intent of each process type
    counter = execute_native_query(GLOBAL_INTENT_STATS)
    num_of_intent_type_display = {}
    for count in counter:
        num_of_intent_type_display[count.status] = {
            'type': knowledge_data.PROCESS_STATUS_DICT[count.status],
            'count': count.intent_count
        }
    for type_key in knowledge_data.PROCESS_STATUS_DICT:
        if type_key not in num_of_intent_type_display:
            num_of_intent_type_display[type_key] = {
                'type': knowledge_data.PROCESS_STATUS_DICT[type_key],
                'count': 0
            }

    result.set_status(True)
    result.set_result_data({
        'bot_version': version,
        'done_intent': done_intent_count,
        'process_intent': process_intent_count,
        'reject_intent': reject_intent_count,
        'draft': draft_count,
        'intent_stat_by_month': intent_done_last_6_months_display,
        'global_intent_stat': num_of_intent_type_display
    })
    response.data = result.to_json()
    return response
