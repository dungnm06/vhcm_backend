import numpy as np
import os
import shutil
import random
from utils import *
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from pathlib import Path


def train_oos_intent_recognizer(datafile, output):
    """------------ HCM relative sentence and normal sentence recognition ------------"""
    # Load HCM relative data
    datafile_folder = Path(datafile).resolve().parent
    unzip(datafile, output=datafile_folder)
    train_data_filepath = os.path.join(os.path.splitext(datafile)[0], 'train_data.pickle')
    hcm_data = unpickle_file(train_data_filepath)
    hcm_data = hcm_data['question']
    sample_size = len(hcm_data)
    print('Total data len: {}'.format(sample_size))

    # Load dialogue data
    dialogue_data = load_text_data(os.path.join(ROOT, 'data/conversations.txt'))
    dialogue_data = random.sample(dialogue_data, sample_size)

    # Apply text_prepare function to preprocess the data.
    hcm_data = [text_prepare(text) for text in hcm_data]
    dialogue_data = [text_prepare(text) for text in dialogue_data]

    # Do a binary classification on TF-IDF representations of texts.
    # Labels will be either hcm_question for hcm relative questions or oos_dialogue for out of scope dialogue.
    # Prepare the data for this task:
    #    concatenate dialogue and stackoverflow examples into one sample
    #    split it into train and test in proportion 9:1, use random_state=0 for reproducibility
    #    transform it into TF-IDF features
    X = np.concatenate([hcm_data, dialogue_data])
    y = ['hcm_question'] * len(hcm_data) + ['oos_dialogue'] * len(dialogue_data)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)
    print('Train size = {}, test size = {}'.format(len(X_train), len(X_test)))

    X_train_tfidf, X_test_tfidf, tfidf_vectorizer = tfidf_features(X_train, X_test, os.path.join(output, 'dialogue_tfidf_vectorizer.pickle'))

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
    print('Xin chào bạn khoẻ không ?')
    question = text_prepare('Xin chào bạn khoẻ không ?')
    features = tfidf_vectorizer.transform([question])
    intent = intent_recognizer.predict(features)[0]
    print('Predicted: ' + intent)

    # Dump the classifier to use it in the running bot.
    # print('Saving data....')
    pickle_file(intent_recognizer, os.path.join(output, 'dialogue_intent_recognizer.pickle'))

    # Clear traindata tempfile
    if os.path.exists(os.path.splitext(datafile)[0]):
        shutil.rmtree(os.path.splitext(datafile)[0])
