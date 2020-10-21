from rest_framework import serializers
from vhcm.models.synonym import Synonym


class SynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Synonym
        fields = ['synonym_id', 'meaning', 'words']
