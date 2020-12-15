import json
import random
import numpy as np
import os
import shutil
import pandas as pd
from vncorenlp import VnCoreNLP
from utils import *
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from pathlib import Path
from itertools import product


HASH = '#'
PERIOD = '.'
COLON = ':'
COMMA = ','
PLUS = '+'
MINUS = '-'
SPACE = ' '
UNDERSCORE = '_'
EXCLAMATION = '!'
NEW_LINE = '\n'
INTENT_SUBJECT_TYPE = 'type'
INTENT_SUBJECT_WORDS = 'words'
INTENT_SUBJECT_VERBS = 'verbs'
INTENT_VERB_EMPTY = 'empty'


# Mapping
SYNONYM_ID = 'id'
SYNONYM_MEANING = 'meaning'
SYNONYM_WORDS = 'words'


class SynonymSet:
    def __init__(self, synonym_model=None, set_id=0, meaning='', words=None):
        if synonym_model:
            self.id = synonym_model.synonym_id
            self.meaning = synonym_model.meaning
            self.words = [word for word in synonym_model.words.split(COMMA)]
        else:
            # ID
            self.id = set_id
            # Meaning
            self.meaning = meaning
            # Words in this synonym set
            if words is None:
                words = []
            self.words = words


class LanguageProcessor(object):
    def __init__(self):
        # Variables for language understanding tasks
        # self.config = config.config_loader
        self.rdrsegmenter = VnCoreNLP("C:\\Users\\Tewi\\Desktop\\nlp\\vncorenlp\\VnCoreNLP-1.1.1.jar")
        # self.rdrsegmenter = None
        self.ner_types = ['LOC', 'PER', 'ORG', 'MISC']
        self.critical_data_ng_patterns = ['N-E-main', 'N-main']
        self.exclude_pos_tag = ['E', 'A', 'L', 'CH', 'X', 'P']
        self.exclude_words = ['bị', 'được', 'giữa', 'và', 'là']

    def word_segmentation_no_join(self, text):
        return self.rdrsegmenter.tokenize(text)

    def batch_word_segmentation(self, texts):
        segmented_text = []
        if type(texts) is list:
            for text in texts:
                tmp = self.word_segmentation(text)
                segmented_text.append(tmp)
        elif type(texts) is str:
            segmented_text.append(self.word_segmentation(texts))
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

    def generate_similary_sentences(self, sentence_synonym_dict_pair, word_segemented=False, segemented_output=False, lower=False):
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
            using_dicts = [srp['sid'] for srp in synonym_replaceable_pos]
            # Generate all posible combinations
            # eg: [('Bác', 'sinh'), ('Bác', 'ra đời'), ('Hồ_Chí_Minh', 'sinh'), ('Hồ_Chí_Minh', 'ra đời')]
            combinations = list(product(*(synonym_dicts[idx].words for idx in using_dicts)))
            # Create similary sentences
            for c in combinations:
                sentence = words_segmented_sentence[:]
                padding = 0
                for idx, srp in enumerate(synonym_replaceable_pos):
                    replace_part = c[idx].split()
                    sentence[srp['start_idx'] + padding:srp['end_idx'] + 1 + padding] = replace_part
                    padding += len(replace_part) - (srp['end_idx'] - srp['start_idx'] + 1)
                if lower:
                    sentence = [w.lower() for w in sentence]
                return_val.append(' '.join(sentence).capitalize() if not segemented_output else sentence)

        return return_val

    def get_synonym_replaceable_pos(self, org_sentence, synonym_dicts):
        """
        synonym_dicts: eg: 1: 'TenBac' (each dict is instance of SynonymSet obj)
        ['Bác', 'sinh', 'năm', '1890']
        return [{
            'word': 'Bác',
            'start_idx': 0,
            'end_idx': 0,
            'sid': 1
        }] - list of replaceable position
        """
        synonyms_replaceable_pos = []
        sentence_lower = [w.lower() for w in org_sentence]
        sentence_lower_joined = SPACE.join(sentence_lower)
        for dictionary_id in synonym_dicts:
            synonyms_words = [w.lower() for w in synonym_dicts[dictionary_id].words]
            for sw in synonyms_words:
                if sw in sentence_lower_joined:
                    sw_splited = sw.split()
                    start_idxs = [idx for idx, w in enumerate(sentence_lower) if w == sw_splited[0]]
                    for start_idx in start_idxs:
                        if start_idx + len(sw_splited) > len(sentence_lower):
                            continue
                        ok_flag = True
                        for sw_idx, sentence_idx in enumerate(range(start_idx, start_idx+len(sw_splited))):
                            if sw_splited[sw_idx] != sentence_lower[sentence_idx]:
                                ok_flag = False
                                break
                        if not ok_flag:
                            continue
                        end_idx = start_idx + len(sw_splited) - 1
                        # Recheck if adding synonym is subset of added synonym (eg: 'thư' is subset of 'bức thư')
                        for srp in synonyms_replaceable_pos:
                            if sw in srp['word'] and sw != srp['word'] and dictionary_id == srp['sid']:
                                ok_flag = False
                                break
                            if srp['word'] in sw and sw != srp['word'] and dictionary_id == srp['sid']:
                                synonyms_replaceable_pos.remove(srp)
                                break
                        if ok_flag:
                            # Push to result list
                            synonyms_replaceable_pos.append({
                                'word': sw,
                                'start_idx': start_idx,
                                'end_idx': end_idx,
                                'sid': dictionary_id
                            })
        synonyms_replaceable_pos.sort(key=lambda x: x['start_idx'])
        return synonyms_replaceable_pos

    def batch_generate_similary_sentences(self, sentence_synonym_dict_pairs):
        return [self.generate_similary_sentences(pair) for pair in sentence_synonym_dict_pairs]

    def get_synonym_dicts(self, word, synonym_dicts):
        # TODO:
        #  Use word embedding for sentiment analyze for more accurate in getting right synonym set
        #  in case of multiple meaning word may belong to multiple synonym set
        #  Currently get all synonym sets thats have the word
        return [synonym_dicts[sid] for sid in synonym_dicts if word in synonym_dicts[sid].words]

    def find_phrase_in_sentence(self, content, sentence, raw_sentence, synonyms, raw_start=None, raw_end=None):
        content = [c.lower() for c in content]
        if not raw_start:
            raw_start = 0
        if not raw_end:
            raw_end = len(raw_sentence) - 1

        start = 0
        for raw_sen_idx in range(raw_start, raw_end + 1):
            try:
                start = sentence.index(raw_sentence[raw_sen_idx])
                break
            except ValueError:
                continue
        end = len(sentence) - 1
        sentence_length = len(sentence)
        for raw_sen_idx in range(raw_end, raw_start - 1, -1):
            try:
                end = sentence_length - 1 - sentence[::-1].index(raw_sentence[raw_sen_idx])
                break
            except ValueError:
                continue
        sentence_lower = [w.lower() for w in sentence]
        raw_sentence_lower = [w.lower() for w in raw_sentence]
        split_sentence = sentence_lower[start:(end + 1)]
        raw_split_sentence = raw_sentence_lower[raw_start:(raw_end + 1)]
        similaries = self.generate_similary_sentences(
            (content, synonyms),
            word_segemented=True,
            segemented_output=True,
            lower=True)
        print(similaries)
        possibilities = []
        word_ranges = []
        for sim in similaries:
            exist_arr = []
            idx_arr = []
            raw_idx_arr = []
            if sim:
                possibilities_starts_pos = [idx for idx, w in enumerate(split_sentence) if w == sim[0].lower()]
                raw_possibilities_starts_pos = [idx for idx, w in enumerate(raw_split_sentence) if w == sim[0].lower()]
                print(possibilities_starts_pos)
                if not possibilities_starts_pos:
                    continue

                for (i1, idx), idx2 in zip(enumerate(possibilities_starts_pos), raw_possibilities_starts_pos):
                    exist_arr.append(True)
                    # For cleaned sentence
                    idx_arr.append(idx)
                    start_idx = idx
                    next_pos = i1 + 1
                    end_idx = possibilities_starts_pos[next_pos] if next_pos < len(possibilities_starts_pos) else (
                                len(split_sentence) - 1)
                    # For raw sentence
                    raw_idx_arr.append(idx2)
                    if len(sim) > (end_idx - start_idx + 1):
                        break
                    tmp_search_part = split_sentence[start_idx:(end_idx + 1)]
                    for w_idx, word in enumerate(sim[1:]):
                        w_lower = word.lower()
                        if w_lower in tmp_search_part:
                            exist_arr.append(True)
                            words = w_lower.split()
                            words_len = len(words)
                            if w_idx + 1 == len(sim):
                                word_to_append = words[(words_len - 1)]
                            else:
                                word_to_append = words[0]
                            idx_arr.append(split_sentence.index(word_to_append))
                            raw_idx_arr.append(raw_split_sentence.index(word_to_append))
                        else:
                            exist_arr.append(False)
                            break
                    if all(exist_arr):
                        idx_arr.sort()
                        raw_idx_arr.sort()
                        content_start_idx = idx_arr[0]
                        content_end_idx = idx_arr[len(idx_arr) - 1]
                        corresponse_part = (SPACE.join(sim), raw_start + raw_idx_arr[0], raw_start + raw_idx_arr[len(raw_idx_arr) - 1])
                        sim_length = len((SPACE.join(sim)).split())
                        word_range = content_end_idx - content_start_idx + 1
                        if sim_length == word_range:
                            possibilities.append(corresponse_part)
                            word_ranges.append(content_end_idx - content_start_idx)
                    exist_arr = []
                    idx_arr = []

        return possibilities

    def text_prepare(self, text, lower=False):
        """Performs tokenization and simple preprocessing."""
        replace_by_space_re = re.compile(r'[/(){}\[\]|@,;!?]')

        if lower:
            text = text.lower()
        text = replace_by_space_re.sub(' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text


language_processor = LanguageProcessor()


def train_context_intent_recognizer(datafile, output):
    """------------ HCM relative sentence and normal sentence recognition ------------"""
    # Load HCM relative data
    datafile_folder = Path(datafile).resolve().parent
    unzip(datafile, output=datafile_folder)
    train_data_filepath = os.path.join(os.path.splitext(datafile)[0], 'train_data.pickle')
    hcm_data = unpickle_file(train_data_filepath)
    hcm_data = hcm_data['question']

    # Load context question data
    intents_data_path = os.path.join(os.path.splitext(datafile)[0], 'IntentData.csv')
    intent_datas = pd.read_csv(intents_data_path, dtype=str)

    intents_data_path_org = os.path.join(os.path.splitext(datafile)[0], 'intent_data.csv')
    intent_datas_org = pd.read_csv(intents_data_path_org, dtype=str)

    synonym_data = None
    # Synonym data
    with open(os.path.join(os.path.splitext(datafile)[0], 'synonyms.json'), encoding='utf-8') as synonym_file:
        synonym_data = json.load(synonym_file)

    context_question_arr = []
    for idx, data in intent_datas.iterrows():
        intent_id = data['Intent']
        context_questions = data['Context question']
        if not pd.isnull(context_questions):
            questions = context_questions.split('#')
            questions = language_processor.batch_word_segmentation(questions)

            synonym_sets = {}
            synonyms = intent_datas_org.loc[intent_datas_org['Intent'] == intent_id]
            if not synonyms.empty:
                synonyms = synonyms['SynonymsID'].iloc[0]
                if not pd.isnull(synonyms):
                    synonyms = synonyms.split(COMMA)
                    for s in synonyms:
                        synonym_set = SynonymSet()
                        synonym_set.id = int(s)
                        synonym_set.meaning = synonym_data[s][SYNONYM_MEANING]
                        synonym_set.words = synonym_data[s][SYNONYM_WORDS]
                        synonym_sets[s] = synonym_set

            if synonym_sets:
                for question in questions:
                    context_question_arr.extend(language_processor.generate_similary_sentences((question.split(), synonym_sets), word_segemented=True))
            else:
                context_question_arr.extend(questions)

    # Apply text_prepare function to preprocess the data.
    hcm_data = [text_prepare(text) for text in hcm_data]
    context_question_arr = [text_prepare(text) for text in context_question_arr]
    context_question_arr = [text for text in context_question_arr if text]
    context_question_len = len(context_question_arr)
    hcm_data = random.sample(hcm_data, context_question_len*3)
    hcm_data_len = len(hcm_data)
    print('Context question length: ' + str(context_question_len))
    print('HCM question length: ' + str(hcm_data_len))
    print('Total data len: {}'.format(context_question_len + hcm_data_len))
    with open('context_questions.txt', 'w', encoding='utf-8') as context_file:
        for question in context_question_arr:
            context_file.write(question + '\n')

    # Do a binary classification on TF-IDF representations of texts.
    # Labels will be either hcm_question for hcm relative questions or oos_dialogue for out of scope dialogue.
    # Prepare the data for this task:
    #    concatenate dialogue and stackoverflow examples into one sample
    #    split it into train and test in proportion 9:1, use random_state=0 for reproducibility
    #    transform it into TF-IDF features
    X = np.concatenate([hcm_data, context_question_arr])
    y = ['hcm_question'] * len(hcm_data) + ['context_question'] * len(context_question_arr)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
    print('Train size = {}, test size = {}'.format(len(X_train), len(X_test)))

    X_train_tfidf, X_test_tfidf, tfidf_vectorizer = tfidf_features(X_train, X_test, os.path.join(output, 'context_tfidf_vectorizer.pickle'))

    # Train the **intent recognizer** using LogisticRegression on the train set
    intent_recognizer = LogisticRegression(penalty='l2', C=10, random_state=0, verbose=1, n_jobs=2, max_iter=2000)
    intent_recognizer.fit(X_train_tfidf, y_train)

    # Check test accuracy.
    y_test_pred = intent_recognizer.predict(X_test_tfidf)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    print('Test accuracy = {}'.format(test_accuracy))

    print('Simple test: ')
    print('Bác Hồ sinh năm nào?')
    question = text_prepare('Bác_Hồ sinh năm nào?')
    features = tfidf_vectorizer.transform([question])
    intent = intent_recognizer.predict(features)[0]
    print('Predicted: ' + intent)
    print()
    print('Ở đâu ?')
    question = text_prepare('Ở đâu ?')
    features = tfidf_vectorizer.transform([question])
    intent = intent_recognizer.predict(features)[0]
    print('Predicted: ' + intent)

    # Dump the classifier to use it in the running bot.
    # print('Saving data....')
    pickle_file(intent_recognizer, os.path.join(output, 'context_question_recognizer.pickle'))

    # Clear traindata tempfile
    if os.path.exists(os.path.splitext(datafile)[0]):
        shutil.rmtree(os.path.splitext(datafile)[0])
