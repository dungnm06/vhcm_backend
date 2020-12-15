import os
from vhcm.common.singleton import Singleton
from vhcm.common.utils.files import unpickle_file
from vhcm.common.constants import PROJECT_ROOT, DIALOGUE_INTENT_RECOGNIZER_FILE_PATH, DIALOGUE_TFIDF_VECTORIZER_FILE_PATH

# Predict label
HCM_QUESTION = 'hcm_question'
OUT_OF_SCOPE_DIALOGUE = 'oos_dialogue'


class OutOfScopeIntentRecognizer(object, metaclass=Singleton):
    def __init__(self):
        self.recognizer = None
        self.tfidf_vectorizer = None

    def load(self):
        self.recognizer = unpickle_file(os.path.join(PROJECT_ROOT, DIALOGUE_INTENT_RECOGNIZER_FILE_PATH))
        self.tfidf_vectorizer = unpickle_file(os.path.join(PROJECT_ROOT, DIALOGUE_TFIDF_VECTORIZER_FILE_PATH))

    def predict(self, x):
        tfidf_vectorized_input = self.tfidf_vectorizer.transform([x.lower()])
        chat_type = self.recognizer.predict(tfidf_vectorized_input)[0]

        return chat_type
