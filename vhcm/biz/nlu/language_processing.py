import os
import re
from vncorenlp import VnCoreNLP
import vhcm.common.config.config_manager as config
from vhcm.common.constants import *
from vhcm.common.utils.CV import to_abs_path
from vhcm.common.utils.files import load_text_data
from vhcm.common.singleton import Singleton
from itertools import product
from vhcm.biz.nlu.model import intent as intent_model


def loaddicchar():
    dic = {}
    char1252 = 'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'.split(
        '|')
    charutf8 = "à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ".split(
        '|')
    for idx in range(len(char1252)):
        dic[char1252[idx]] = charutf8[idx]
    return dic


dicchar = loaddicchar()

bang_nguyen_am = [['a', 'à', 'á', 'ả', 'ã', 'ạ', 'a'],
                  ['ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ', 'aw'],
                  ['â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ', 'aa'],
                  ['e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ', 'e'],
                  ['ê', 'ề', 'ế', 'ể', 'ễ', 'ệ', 'ee'],
                  ['i', 'ì', 'í', 'ỉ', 'ĩ', 'ị', 'i'],
                  ['o', 'ò', 'ó', 'ỏ', 'õ', 'ọ', 'o'],
                  ['ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ', 'oo'],
                  ['ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ', 'ow'],
                  ['u', 'ù', 'ú', 'ủ', 'ũ', 'ụ', 'u'],
                  ['ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự', 'uw'],
                  ['y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ', 'y']]
bang_ky_tu_dau = ['', 'f', 's', 'r', 'x', 'j']
nguyen_am_to_ids = {}
for i in range(len(bang_nguyen_am)):
    for i2 in range(len(bang_nguyen_am[i]) - 1):
        nguyen_am_to_ids[bang_nguyen_am[i][i2]] = (i, i2)


