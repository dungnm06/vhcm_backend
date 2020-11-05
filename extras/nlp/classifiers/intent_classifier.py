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


def train_intent_classifier(data, output, sentencelength, batch, epoch, learning_rate, epsilon, activation):
    ###################################
    # --------- Setup BERT ---------- #
    BERT_MODEL = 'vinai/phobert-base'
    # Max length of tokens
    SENTENCE_MAX_LENGTH = sentencelength
    # # Load transformers config and set output_hidden_states to False
    # config = AutoConfig.from_pretrained(BERT_MODEL)
    # config.output_hidden_states = True
    # Load BERT tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL)
    # Load the Transformers BERT model
    transformer_model = TFAutoModel.from_pretrained(BERT_MODEL)

    ###################################
    # --------- Import data --------- #
    # Import datas
    TRAIN_DATA = data
    data = unpickle_file(TRAIN_DATA)
    x = data['x']
    y = data['y']
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

    ###################################
    # ------- Build the model ------- #

    model = build_PhoBERT_classifier_model(sequence_length=SENTENCE_MAX_LENGTH, output_layer_size=len(intents_count),
                    activation=activation, name='Intent_Classifier_BERT_MultiClass')
    # model.load_weights('/content/drive/My Drive/training-data/intent_reconizer')

    ###################################
    # ------- Train the model ------- #
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
    SAVE_NAME = 'intent_reconizer'
    save_path = output
    path = save_path + '/{time}/'.format(time=datetime.now().strftime('%d-%m-%Y_%H-%M-%S'))
    model.save_weights(path + SAVE_NAME)

    # Save intent map
    map_datas = {
        'obj2idx': INTENT_TO_IDX,
        'idx2obj': IDX_TO_INTENT
    }
    pickle_file(map_datas, path + '/intent_map.pickle')
