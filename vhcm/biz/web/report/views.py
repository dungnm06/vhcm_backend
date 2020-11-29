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
import vhcm.models.report as report_model
import vhcm.models.knowledge_data as knowledge_data_model


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
            'bot_version': report.bot_version.strftime(DATETIME_DDMMYYYY.regex),
            'cdate': report.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
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
            'mdate': report.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
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
            'mdate': report.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
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

    report = report_model.Report.objects.filter(id=report_id, status=report_model.PENDING)\
        .select_related('reporter', 'bot_version')\
        .first()
    if not report:
        raise APIException('Invalid report id, report not found')

    available_knowledge_datas = knowledge_data_model.KnowledgeData.objects\
        .filter(Q(status=knowledge_data_model.AVAILABLE)
                | Q(status__in=[knowledge_data_model.PROCESSING, knowledge_data_model.DONE], edit_user=user))

    kds = []
    for kd in available_knowledge_datas:
        kds.append({
            'id': kd.knowledge_data_id,
            'intent': kd.intent,
            'intent_fullname': kd.intent_fullname
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
        'available_knowledge_data': kds
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

    report = report_model.Report.objects.filter(id=report_id, status=report_model.ACCEPTED)\
        .select_related('reporter', 'processor', 'bot_version', 'forward_intent')\
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
        'forward_intent_id': report.forward_intent.knowledge_data_id,
        'forward_intent_name': report.forward_intent.intent_fullname,
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

    report = report_model.Report.objects.filter(id=report_id, status=report_model.REJECTED)\
        .select_related('reporter', 'processor', 'bot_version', 'forward_intent')\
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
