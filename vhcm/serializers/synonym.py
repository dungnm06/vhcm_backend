from rest_framework import serializers
import vhcm.models.synonym as synonym_model


class SynonymSerializer(serializers.ModelSerializer):
    class Meta:
        model = synonym_model.Synonym
        fields = [synonym_model.ID, synonym_model.MEANING, synonym_model.WORDS]
