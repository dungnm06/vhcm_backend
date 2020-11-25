from rest_framework.decorators import api_view
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import DATETIME_DDMMYYYY, DATETIME_DDMMYYYY_HHMMSS
from vhcm.common.dao.native_query import execute_native_query
from vhcm.biz.web.report.sql import *
import vhcm.models.report as report_model


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
            'reporter': report.reporter,
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
            'reporter': report.reporter,
            'reported_intent': report.reported_intent,
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
            'reporter': report.reporter,
            'reported_intent': report.reported_intent,
            'processor': report.processor,
            'forward_intent': report.forward_intent,
            'mdate': report.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        })

    result.set_status(True)
    result.set_result_data(reports_display)
    response.data = result.to_json()
    return response
