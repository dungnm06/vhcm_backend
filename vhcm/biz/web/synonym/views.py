import vhcm.models.synonym as synonym_model
import vhcm.models.knowledge_data as knowledge_data_model
from rest_framework.decorators import api_view
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.serializers.synonym import SynonymSerializer
from vhcm.common.constants import COMMA, SPACE


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


@api_view(['GET', 'POST'])
def get(request):
    response = Response()
    result = ResponseJSON()

    try:
        synonym_id = int(request.data['id']) if request.method == 'POST' else int(request.GET['id'])
        synonym = synonym_model.Synonym.objects.filter(synonym_id=synonym_id).first()
        if synonym is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid synonym set ids: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing synonym set id')

    serialized_synonyms = SynonymSerializer(synonym).data
    words = serialized_synonyms['words']
    words = [w for w in words.split(COMMA)]
    serialized_synonyms['words'] = words

    result.set_status(True)
    result.set_result_data(serialized_synonyms)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def add(request):
    response = Response()
    result = ResponseJSON()

    errors = validate(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    synonym = synonym_model.Synonym()
    synonym.meaning = request.data.get('meaning').strip()
    synonym.words = COMMA.join([w.strip() for w in request.data.get('words')])
    synonym.ne_synonym = request.data.get('ne_synonym', False)
    synonym.save()

    serilized_synonym = SynonymSerializer(synonym).data
    words = serilized_synonym['words']
    words = [w for w in words.split(COMMA)]
    serilized_synonym['words'] = words

    result.set_status(True)
    result.set_result_data(serilized_synonym)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def edit(request):
    response = Response()
    result = ResponseJSON()

    errors = validate(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    try:
        synonym_id = int(request.data['id'])
        synonym = synonym_model.Synonym.objects.filter(synonym_id=synonym_id).first()
        if synonym is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid synonym set ids: {}'.format(request.data['id']))
    except KeyError:
        raise Exception('Missing synonym set id')

    synonym.meaning = request.data.get('meaning').strip()
    synonym.words = COMMA.join([w.strip() for w in request.data.get('words')])
    synonym.ne_synonym = request.data.get('ne_synonym', False)
    synonym.save()

    serilized_synonym = SynonymSerializer(synonym).data
    words = serilized_synonym['words']
    words = [w for w in words.split(COMMA)]
    serilized_synonym['words'] = words

    result.set_status(True)
    result.set_result_data(serilized_synonym)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def delete(request):
    response = Response()
    result = ResponseJSON()

    try:
        synonym_id = int(request.data['id']) if request.method == 'POST' else int(request.GET['id'])
        synonym = synonym_model.Synonym.objects.filter(synonym_id=synonym_id).first()
        if synonym is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid synonym set ids: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing synonym set id')

    knowledge_datas = knowledge_data_model.KnowledgeData.objects.filter(synonym=synonym)
    kd_nums = len(knowledge_datas)
    if kd_nums > 0:
        result.set_status(False)
        kds = knowledge_datas[:] if len(knowledge_datas) <= 3 else knowledge_datas[:3]
        kd_names = (COMMA+SPACE).join([k.intent for k in kds])
        if kd_nums > 3:
            kd_names += '...'
        result.set_messages('Synonym set "{}" is being used in {} Knowledge Data: {}.\nNeed to edit knowledge data first!'.format(
            synonym.meaning,
            kd_nums,
            kd_names
        ))
        response.data = result.to_json()
        return response

    synonym.delete()

    result.set_status(True)
    response.data = result.to_json()
    return response


def validate(request):
    errors = []
    # Meaning
    if not ('meaning' in request.data and request.data.get('meaning').strip()):
        errors.append('Missing synonym meaning')

    # Words
    if not ('words' in request.data and isinstance(request.data.get('words'), list)):
        errors.append('Form data is malformed')
    elif len(request.data.get('words')) < 1:
        errors.append('Synonym set must contains atleast 1 word')

    return errors
