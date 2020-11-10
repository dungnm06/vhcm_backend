import os
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from vhcm.biz.nlu.language_processing import language_processor
from vhcm.common.constants import *
from vhcm.common.singleton import Singleton
from vhcm.common.utils.files import unpickle_file
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
        self.intent_to_idx = None
        self.idx_to_intent = None
        self.config = None
        self.threshold = None
        self.label_binarizer = None

    def unload(self):
        self.tokenizer = None
        self.model = None
        self.intent_to_idx = None
        self.idx_to_intent = None
        self.config = None
        self.threshold = None
        self.label_binarizer = None

    def load(self):
        # Paths
        config_path = os.path.join(PROJECT_ROOT, QUESTION_TYPE_MODEL_CONFIG)
        question_type_maps_path = os.path.join(PROJECT_ROOT, QUESTION_TYPE_MAP_FILE_PATH)
        model_path = os.path.join(PROJECT_ROOT, MODEL_DATA_FOLDER + QUESTION_TYPE_MODEL_NAME)
        if any([os.path.exists(p) for p in [config_path, question_type_maps_path, model_path]]):
            return False

        # Unload current model first
        self.unload()
        # Model config
        self.config = unpickle_file(config_path)

        # Intent maps
        intent_maps = unpickle_file(question_type_maps_path)
        self.intent_to_idx = intent_maps[OBJ2IDX]
        self.idx_to_intent = intent_maps[IDX2OBJ]

        # Label Binarizer
        self.label_binarizer = MultiLabelBinarizer()
        self.label_binarizer.fit_transform([list(self.idx_to_intent.values())])
        
        # Threshold
        self.threshold = config.CONFIG_LOADER.get_setting_value_float(config.PREDICT_THRESHOLD)

        # Pretrained model
        print('(IntentClassifier) Loading pretrained model from: ', model_path)
        self.model, self.tokenizer = build_PhoBERT_classifier_model(
            self.config.sequence_length, self.config.output_layer_size, self.config.activation, self.config.name)
        self.model.load_weights(model_path)

        return True

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
            threshold = self.threshold
            preds = np.array([[1 if acc > threshold else 0 for acc in p] for p in preds['type']])
            preds = self.label_binarizer.inverse_transform(preds)
            # for predict in preds:
            print('Predicted types: ', ', '.join(preds[0]))
            return list(preds[0])


predict_instance = QuestionTypeClassifier()
