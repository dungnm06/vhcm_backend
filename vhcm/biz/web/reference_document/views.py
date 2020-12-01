from rest_framework.exceptions import APIException
import vhcm.models.reference_document as document_model
import vhcm.models.knowledge_data as knowledge_data_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from vhcm.common.response_json import ResponseJSON
from vhcm.serializers.reference_document import ReferenceDocumentSerializer
from vhcm.common.utils.CV import ImageUploadParser, extract_validation_messages
from vhcm.biz.authentication.user_session import get_current_user
from .forms import DocumentAddForm, DocumentEditForm
from vhcm.common.constants import COMMA, SPACE


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
        document_id = int(request.data[document_model.ID]) if request.method == 'POST' else int(request.GET[document_model.ID])
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


class AddNewReferenceDocument(APIView):
    parser_class = (ImageUploadParser,)

    def add_new(self, request):
        response = Response()
        result = ResponseJSON()
        user = get_current_user(request)

        form = DocumentAddForm(request.data, request.FILES)
        if form.is_valid():
            document = document_model.RefercenceDocument()
            datas = form.instance
            document.reference_name = datas.reference_name
            document.link = datas.link
            document.author = datas.author
            if form.data.get(document_model.COVER):
                document.cover = datas.cover

            document.create_user = user
            document.last_edit_user = user

            document.save()
            serialized_document = ReferenceDocumentSerializer(document)
            result.set_result_data(serialized_document.data)
        else:
            result.set_status(False)
            result.set_messages(extract_validation_messages(form, document_model.FIELDS))
            response.data = result.to_json()
            return response

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
            raise APIException('Document id is invalid')

        document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
        if not document:
            raise Exception('References document not found')

        result.set_status(True)
        form = DocumentEditForm(request.data, request.FILES, instance=document)
        if form.is_valid():
            datas = form.instance
            document.reference_name = datas.reference_name
            document.link = datas.link
            document.author = datas.author
            if form.data.get(document_model.COVER):
                document.cover = datas.cover

            user = get_current_user(request)
            document.last_edit_user = user

            document.save()
            serialized_document = ReferenceDocumentSerializer(document)
            result.set_result_data(serialized_document.data)
        else:
            result.set_status(False)
            result.set_messages(extract_validation_messages(form, document_model.FIELDS))
            response.data = result.to_json()
            return response

        response.data = result.to_json()
        return response

    def post(self, request, format=None):
        return self.edit(request)

    def put(self, request, format=None):
        return self.edit(request)


@api_view(['GET', 'POST'])
def delete(request):
    response = Response()
    result = ResponseJSON()

    try:
        id = int(request.data[document_model.ID]) if request.method == 'POST' else int(request.GET[document_model.ID])
        document = document_model.RefercenceDocument.objects.filter(reference_document_id=id).first()
        if document is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid reference document id: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing reference document id')

    knowledge_datas = knowledge_data_model.KnowledgeData.objects.filter(references__reference_document_id=id)
    kd_nums = len(knowledge_datas)
    if kd_nums > 0:
        result.set_status(False)
        kds = knowledge_datas[:] if len(knowledge_datas) <= 3 else knowledge_datas[:3]
        kd_names = (COMMA+SPACE).join([k.intent for k in kds])
        if kd_nums > 3:
            kd_names += '...'
        result.set_messages('Reference document "{}" is being linked with {} Knowledge Data: {}.\nNeed to edit knowledge data first!'.format(
            document.reference_name,
            kd_nums,
            kd_names
        ))
        response.data = result.to_json()
        return response

    document.delete()

    result.set_status(True)
    response.data = result.to_json()
    return response
