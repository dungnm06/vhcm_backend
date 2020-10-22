from rest_framework import serializers
import vhcm.models.reference_document as rd_model


class ReferenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = rd_model.RefercenceDocument
        fields = [rd_model.ID, rd_model.CREATE_USER, rd_model.LAST_EDIT_USER,
                  rd_model.NAME, rd_model.LINK, rd_model.COVER, rd_model.AUTHOR,
                  rd_model.CDATE, rd_model.MDATE]
