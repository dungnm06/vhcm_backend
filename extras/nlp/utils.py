import pickle
import re
import zipfile
from sklearn.feature_extraction.text import TfidfVectorizer


def load_text_data(txt_file):
    try:
        texts = []
        with open(txt_file, 'r', encoding='utf8') as fp:
            for line in fp:
                texts.append(line.strip())
        return texts
    except Exception as e:
        print(e)
        print('Failed to load file: ', txt_file)
        return []


def text_prepare(text):
    """Performs tokenization and simple preprocessing."""
    replace_by_space_re = re.compile(r'[/(){}\[\]|@,;!?]')
    # good_symbols_re = re.compile('[^0-9a-z #+_]')
    stopwords_set = set(load_text_data('data/stopwords.txt'))

    text = text.lower()
    text = replace_by_space_re.sub(' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # text = good_symbols_re.sub('', text)
    text = ' '.join([x for x in text.split() if x and x not in stopwords_set])

    return text.strip()


def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)


def pickle_file(datas, filename):
    """Storing datas to the file using pickle."""
    with open(filename, 'wb') as fp:
        pickle.dump(datas, fp, protocol=pickle.HIGHEST_PROTOCOL)


def tfidf_features(x_train, x_test, vectorizer_path):
    """Performs TF-IDF transformation and dumps the model."""

    # Train a vectorizer on X_train data.
    # Transform X_train and X_test data.
    tfidf_vectorizer = TfidfVectorizer(min_df=5, max_df=0.9, ngram_range=(1, 2), token_pattern=r'(\S+)')
    x_train = tfidf_vectorizer.fit_transform(x_train)
    x_test = tfidf_vectorizer.transform(x_test)

    # Pickle the trained vectorizer to 'vectorizer_path'
    with open(vectorizer_path, 'wb') as file:
        pickle.dump(tfidf_vectorizer, file)

    return x_train, x_test, tfidf_vectorizer


def unzip(path, output='.'):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(output)
