from rest_framework import serializers
import vhcm.models.report as report


class PendingReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = report.Report
        fields = [report.ID, report.TYPE, report.REPORTER, report.REPORTED_INTENT,
                  report.BOT_VERSION, report.CDATE]


class AcceptedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = report.Report
        fields = [report.ID, report.TYPE, report.REPORTER, report.REPORTED_INTENT,
                  report.PROCESSOR, report.FORWARD_INTENT, report.MDATE]


class RejectedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = report.Report
        fields = [report.ID, report.TYPE, report.REPORTER, report.REPORTED_INTENT,
                  report.PROCESSOR, report.BOT_VERSION, report.MDATE]
