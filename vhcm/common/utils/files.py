import os
import pickle
import json
import zipfile

PICKLE_EXTENSION = '.pickle'
ZIP_EXTENSION = '.zip'


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


def zipdir(output, path):
    zipf = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    dirname = os.path.basename(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            abspath = os.path.join(root, file)
            filename = os.path.basename(abspath)
            zipf.write(abspath, dirname + '/' + filename)

    zipf.close()


def unzip(path, output='.'):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(output)


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