class LanguageProcessor(object, metaclass=Singleton):
    def __init__(self):
        # Variables for language understanding tasks
        self.config = config.config_loader
        self.rdrsegmenter = VnCoreNLP(
            os.path.join(PROJECT_ROOT, to_abs_path(self.config.get_setting_value(config.VNCORENLP)))
        )
        self.ner_types = self.config.get_setting_value_array(config.NAMED_ENTITY_TYPES, COMMA)
        self.critical_data_ng_patterns = self.config.get_setting_value_array(config.CRITICAL_DATA_NG_PATTERNS, COMMA)
        self.exclude_pos_tag = self.config.get_setting_value_array(config.EXCLUDE_POS_TAG, COMMA)
        self.exclude_words = self.config.get_setting_value_array(config.EXCLUDE_WORDS, COMMA)

        stopwords_path = os.path.join(PROJECT_ROOT, to_abs_path(self.config.get_setting_value(config.STOPWORDS)))
        self.stopwords = set(load_text_data(stopwords_path))

    def word_segmentation_no_join(self, text):
        return self.rdrsegmenter.tokenize(text)

    def batch_word_segmentation(self, texts):
        segmented_text = []
        if type(texts) is list:
            for text in texts:
                segmented_text.extend(self.word_segmentation(text))
        elif type(texts) is str:
            segmented_text.extend(self.word_segmentation(texts))
        else:
            raise Exception("Invaild input type, only str or list of string")

        return segmented_text

    def word_segmentation(self, text):
        word_segmented_text = self.rdrsegmenter.tokenize(text)
        return SPACE.join([SPACE.join(sentence) for sentence in word_segmented_text])

    def words_unsegmentation(self, sentence):
        if type(sentence) is str:
            return SPACE.join([s.strip().replace(UNDERSCORE, SPACE) for s in sentence.split(SPACE)])
        elif type(sentence) is list:
            return [SPACE.join([s2.strip().replace(UNDERSCORE, SPACE) for s2 in s1.split(SPACE)]) for s1 in sentence]
        else:
            raise Exception("Invaild input type, only str or list of string")

    def pos_tagging(self, sentence):
        return self.rdrsegmenter.pos_tag(sentence)

    def named_entity_reconize(self, sentence):
        ners = self.rdrsegmenter.ner(sentence)
        # Collect named entity words to list
        # Using BIO rule: B: begin, I: inside, O: outside
        named_entities_list = []
        tmp_word = ''
        current_type = ''
        idx = 0
        for ner in ners:
            tmp_list = []
            for widx, o in enumerate(ner):
                word, tag = o
                if tag != 'O':
                    pos, typ = tag.split('-')
                    # Not supporting type
                    if typ not in self.ner_types:
                        continue
                    # Begin of entity
                    if pos == 'B' and not current_type:
                        idx = widx
                        tmp_word += word + ' '
                        current_type = typ
                    # Inside of entity
                    elif pos == 'I' and current_type == typ:
                        tmp_word += word + ' '
                    # Start new entity
                    elif pos == 'B' and current_type:
                        named_entity = {
                            'type': current_type,
                            'word': tmp_word.strip(),
                            'start_idx': idx,
                            'end_idx': widx - 1
                        }
                        tmp_list.append(named_entity)
                        tmp_word = word + ' '
                        current_type = typ
                        idx = widx
                # Outside of entity
                elif tag == 'O' and current_type:
                    named_entity = {
                        'type': current_type,
                        'word': tmp_word.strip(),
                        'start_idx': idx,
                        'end_idx': widx - 1
                    }
                    tmp_list.append(named_entity)
                    tmp_word = ''
                    current_type = ''
                # End of sentence
                if widx + 1 == len(ner) and current_type:
                    named_entity = {
                        'type': current_type,
                        'word': tmp_word.strip(),
                        'start_idx': idx,
                        'end_idx': widx
                    }
                    tmp_list.append(named_entity)
            named_entities_list.append(tmp_list)
        return named_entities_list

    def generate_similary_sentences(self, sentence_synonym_dict_pair, word_segemented=False, segemented_output=False):
        org_sentence, synonym_dicts = sentence_synonym_dict_pair
        return_val = []
        # synonym_dicts: eg: 1: 'sinh', 2: 'TenBac' (each dict is instance of SynonymSet obj)
        # ['Bác', 'sinh', 'năm', '1890']
        if not word_segemented:
            words_segmented_sentences = self.word_segmentation_no_join(org_sentence)
        else:
            words_segmented_sentences = [org_sentence]
        for words_segmented_sentence in words_segmented_sentences:
            # synonym_replaceable_pos: [(0,2), (1,1)]
            synonym_replaceable_pos = self.get_synonym_replaceable_pos(words_segmented_sentence, synonym_dicts)
            # [2, 1]
            using_dicts = [srp[1] for srp in synonym_replaceable_pos]
            # Generate all posible combinations
            # eg: [('Bác', 'sinh'), ('Bác', 'ra đời'), ('Hồ_Chí_Minh', 'sinh'), ('Hồ_Chí_Minh', 'ra đời')]
            combinations = list(product(*(synonym_dicts[idx].words for idx in using_dicts)))
            # Create similary sentences
            for c in combinations:
                sentence = words_segmented_sentence[:]
                for idx, srp in enumerate(synonym_replaceable_pos):
                    sentence[srp[0]] = c[idx]
                return_val.append(' '.join(sentence) if not segemented_output else sentence)

        return return_val

    def get_synonym_replaceable_pos(self, org_sentence, synonym_dicts):
        # synonym_dicts: eg: 1: 'sinh', 2: 'TenBac' (each dict is instance of SynonymSet obj)
        # ['Bác', 'sinh', 'năm', '1890']
        # return [(0,2), (1,1)] - tuple of (word_pos_in_sentence, synonym_id)
        synonyms_replaceable_pos = []
        for idx, word in enumerate(org_sentence):
            for dictionary_id in synonym_dicts:
                synonyms_words = [w.lower() for w in synonym_dicts[dictionary_id].words]
                if word.lower() in synonyms_words:
                    synonyms_replaceable_pos.append((idx, dictionary_id))
        return synonyms_replaceable_pos

    def batch_generate_similary_sentences(self, sentence_synonym_dict_pairs):
        return [self.generate_similary_sentences(pair) for pair in sentence_synonym_dict_pairs]

    def get_synonym_dicts(self, word, synonym_dicts):
        # TODO:
        #  Use word embedding for sentiment analyze for more accurate in getting right synonym set
        #  in case of multiple meaning word may belong to multiple synonym set
        #  Currently get all synonym sets thats have the word
        return [synonym_dicts[sid] for sid in synonym_dicts if word in synonym_dicts[sid].words]

    def find_phrase_in_sentence(self, content, sentence, synonyms, start=None, end=None):
        content = [c.lower() for c in content]
        if not start:
            start = 0
        if not end:
            end = len(sentence) - 1
        sentence_lower = [w.lower() for w in sentence]
        split_sentence = sentence_lower[start:(end + 1)]
        full_sentence = SPACE.join(split_sentence)
        similaries = self.generate_similary_sentences(
            (content, synonyms),
            word_segemented=True,
            segemented_output=True)
        possibilities = []
        word_ranges = []
        for sim in similaries:
            # Should i search for words in sentence by order in array (1)
            # or just ok by having all words exist in sentence ? (2)
            # Using method 2 for now
            exist_arr = []
            idx_arr = []
            for w_idx, word in enumerate(sim):
                w_lower = word.lower()
                if w_lower in split_sentence:
                    exist_arr.append(True)
                    words = w_lower.split()
                    words_len = len(words)
                    if w_idx + 1 == len(sim):
                        word_to_append = words[(words_len - 1)]
                    else:
                        word_to_append = words[0]
                    idx_arr.append(split_sentence.index(word_to_append))
                else:
                    exist_arr.append(False)
                    break
            if all(exist_arr):
                idx_arr.sort()
                start_idx = idx_arr[0]
                end_idx = idx_arr[len(idx_arr) - 1]
                corresponse_part = (SPACE.join(sim), start_idx, end_idx)
                sim_length = len((SPACE.join(sim)).split())
                word_range = end_idx - start_idx + 1
                if sim_length == word_range:
                    possibilities.append(corresponse_part)
                    word_ranges.append(end_idx - start_idx)
        return possibilities[word_ranges.index(max(word_ranges))] if word_ranges else None

    def grammar_struct_analyze(self, sentence_pos, ng_patterns, critical_data_infos):
        sentence_struct = [w[1] for w in sentence_pos]
        struct_ok = True
        for pattern in ng_patterns:
            pattern_struct = pattern.split(MINUS)
            start_pos = critical_data_infos[1]
            end_pos = critical_data_infos[2]
            rel_pos_main = pattern_struct.index('main')
            rel_pos_end = len(pattern_struct) - 1
            tmp = start_pos - rel_pos_main
            left_pos = tmp if tmp >= 0 else 0
            tmp = end_pos + (rel_pos_end - rel_pos_main)
            right_pos = tmp if tmp <= (len(sentence_struct) - 1) else (len(sentence_struct) - 1)
            # walk to left
            for idx in range(start_pos - left_pos):
                # If Preposition so skip
                if pattern_struct[rel_pos_main - (idx + 1)] == 'E' and sentence_struct[start_pos - (idx + 1)] == 'E':
                    continue
                # Out of sentence, grammar error
                elif sentence_struct[rel_pos_main - idx] == 'E' and (start_pos - (idx + 1)) < 0:
                    struct_ok = False
                    break
                # NG pattern matching, change flag to False but keep walking to the end
                elif ((pattern_struct[rel_pos_main - (idx + 1)] != 'any' and pattern_struct[rel_pos_main - (idx + 1)] ==
                       sentence_struct[start_pos - (idx + 1)])
                      or (pattern_struct[rel_pos_main - (idx + 1)] == 'any')):
                    struct_ok = False
                # NG pattern not match, sentence is ok
                elif pattern_struct[rel_pos_main - (idx + 1)] != 'any' and pattern_struct[rel_pos_main - (idx + 1)] != \
                        sentence_struct[start_pos - (idx + 1)]:
                    struct_ok = True
                    break
            if not struct_ok:
                break
            # walk to right
            for idx in range(right_pos - end_pos):
                # If Preposition so skip
                if pattern_struct[rel_pos_main + (idx + 1)] == 'E' and sentence_struct[end_pos + (idx + 1)] == 'E':
                    continue
                # Out of sentence, grammar error
                elif sentence_struct[start_pos + idx] == 'E' and (end_pos + (idx + 1)) > (len(sentence_struct) - 1):
                    struct_ok = False
                    break
                # NG pattern matching, change flag to False but keep walking to the end
                elif ((pattern_struct[rel_pos_main + (idx + 1)] != 'any' and pattern_struct[rel_pos_main + (idx + 1)] ==
                       sentence_struct[end_pos + (idx + 1)])
                      or (pattern_struct[rel_pos_main + (idx + 1)] == 'any')):
                    struct_ok = False
                # NG pattern not match, sentence is ok
                elif pattern_struct[rel_pos_main + (idx + 1)] != 'any' and pattern_struct[rel_pos_main + (idx + 1)] != \
                        sentence_struct[end_pos + (idx + 1)]:
                    struct_ok = True
                    break
        return struct_ok

    def analyze_critical_parts(self, pos_tag, ner, intent, tokenized_sentence):
        # Data for the process
        intent_critical_datas = intent.subjects
        tokenized_sentence_list = tokenized_sentence.split()

        # Nothing to analyze
        if len(ner) == 0 and len(intent_critical_datas) == 0:
            return True

        # Compare named entities in sentence with entities in intent
        corresponse_parts = []
        check_flag = True
        for typ in self.ner_types:
            if not check_flag:
                break
            subjects_in_intent = []
            for c in intent_critical_datas:
                if c[intent_model.INTENT_SUBJECT_TYPE] == typ:
                    subjects_in_intent.append(c)

            # Find in the sentence for intent critical datas
            sit_1 = subjects_in_intent[:]
            for sit in sit_1:
                # find subject existence in the sentence
                # corresponse_part: (phrase, entity start pos, entity end pos)
                content = [part.split(COLON)[1] for part in sit[intent_model.INTENT_SUBJECT_WORDS].split(PLUS) if
                           part.split(COLON)[0] not in self.exclude_pos_tag]
                content = [c.lower() for c in content if c not in self.exclude_words]
                # print(content)
                corresponse_part = self.find_phrase_in_sentence(content, tokenized_sentence_list, intent.synonym_sets)
                # Critical part still not found -> not same intent
                if not corresponse_part:
                    check_flag = False
                    break
                corresponse_parts.append(corresponse_part)
                # Critical data existing, but need to check grammar structure too
                check_flag = self.grammar_struct_analyze(pos_tag, self.critical_data_ng_patterns, corresponse_part)

        return check_flag, corresponse_parts

    def analyze_verb_components(self, intent, subjects_in_sentence, tokenized_sentence):
        intent_subjects = intent.subjects
        tokenized_sentence_list = tokenized_sentence.split()
        for idx, (subject, subject_part_in_sentence) in enumerate(zip(intent_subjects, subjects_in_sentence)):
            verb = [v[1] for v in subject[intent_model.INTENT_SUBJECT_VERBS]]
            if not verb:
                continue
            startpos = subject_part_in_sentence[2] + 1
            next_subject_idx = idx + 1
            if next_subject_idx == len(subjects_in_sentence):
                endpos = len(tokenized_sentence_list) - 1
            else:
                endpos = subjects_in_sentence[next_subject_idx][1]
            verb_found_in_sentence = self.find_phrase_in_sentence(verb, tokenized_sentence_list, intent.synonym_sets, start=startpos, end=endpos)
            if not verb_found_in_sentence:
                return False

        return True

    def analyze_sentence_components(self, intent, sentence):
        # Word POS tagging
        # Can only handle simple sentence for now
        pos_tag = self.pos_tagging(sentence)[0]
        # Obtain named entity in the sentence
        ner = self.named_entity_reconize(sentence)
        # Data for the process
        tokenized_sentence = self.word_segmentation(sentence)

        flag, subjects = self.analyze_critical_parts(pos_tag, ner, intent, tokenized_sentence)
        if not flag:
            return flag
        flag = self.analyze_verb_components(intent, subjects, tokenized_sentence)
        return flag

    # BELOW IS CODE COPIED FROM https://gist.github.com/nguyenvanhieuvn/72ccf3ddf7d179b281fdae6c0b84942b
    def remove_stopwords(self, line):
        words = []
        for word in line.strip().split():
            if word not in self.stopwords:
                words.append(word)
        return ' '.join(words)

    def chuan_hoa_dau_tu_tieng_viet(self, word):
        if not self.is_valid_vietnam_word(word):
            return word

        chars = list(word)
        dau_cau = 0
        nguyen_am_index = []
        qu_or_gi = False
        for index, char in enumerate(chars):
            x, y = nguyen_am_to_ids.get(char, (-1, -1))
            if x == -1:
                continue
            elif x == 9:  # check qu
                if index != 0 and chars[index - 1] == 'q':
                    chars[index] = 'u'
                    qu_or_gi = True
            elif x == 5:  # check gi
                if index != 0 and chars[index - 1] == 'g':
                    chars[index] = 'i'
                    qu_or_gi = True
            if y != 0:
                dau_cau = y
                chars[index] = bang_nguyen_am[x][0]
            if not qu_or_gi or index != 1:
                nguyen_am_index.append(index)
        if len(nguyen_am_index) < 2:
            if qu_or_gi:
                if len(chars) == 2:
                    x, y = nguyen_am_to_ids.get(chars[1])
                    chars[1] = bang_nguyen_am[x][dau_cau]
                else:
                    x, y = nguyen_am_to_ids.get(chars[2], (-1, -1))
                    if x != -1:
                        chars[2] = bang_nguyen_am[x][dau_cau]
                    else:
                        chars[1] = bang_nguyen_am[5][dau_cau] if chars[1] == 'i' else bang_nguyen_am[9][dau_cau]
                return ''.join(chars)
            return word

        for index in nguyen_am_index:
            x, y = nguyen_am_to_ids[chars[index]]
            if x == 4 or x == 8:  # ê, ơ
                chars[index] = bang_nguyen_am[x][dau_cau]
                # for index2 in nguyen_am_index:
                #     if index2 != index:
                #         x, y = nguyen_am_to_ids[chars[index]]
                #         chars[index2] = bang_nguyen_am[x][0]
                return ''.join(chars)

        if len(nguyen_am_index) == 2:
            if nguyen_am_index[-1] == len(chars) - 1:
                x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
                chars[nguyen_am_index[0]] = bang_nguyen_am[x][dau_cau]
                # x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
                # chars[nguyen_am_index[1]] = bang_nguyen_am[x][0]
            else:
                # x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
                # chars[nguyen_am_index[0]] = bang_nguyen_am[x][0]
                x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
                chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
        else:
            # x, y = nguyen_am_to_ids[chars[nguyen_am_index[0]]]
            # chars[nguyen_am_index[0]] = bang_nguyen_am[x][0]
            x, y = nguyen_am_to_ids[chars[nguyen_am_index[1]]]
            chars[nguyen_am_index[1]] = bang_nguyen_am[x][dau_cau]
            # x, y = nguyen_am_to_ids[chars[nguyen_am_index[2]]]
            # chars[nguyen_am_index[2]] = bang_nguyen_am[x][0]
        return ''.join(chars)

    @staticmethod
    def is_valid_vietnam_word(word):
        chars = list(word)
        nguyen_am_index = -1
        for index, char in enumerate(chars):
            x, y = nguyen_am_to_ids.get(char, (-1, -1))
            if x != -1:
                if nguyen_am_index == -1:
                    nguyen_am_index = index
                else:
                    if index - nguyen_am_index != 1:
                        return False
                    nguyen_am_index = index
        return True

    def chuan_hoa_dau_cau_tieng_viet(self, sentence):
        """
            Chuyển câu tiếng việt về chuẩn gõ dấu kiểu cũ.
            :param sentence:
            :return:
            """
        sentence = sentence.lower()
        words = sentence.split()
        for index, word in enumerate(words):
            cw = re.sub(r'(^\p{P}*)([p{L}.]*\p{L}+)(\p{P}*$)', r'\1/\2/\3', word).split('/')
            # print(cw)
            if len(cw) == 3:
                cw[1] = self.chuan_hoa_dau_tu_tieng_viet(cw[1])
            words[index] = ''.join(cw)
        return ' '.join(words)

    @staticmethod
    def convert_unicode(txt):
        return re.sub(
            r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ',
            lambda x: dicchar[x.group()], txt)

language_processor = LanguageProcessor()
# language_processor = None
