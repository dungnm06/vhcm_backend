import random
import pickle
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.metrics import SparseCategoricalAccuracy
from transformers import AutoTokenizer, TFAutoModel
from collections import Counter
from bert.PhoBERT import build_PhoBERT_classifier_model


def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)


def pickle_file(datas, filename):
    """Storing datas to the file using pickle."""
    with open(filename, 'wb') as fp:
        pickle.dump(datas, fp, protocol=pickle.HIGHEST_PROTOCOL)


def train_question_classifier(data, output, sentencelength, batch, epoch, learning_rate, epsilon, activation):
    #####################################
    # ------- Setup BERT model -------- #
    BERT_MODEL = 'vinai/phobert-base'
    # Max length of tokens
    SENTENCE_MAX_LENGTH = sentencelength
    # # Load transformers config and set output_hidden_states to False
    # config = AutoConfig.from_pretrained(BERT_MODEL)
    # config.output_hidden_states = True
    # Load BERT tokenizer, build the model
    model, tokenizer = build_PhoBERT_classifier_model(sequence_length=SENTENCE_MAX_LENGTH,
                                                      output_layer_size=1,
                                                      activation=activation, name='Intent_Classifier_BERT_MultiClass')
