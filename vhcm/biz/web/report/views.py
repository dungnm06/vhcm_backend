from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.db.models import Q
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import DATETIME_DDMMYYYY, DATETIME_DDMMYYYY_HHMMSS
from vhcm.common.dao.native_query import execute_native_query
from vhcm.common.utils.CH import isInt
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.biz.web.report.sql import *
from vhcm.common.utils.CV import utc_to_gmt7
import vhcm.models.report as report_model
import vhcm.models.knowledge_data as knowledge_data_model
import vhcm.models.knowledge_data_comment as comment_model
import vhcm.models.knowledge_data_comment_report as report_comment_model


@api_view(['GET', 'POST'])
def all_pending_report(request):
    response = Response()
    result = ResponseJSON()

    pending_reports = execute_native_query(ALL_PENDING_REPORT)
    reports_display = []
    for report in pending_reports:
        reports_display.append({
            'report_id': report.report_id,
            'report_type': report.report_type,
            'reporter_id': report.reporter_id,
            'reporter': report.reporter,
            'report_data': report.report_data,
            'reported_intent': report.reported_intent,
            'bot_version': utc_to_gmt7(report.bot_version).strftime(DATETIME_DDMMYYYY.regex),
            'cdate': utc_to_gmt7(report.cdate).strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        })

    result.set_status(True)
    result.set_result_data(reports_display)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def all_accepted_report(request):
    response = Response()
    result = ResponseJSON()

    pending_reports = execute_native_query(ALL_ACCEPTED_REPORT)
    reports_display = []
    for report in pending_reports:
        reports_display.append({
            'report_id': report.report_id,
            'report_type': report.report_type,
            'reporter_id': report.reporter_id,
            'reporter': report.reporter,
            'report_data': report.report_data,
            'reported_intent': report.reported_intent,
            'processor_id': report.processor_id,
            'processor': report.processor,
            'forward_intent': report.forward_intent,
            'mdate': utc_to_gmt7(report.mdate).strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        })

    result.set_status(True)
    result.set_result_data(reports_display)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def all_rejected_report(request):
    response = Response()
    result = ResponseJSON()

    pending_reports = execute_native_query(ALL_REJECTED_REPORT)
    reports_display = []
    for report in pending_reports:
        reports_display.append({
            'report_id': report.report_id,
            'report_type': report.report_type,
            'reporter_id': report.reporter_id,
            'reporter': report.reporter,
            'report_data': report.report_data,
            'reported_intent': report.reported_intent,
            'processor_id': report.processor_id,
            'processor': report.processor,
            'reject_reason': report.reason,
            'mdate': utc_to_gmt7(report.mdate).strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        })

    result.set_status(True)
    result.set_result_data(reports_display)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get_pending_report(request):
    response = Response()
    result = ResponseJSON()

    user = get_current_user(request)

    report_id = request.data.get(report_model.ID) if request.method == 'POST' else request.GET.get(report_model.ID)
    if not report_id or not isInt(report_id):
        raise APIException('Invalid report id')

    report = report_model.Report.objects.filter(id=report_id, status=report_model.PENDING) \
        .select_related('reporter', 'bot_version') \
        .first()
    if not report:
        raise APIException('Invalid report id, report not found')

    available_knowledge_datas = knowledge_data_model.KnowledgeData.objects \
        .filter(Q(status=knowledge_data_model.AVAILABLE)
                | Q(status__in=[knowledge_data_model.PROCESSING, knowledge_data_model.DONE], edit_user=user))

    other_knowledge_datas = knowledge_data_model.KnowledgeData.objects \
        .select_related('edit_user') \
        .filter(status__in=[knowledge_data_model.PROCESSING, knowledge_data_model.DONE]) \
        .exclude(edit_user=user)

    kds = []
    for kd in available_knowledge_datas:
        kds.append({
            'id': kd.knowledge_data_id,
            'intent': kd.intent,
            'intent_fullname': kd.intent_fullname
        })

    okds = []
    for kd in other_knowledge_datas:
        okds.append({
            'id': kd.knowledge_data_id,
            'intent': kd.intent,
            'intent_fullname': kd.intent_fullname,
            'edit_user_id': kd.edit_user.user_id,
            'edit_username': kd.edit_user.username
        })

    result_data = {
        'id': report.id,
        'report_type': report.type,
        'reporter_id': report.reporter.user_id,
        'reporter': report.reporter.username,
        'reporter_note': report.reporter_note,
        'reported_intent': report.reported_intent,
        'report_data': report.report_data,
        'question': report.question,
        'bot_answer': report.bot_answer,
        'bot_version_id': report.bot_version.id,
        'bot_version_date': report.bot_version.cdate.strftime(DATETIME_DDMMYYYY.regex),
        'cdate': report.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
        'available_knowledge_data': kds,
        'other_knowledge_data': okds
    }

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get_accepted_report(request):
    response = Response()
    result = ResponseJSON()

    report_id = request.data.get(report_model.ID) if request.method == 'POST' else request.GET.get(report_model.ID)
    if not report_id or not isInt(report_id):
        raise APIException('Invalid report id')

    report = report_model.Report.objects.filter(id=report_id, status=report_model.PROCESSED) \
        .select_related('reporter', 'processor', 'bot_version', 'forward_intent') \
        .first()
    if not report:
        raise APIException('Invalid report id, report not found')

    result_data = {
        'id': report.id,
        'report_type': report.type,
        'reporter_id': report.reporter.user_id,
        'reporter': report.reporter.username,
        'reporter_note': report.reporter_note,
        'reported_intent': report.reported_intent,
        'report_data': report.report_data,
        'question': report.question,
        'bot_answer': report.bot_answer,
        'bot_version_id': report.bot_version.id,
        'bot_version_date': report.bot_version.cdate.strftime(DATETIME_DDMMYYYY.regex),
        'processor_id': report.processor.user_id,
        'processor': report.processor.username,
        'processor_note': report.processor_note,
        'forward_intent_name': report.forward_intent.intent if report.forward_intent else None,
        'mdate': report.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
    }

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get_rejected_report(request):
    response = Response()
    result = ResponseJSON()

    report_id = request.data.get(report_model.ID) if request.method == 'POST' else request.GET.get(report_model.ID)
    if not report_id or not isInt(report_id):
        raise APIException('Invalid report id')

    report = report_model.Report.objects.filter(id=report_id, status=report_model.REJECTED) \
        .select_related('reporter', 'processor', 'bot_version') \
        .first()
    if not report:
        raise APIException('Invalid report id, report not found')

    result_data = {
        'id': report.id,
        'report_type': report.type,
        'reporter_id': report.reporter.user_id,
        'reporter': report.reporter.username,
        'reporter_note': report.reporter_note,
        'reported_intent': report.reported_intent,
        'report_data': report.report_data,
        'question': report.question,
        'bot_answer': report.bot_answer,
        'bot_version_id': report.bot_version.id,
        'bot_version_date': report.bot_version.cdate.strftime(DATETIME_DDMMYYYY.regex),
        'processor_id': report.processor.user_id,
        'processor': report.processor.username,
        'processor_note': report.processor_note,
        'mdate': report.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
    }

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def reject_report(request):
    response = Response()
    result = ResponseJSON()

    user = get_current_user(request)

    report_id = request.data.get(report_model.ID) if request.method == 'POST' else request.GET.get(report_model.ID)
    if not report_id or not isInt(report_id):
        raise APIException('Invalid report id')

    reject_reason = request.data.get(report_model.PROCESSOR_NOTE)
    if not reject_reason or not isinstance(reject_reason, str):
        raise APIException('Processor must fill reject reason')

    report = report_model.Report.objects.filter(id=report_id, status=report_model.PENDING).first()
    if not report:
        raise APIException('Invalid report id, report not found')

    report.status = report_model.REJECTED
    report.processor_note = reject_reason
    report.processor = user
    report.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def report_to_contributor(request):
    response = Response()
    result = ResponseJSON()

    user = get_current_user(request)

    # Get existing Knowledge data
    kd_id = request.data.get(knowledge_data_model.ID)
    if not (kd_id and isInt(kd_id)):
        raise APIException('Invalid intent id: ID({})'.format(kd_id))

    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=kd_id).select_related('edit_user').first()
    if knowledge_data is None:
        raise APIException('Intent id not found: ID({})'.format(kd_id))

    report_process = request.data.get('report_processing')
    if not report_process:
        raise APIException('Report process data is invalid')

    report_id = report_process.get(report_model.ID)
    if not (report_id and isInt(report_id)):
        raise APIException('Report id is invalid')

    processor_note = report_process.get(report_model.PROCESSOR_NOTE)
    if not processor_note or not isinstance(processor_note, str):
        raise APIException('Report processor must leave a comment')

    report = report_model.Report.objects.filter(id=report_id, status=report_model.PENDING).first()
    if not report:
        raise APIException('Report id is invalid')

    comment = comment_model.Comment(
        user=user,
        knowledge_data=knowledge_data,
        comment=processor_note,
        able_to_delete=False,
        status=comment_model.VIEWABLE
    )
    comment.save()
    report_comment = report_comment_model.ReportComment(
        report_to=knowledge_data.edit_user,
        report=report,
        comment=comment
    )
    report_comment.save()

    result.set_status(True)
    response.data = result.to_json()
    return response
