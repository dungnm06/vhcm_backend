from rest_framework.decorators import api_view
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.biz.nlu.language_processing import language_processor


@api_view(['POST'])
def tokenize_sentences(request):
    response = Response()
    result = ResponseJSON()

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
def get_synonym_dicts(request):
    pass
