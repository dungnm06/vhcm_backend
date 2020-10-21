import vhcm.models.synonym as synonym_model
from rest_framework.decorators import api_view
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.serializers.synonym import SynonymSerializer
from vhcm.common.constants import COMMA


@api_view(['GET', 'POST'])
def get_all_synonyms(request):
    response = Response()
    result = ResponseJSON()
    all_synonyms = synonym_model.Synonym.objects.all()
    serialized_synonyms = SynonymSerializer(all_synonyms, many=True)
    for synonym in serialized_synonyms.data:
        synonym[synonym_model.WORDS] = synonym[synonym_model.WORDS].split(COMMA)

    data = {
        'synonym_dicts': serialized_synonyms.data
    }

    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response
