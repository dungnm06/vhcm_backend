import random
import shutil
import tensorflow as tf
import os
import json
from pathlib import Path
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.metrics import SparseCategoricalAccuracy
from collections import Counter
from bert.PhoBERT import build_PhoBERT_classifier_model
from utils import unpickle_file, unzip


def train_intent_classifier(datapath, output, sentencelength, batch, epoch, learning_rate, epsilon, activation, bot_version):
    ###################################
    # --------- Import data --------- #
    # Import datas
    datafile_folder = Path(datapath).resolve().parent
    unzip(datapath, output=datafile_folder)
    train_data_filepath = os.path.join(os.path.splitext(datapath)[0], 'train_data.pickle')
    TRAIN_DATA = unpickle_file(train_data_filepath)
    x = TRAIN_DATA['question']
    y = TRAIN_DATA['intent']
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
    with open(output + '/intent_map.json', 'w') as fp:
        json.dump(map_datas, fp, indent=4)

    # Save training config
    config = {
        'model_name': model_name,
        'sentence_max_length': SENTENCE_MAX_LENGTH,
        'output_size': len(intents_count),
        'activation_function': activation
    }
    with open(output + '/intent_config.json', 'w') as fp:
        json.dump(config, fp, indent=4)

    # Save bot version for next startup load
    bot_version_path = output + '/bot_version'
    if os.path.exists(bot_version_path):
        with open(bot_version_path) as f:
            version = json.load(f)
            version['next_startup'] = bot_version
    else:
        version = {
            'current': 0,
            'next_startup': bot_version
        }
    with open(bot_version_path, 'w') as f:
        json.dump(version, f, indent=4)

    # Clear traindata tempfile
    tempstorepath = os.path.dirname(os.path.abspath(datapath))
    if os.path.exists(tempstorepath):
        shutil.rmtree(tempstorepath)
