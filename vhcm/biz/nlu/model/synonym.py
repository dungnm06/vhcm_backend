from vhcm.common.constants import COMMA

# Mapping
SYNONYM_ID = 'id'
SYNONYM_MEANING = 'meaning'
SYNONYM_WORDS = 'words'


class SynonymSet:
    def __init__(self, synonym_model=None, set_id=0, meaning='', words=None):
        if synonym_model:
            self.id = synonym_model.synonym_id
            self.meaning = synonym_model.meaning
            self.words = [word for word in synonym_model.words.split(COMMA)]
        else:
            # ID
            self.id = set_id
            # Meaning
            self.meaning = meaning
            # Words in this synonym set
            if words is None:
                words = []
            self.words = words
