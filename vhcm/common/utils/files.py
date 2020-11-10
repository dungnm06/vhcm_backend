import pickle
import json

PICKLE_EXTENSION = '.pickle'


def unpickle_file(filename):
    """Returns the result of unpickling the file content."""
    with open(filename, 'rb') as f:
        return pickle.load(f)


def pickle_file(datas, filename):
    """Storing datas to the file using pickle."""
    with open(filename, 'wb') as fp:
        pickle.dump(datas, fp, protocol=pickle.HIGHEST_PROTOCOL)


def load_json(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data
