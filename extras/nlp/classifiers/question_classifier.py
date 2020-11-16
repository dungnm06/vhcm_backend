import os
import random
import pickle
import tensorflow as tf
from sklearn.preprocessing import MultiLabelBinarizer
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.metrics import CategoricalAccuracy
from bert.PhoBERT import build_PhoBERT_classifier_model


class QuestionModelConfig(object):
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


def types_map_generate(types):
    t2i = {}
    i2t = {}
    id_count = 1
    for t in types:
        t2i[t] = id_count
        id_count += 1
    i2t = {v: k for k, v in t2i.items()}
    return t2i, i2t


def train_question_classifier(datapath, output, sentencelength, batch, epoch, learning_rate, epsilon, activation):
    ###################################
    # --------- Import data --------- #
    # Import data from csv
    # Import datas
    data = unpickle_file(datapath)
    x = data['question']
    y = data['type']
    # Ready output data for the model
    y = [[int(t) for t in types.split(',')] for types in y]
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(y)
    # print(y)
    # get all question types
    types = mlb.classes_
    # print(types)
    type2id_map, id2type_map = types_map_generate(types)
    print(id2type_map)
    print(type2id_map)

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
    model_name = 'QuestionType_BERT_MultiLabel'
    model, tokenizer = build_PhoBERT_classifier_model(sequence_length=SENTENCE_MAX_LENGTH,
                                                      output_layer_size=len(types),
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
        truncation=True)

    # Hyperparameters
    BATCH_SIZE = batch
    EPOCHES = epoch
    LEARNING_RATE = learning_rate
    EPSILON = epsilon
    # Set an optimizer
    optimizer = Adam(
        learning_rate=LEARNING_RATE,
        epsilon=EPSILON,
        decay=0.01,
        clipnorm=1.0)

    # Set loss and metrics
    loss = {'type': CategoricalCrossentropy(from_logits=True)}
    metric = {'type': CategoricalAccuracy('accuracy')}
    # Compile the model
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metric)
    # Fit the model
    model.fit(
        x={
            'input_ids': x['input_ids'],
            'attention_mask': x['attention_mask']
        },
        y={'classifier': y},
        # validation_split=0.2,
        batch_size=BATCH_SIZE,
        epochs=EPOCHES)

    # Save weight of trained model
    print('Saving data....')
    save_path = os.path.join(output, 'intent/model_weights')
    model.save_weights(save_path)

    # Save intent map
    map_datas = {
        'obj2idx': type2id_map,
        'idx2obj': id2type_map
    }
    pickle_file(map_datas, output + '/question_type_map.pickle')

    # Save training config
    config = QuestionModelConfig(model_name, SENTENCE_MAX_LENGTH, len(types), activation)
    pickle_file(config, output + '/question_type_config.pickle')
