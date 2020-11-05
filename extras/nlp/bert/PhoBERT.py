from tensorflow.keras.layers import Input, Dropout, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.initializers import TruncatedNormal
from transformers import AutoTokenizer, TFAutoModel, AutoConfig


def build_PhoBERT_classifier_model(sequence_length, output_layer_size, activation, name='default_phobert_name'):
    BERT_MODEL = 'vinai/phobert-base'
    # Load transformers config and set output_hidden_states to False
    config = AutoConfig.from_pretrained(BERT_MODEL)
    config.output_hidden_states = True
    # Load BERT tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL)
    # Load the Transformers BERT model
    transformer_model = TFAutoModel.from_pretrained(BERT_MODEL)

    # TF Keras documentation: https://www.tensorflow.org/api_docs/python/tf/keras/Model
    # Load the MainLayer
    bert = transformer_model.layers[0]
    # Build your model input
    input_ids = Input(shape=(sequence_length,), name='input_ids', dtype='int32')
    # token_ids = Input(shape=(SENTENCE_MAX_LENGTH,), name='token_type_ids', dtype='int32')
    attention_mask = Input(shape=(sequence_length,), name='attention_mask', dtype='int32')
    inputs = {'input_ids': input_ids, 'attention_mask': attention_mask}
    # inputs = {'input_ids': input_ids, 'token_type_ids': token_ids, 'attention_mask': attention_mask}
    # Load the Transformers BERT model as a layer in a Keras model
    bert_model = bert(inputs)[1]
    dropout = Dropout(config.hidden_dropout_prob, name='pooled_output')
    pooled_output = dropout(bert_model)
    # Output layer
    output = Dense(units=output_layer_size,
                   kernel_initializer=TruncatedNormal(stddev=config.initializer_range), name='classifier',
                   activation=activation)(pooled_output)
    outputs = {'classifier': output}
    # And combine it all in a model object
    model = Model(inputs=inputs, outputs=outputs, name=name)

    # Take a look at the model
    model.summary()

    return model
