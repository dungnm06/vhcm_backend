from collections import Counter
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.biz.nlu.language_processing import language_processor
import vhcm.models.synonym as synonym_model
from vhcm.biz.nlu.model.synonym import SynonymSet
from vhcm.common.constants import COMMA, SPACE


@api_view(['POST'])
def tokenize_sentences(request):
    response = Response()
    result = ResponseJSON()

    if not ('paragraph' in request.data and request.data.get('paragraph')):
        sentence = ''
    else:
        sentence = request.data['paragraph']
    # Named entity extract
    ner = language_processor.named_entity_reconize(sentence)
    # POS tagging
    pos_tag = language_processor.pos_tagging(sentence)
    pos_tag_tmp = []
    for pos in pos_tag:
        words = []
        for word in pos:
            words.append({
                "type": word[1],
                "value": word[0]
            })
        pos_tag_tmp.append(words)

    data = {
        'ner': ner,
        'pos': pos_tag_tmp
    }
    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def untokenize_sentences(request):
    response = Response()
    result = ResponseJSON()
    result_data = {
        'sentences': []
    }

    if not ('sentences' in request.data and request.data.get('sentences')):
        sentence = []
    else:
        sentence = request.data['sentences']

    result_data['sentences'].extend(language_processor.words_unsegmentation(sentence))

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def generate_similaries(request):
    response = Response()
    result = ResponseJSON()
    result_data = {
        'similaries': []
    }

    if not ('sentences' in request.data and request.data.get('sentences')):
        result.set_status(True)
        result.set_result_data(result_data)
        response.data = result.to_json()
        return response

    try:
        sentences = request.data.get('sentences')
        all_synonym_ids = []
        for data in sentences:
            all_synonym_ids.extend(data['synonyms'])
        all_synonym_ids = list(Counter(all_synonym_ids))
        synonyms = synonym_model.Synonym.objects.filter(synonym_id__in=all_synonym_ids)
        check_ids = [s.synonym_id for s in synonyms]
        error_ids = []
        for sid in all_synonym_ids:
            if sid not in check_ids:
                error_ids.append(str(sid))
        if error_ids:
            raise ValueError(COMMA.join(error_ids))

        synonym_set_dicts = {}
        for synonym in synonyms:
            synonym_set_dicts[synonym.synonym_id] = SynonymSet(synonym)

        for data in sentences:
            sentence = data['sentence']
            synonym_ids = data['synonyms']

            result_data['similaries'].append(
                language_processor.generate_similary_sentences(
                                    (sentence.split(SPACE), {k: synonym_set_dicts[k] for k in synonym_ids}),
                                    word_segemented=True
                ))

    except KeyError:
        raise APIException('Data structure error.')
    except ValueError as ex:
        raise APIException('Invalid synonym ID. ' + str(ex))

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response
