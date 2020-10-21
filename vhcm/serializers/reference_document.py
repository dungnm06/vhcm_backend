from rest_framework import serializers
from vhcm.models.reference_document import RefercenceDocument


class ReferenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefercenceDocument
        fields = ['reference_document_id', 'create_user_id', 'last_edit_user_id',
                  'reference_name', 'link', 'cover', 'author', 'cdate', 'mdate']
