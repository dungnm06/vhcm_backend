import os
import json
import numpy as np
import traceback
from sklearn.preprocessing import MultiLabelBinarizer
from vhcm.biz.nlu.language_processing import language_processor
from vhcm.common.constants import *
from vhcm.common.singleton import Singleton
import vhcm.common.config.config_manager as config
from extras.nlp.bert.PhoBERT import build_PhoBERT_classifier_model


class QuestionModelConfig(object):
    def __init__(self, name, sequence_length, output_layer_size, activation):
        self.name = name
        self.sequence_length = sequence_length
        self.output_layer_size = output_layer_size
        self.activation = activation


class QuestionTypeClassifier(object, metaclass=Singleton):
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.type_to_idx = None
        self.idx_to_type = None
        self.config = None
        self.threshold = None
        self.label_binarizer = None

    def unload(self):
        self.tokenizer = None
        self.model = None
        self.type_to_idx = None
        self.idx_to_type = None
        self.config = None
        self.threshold = None
        self.label_binarizer = None

    def load(self):
        # Paths
        config_path = os.path.join(PROJECT_ROOT, QUESTION_TYPE_MODEL_CONFIG)
        question_type_maps_path = os.path.join(PROJECT_ROOT, QUESTION_TYPE_MAP_FILE_PATH)
        model_path = os.path.join(PROJECT_ROOT, MODEL_DATA_FOLDER + QUESTION_TYPE_MODEL_NAME)
        model_folder = os.path.join(PROJECT_ROOT, MODEL_DATA_FOLDER) + 'question_type/'
        model_file_to_check = [model_folder + f for f in CLASSIFIER_MODEL_FILES]
        if any([not os.path.exists(p) for p in [config_path, question_type_maps_path, *model_file_to_check]]):
            raise RuntimeError('[startup] Missing initial data for intent classifier')
        # Unload current model first
        self.unload()
        # Model config
        with open(config_path) as json_file:
            self.config = json.load(json_file)

        # Intent maps
        with open(question_type_maps_path) as json_file:
            question_type_map = json.load(json_file)
        self.type_to_idx = question_type_map[OBJ2IDX]
        self.idx_to_type = question_type_map[IDX2OBJ]

        # Label Binarizer
        self.label_binarizer = MultiLabelBinarizer()
        self.label_binarizer.fit_transform([list(self.idx_to_type.values())])

        # Threshold
        self.threshold = config.config_loader.get_setting_value_float(config.PREDICT_THRESHOLD)

        # Pretrained model
        print('(QuestionTypeClassifier) Loading pretrained model from: ', model_path)
        self.model, self.tokenizer = build_PhoBERT_classifier_model(
            self.config['sentence_max_length'], self.config['output_size'],
            self.config['activation_function'], self.config['model_name']
        )
        self.model.load_weights(model_path)

    def predict(self, input_query):
        if not (self.model or self.label_binarizer or self.tokenizer or self.config or self.threshold):
            return None
        else:
            print('Predict:')
            x = language_processor.word_segmentation(input_query)
            print(x)
            x = self.tokenizer(
                text=x,
                return_tensors='tf',
                add_special_tokens=True,  # add [CLS], [SEP]
                max_length=self.config.sequence_length,  # max length of the text that can go to BERT
                padding='max_length',  # add [PAD] tokens
                return_attention_mask=True,  # add attention mask to not focus on pad tokens
                return_token_type_ids=False,
                truncation=True)
            input_dict = {
                'input_ids': x['input_ids'],
                # 'token_type_ids': x['token_type_ids'],
                'attention_mask': x['attention_mask']
            }
            # x_tensor = tf.constant(np.concatenate((ids, atm), axis=0))
            # print(x_tensor)
            preds = self.model.predict(input_dict)
            # print(preds['type'])
            preds = np.array([[1 if acc > self.threshold else 0 for acc in p] for p in preds['type']])
            preds = self.label_binarizer.inverse_transform(preds)
            # for predict in preds:
            print('Predicted types: ', ', '.join(preds[0]))
            return list(preds[0])
