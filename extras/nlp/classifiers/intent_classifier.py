import random
import pickle
import tensorflow as tf
import os
from pathlib import Path
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.metrics import SparseCategoricalAccuracy
from collections import Counter
from bert.PhoBERT import build_PhoBERT_classifier_model


class IntentModelConfig(object):
    def __init__(self, name, sequence_length, output_layer_size, activation):
        self.name = name
        self.sequence_length = sequence_length
        self.output_layer_size = output_layer_size
        self.activation = activation


def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)


def pickle_file(datas, filename):
    """Storing datas to the file using pickle."""
    with open(filename, 'wb') as fp:
        pickle.dump(datas, fp, protocol=pickle.HIGHEST_PROTOCOL)


def train_intent_classifier(data, output, sentencelength, batch, epoch, learning_rate, epsilon, activation):
    ###################################
    # --------- Import data --------- #
    # Import datas
    TRAIN_DATA = data
    data = unpickle_file(TRAIN_DATA)
    x = data['question']
    y = data['intent']
    # Intent mapping for future uses
    intents_count = Counter(y)
    INTENT_TO_IDX = {intent: i for i, intent in enumerate(intents_count)}
    IDX_TO_INTENT = {i: intent for i, intent in enumerate(intents_count)}
    # Intent list to index number for training
    y = [INTENT_TO_IDX[intent] for intent in y]
    # Shuffle train data
    temp = list(zip(x, y))
    random.shuffle(temp)
    x, y = zip(*temp)
    x = list(x)
    y = list(y)
    y = tf.constant(y)

    #####################################
    # ------- Setup BERT model -------- #
    # Max length of tokens
    SENTENCE_MAX_LENGTH = sentencelength
    # # Load transformers config and set output_hidden_states to False
    # config = AutoConfig.from_pretrained(BERT_MODEL)
    # config.output_hidden_states = True
    # Load BERT tokenizer, build the model
    model_name = 'Intent_Classifier_BERT_MultiClass'
    model, tokenizer = build_PhoBERT_classifier_model(sequence_length=SENTENCE_MAX_LENGTH,
                                                      output_layer_size=len(intents_count),
                                                      activation=activation, name=model_name)

    ###################################
    # ------- Train the model ------- #
    # Tokenize the input
    x = tokenizer(
        text=x,
        return_tensors='tf',
        add_special_tokens=True,  # add [CLS], [SEP]
        max_length=SENTENCE_MAX_LENGTH,  # max length of the text that can go to BERT
        padding='max_length',  # add [PAD] tokens
        return_attention_mask=True,  # add attention mask to not focus on pad tokens
        return_token_type_ids=False,
        truncation=True
    )
    # Hyperparameters
    BATCH_SIZE = batch
    EPOCHES = epoch
    LEARNING_RATE = learning_rate
    EPSILON = epsilon
    # Set an optimizer
    optimizer = Adam(
        learning_rate=LEARNING_RATE,
        epsilon=EPSILON)
    # Set loss and metrics
    loss = {'classifier': SparseCategoricalCrossentropy(from_logits=True)}
    metric = {'classifier': SparseCategoricalAccuracy('accuracy')}
    # Compile the model
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metric)
    # Fit the model
    model.fit(
        x={
            'input_ids': x['input_ids'],
            # 'token_type_ids': x_train['token_type_ids'],
            'attention_mask': x['attention_mask']
        },
        y={'classifier': y},
        batch_size=BATCH_SIZE,
        epochs=EPOCHES)

    # Save weight of trained model
    print('Saving data....')
    save_path = os.path.join(output, 'intent/model_weights')
    model.save_weights(save_path)

    # Save intent map
    map_datas = {
        'obj2idx': INTENT_TO_IDX,
        'idx2obj': IDX_TO_INTENT
    }
    pickle_file(map_datas, output + '/intent_map.pickle')

    # Save training config
    config = IntentModelConfig(model_name, SENTENCE_MAX_LENGTH, len(intents_count), activation)
    pickle_file(config, output + '/intent_config.pickle')
