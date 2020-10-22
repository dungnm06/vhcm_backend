import io
import jwt
import vhcm.biz.authentication.jwt.jwt_utils as jwt_utils
import rest_framework.status as status
import vhcm.models.reference_document as document_model
import vhcm.models.user as user_model
import vhcm.common.config.config_manager as config
from django.conf import settings
from rest_framework import exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from vhcm.common.response_json import ResponseJSON
from vhcm.serializers.reference_document import ReferenceDocumentSerializer
from vhcm.common.constants import ACCESS_TOKEN, COMMA
from PIL import Image


@api_view(['GET', 'POST'])
def get_all_document(request):
    response = Response()
    result = ResponseJSON()
    all_document = document_model.RefercenceDocument.objects.all()
    serialized_documents = ReferenceDocumentSerializer(all_document, many=True)

    data = {
        'references': serialized_documents.data
    }

    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get_document(request):
    response = Response()
    result = ResponseJSON()
    try:
        document_id = int(request.data[document_model.ID])
    except Exception:
        raise Exception('Document id is invalid')

    document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
    if not document:
        raise Exception('References document not found')

    serialized_documents = ReferenceDocumentSerializer(document)

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
        response = Response()
        result = ResponseJSON()

        document = document_model.RefercenceDocument()

        if document_model.COVER in request.data and request.data[document_model.COVER]:
            f = request.data[document_model.COVER].read()
            image = Image.open(io.BytesIO(f))
            if image.format not in config.CONFIG_LOADER.get_setting_value_array(config.ACCEPT_IMAGE_FORMAT, COMMA):
                raise Exception('Only accept jpg, png image file format')
            document.cover = f

        if document_model.AUTHOR in request.data and request.data[document_model.AUTHOR]:
            document.author = request.data[document_model.AUTHOR]
        else:
            raise Exception('Missing reference document author')

        if document_model.NAME in request.data and request.data[document_model.NAME]:
            document.reference_name = request.data[document_model.NAME]
        else:
            raise Exception('Missing reference document name')

        if document_model.LINK in request.data and request.data[document_model.LINK]:
            document.link = request.data[document_model.LINK]

        # User
        access_token = request.COOKIES.get(ACCESS_TOKEN)
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Something wrong with access-token')
        user = user_model.User.objects.filter(user_id=int(payload.get(jwt_utils.USER_ID))).first()
        document.create_user = user
        document.last_edit_user = user
        document.save()

        result.set_status(True)
        response.data = result.to_json()
        return response

    def post(self, request, format=None):
        return self.add_new(request)

    def put(self, request, format=None):
        return self.add_new(request)


class EditReferenceDocument(APIView):
    parser_class = (ImageUploadParser,)

    def edit(self, request):
        response = Response()
        result = ResponseJSON()
        try:
            document_id = int(request.data[document_model.ID])
        except Exception:
            raise Exception('Document id is invalid')

        document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
        if not document:
            raise Exception('References document not found')

        if document_model.COVER in request.data and request.data[document_model.COVER]:
            f = request.data[document_model.COVER].read()
            image = Image.open(io.BytesIO(f))
            if image.format not in config.CONFIG_LOADER.get_setting_value_array(config.ACCEPT_IMAGE_FORMAT, COMMA):
                raise Exception('Only accept jpg, png image file format')
            document.cover = f

        if document_model.AUTHOR in request.data and request.data[document_model.AUTHOR]:
            document.author = request.data[document_model.AUTHOR]

        if document_model.NAME in request.data and request.data[document_model.NAME]:
            document.reference_name = request.data[document_model.NAME]

        if document_model.LINK in request.data and request.data[document_model.LINK]:
            document.link = request.data[document_model.LINK]

        # Edit user
        access_token = request.COOKIES.get(ACCESS_TOKEN)
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Something wrong with access-token')

        document.last_edit_user = user_model.User.objects.filter(user_id=int(payload.get(jwt_utils.USER_ID))).first()
        document.save()

        result.set_status(True)
        response.data = result.to_json()
        return response

    def post(self, request, format=None):
        return self.edit(request)

    def put(self, request, format=None):
        return self.edit(request)
