import vhcm.models.reference_document as docuemnt_model
from rest_framework.decorators import api_view
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.serializers.reference_document import ReferenceDocumentSerializer
import base64


@api_view(['GET', 'POST'])
def get_all_document(request):
    response = Response()
    result = ResponseJSON()
    all_document = docuemnt_model.RefercenceDocument.objects.all()
    serialized_documents = ReferenceDocumentSerializer(all_document, many=True)
    # Convert to client readable data
    for document in serialized_documents.data:
        if document[docuemnt_model.COVER]:
            document[docuemnt_model.COVER] = base64.b64encode(document[docuemnt_model.COVER]).decode()

    data = {
        'references': serialized_documents.data
    }

    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


