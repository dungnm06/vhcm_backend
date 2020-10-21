import base64
import rest_framework.status as status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from vhcm.common.response_json import ResponseJSON
import vhcm.models.reference_document as docuemnt_model
from vhcm.serializers.reference_document import ReferenceDocumentSerializer


@api_view(['GET', 'POST'])
def get_all_document(request):
    response = Response()
    result = ResponseJSON()
    all_document = docuemnt_model.RefercenceDocument.objects.all()
    serialized_documents = ReferenceDocumentSerializer(all_document, many=True)

    data = {
        'references': serialized_documents.data
    }

    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


class AddNewReferenceDocument(APIView):
    parser_class = (ImageUploadParser,)

    def add_new(self, request):

        try:
            document_id = int(request.data['document_id'])
        except ValueError:
            raise Exception('Document id is invalid')

        document = docuemnt_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
        if not document:
            raise Exception('References document not found')

        if 'file' in request.data:
            f = request.data['file']
            document.cover = f.read()

        document.save()

        # mymodel.my_file_field.save(f.name, f, save=True)
        return Response(status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        return self.add_new(request)

    def put(self, request, format=None):
        return self.add_new(request)
