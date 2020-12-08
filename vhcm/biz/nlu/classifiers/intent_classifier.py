import os
import json
import numpy as np
from vhcm.common.constants import *
from vhcm.common.singleton import Singleton
from extras.nlp.bert.PhoBERT import build_PhoBERT_classifier_model


class IntentModelConfig(object):
    def __init__(self, name, sequence_length, output_layer_size, activation):
        self.name = name
        self.sequence_length = sequence_length
        self.output_layer_size = output_layer_size
        self.activation = activation


class IntentClassifier(object, metaclass=Singleton):
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.intent_to_idx = None
        self.idx_to_intent = None
        self.config = None

    def unload(self):
        self.tokenizer = None
        self.model = None
        self.intent_to_idx = None
        self.idx_to_intent = None
        self.config = None

    def load(self):
        # Paths
        config_path = os.path.join(PROJECT_ROOT, INTENT_MODEL_CONFIG)
        intent_maps_path = os.path.join(PROJECT_ROOT, INTENT_MAP_FILE_PATH)
        model_path = os.path.join(PROJECT_ROOT, MODEL_DATA_FOLDER + INTENT_MODEL_NAME)
        model_folder = os.path.join(PROJECT_ROOT, MODEL_DATA_FOLDER) + 'intent/'
        model_file_to_check = [model_folder + f for f in CLASSIFIER_MODEL_FILES]
        if any([not os.path.exists(p) for p in [config_path, intent_maps_path, *model_file_to_check]]):
            raise RuntimeError('[startup] Missing initial data for intent classifier')

        # Unload current model first
        self.unload()
        # Model config
        with open(config_path) as json_file:
            self.config = json.load(json_file)

        # Intent maps
        with open(intent_maps_path) as json_file:
            intent_maps = json.load(json_file)
        self.intent_to_idx = intent_maps[OBJ2IDX]
        self.idx_to_intent = intent_maps[IDX2OBJ]

        # Pretrained model
        print('(IntentClassifier) Loading pretrained model from: ', model_path)
        self.model, self.tokenizer = build_PhoBERT_classifier_model(
            self.config['sentence_max_length'], self.config['output_size'],
            self.config['activation_function'], self.config['model_name']
        )
        self.model.load_weights(model_path)

    def predict(self, x):
        if not (self.model or self.idx_to_intent or self.tokenizer or self.config):
            return None
        else:
            # print('Predict:')
            # print(x)
            x = self.tokenizer(
                text=x,
                return_tensors='tf',
                add_special_tokens=True,  # add [CLS], [SEP]
                max_length=self.config['sentence_max_length'],  # max length of the text that can go to BERT
                padding='max_length',  # add [PAD] tokens
                return_attention_mask=True,  # add attention mask to not focus on pad tokens
                return_token_type_ids=False,
                truncation=True)
            input_dict = {
                'input_ids': x['input_ids'],
                'attention_mask': x['attention_mask']
            }
            pred = self.model.predict(input_dict)
            # print(pred)
            intent_idx = np.argmax(pred['classifier'], axis=1)[0]
            pred_intent = self.idx_to_intent[str(intent_idx)]
            # print("Intent: ", pred_intent)
        return pred_intent
