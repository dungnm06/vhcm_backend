from django.db import models
from vhcm.common.constants import COMMA


# Fields
ID = 'synonym_id'
MEANING = 'meaning'
WORDS = 'words'
NAMED_ENTITY = 'ne_synonym'


class Synonym(models.Model):
    synonym_id = models.AutoField(
        primary_key=True, verbose_name='synonym id', serialize=True
    )
    meaning = models.CharField(
        max_length=50, verbose_name='synonym group main meaning'
    )
    words = models.TextField(
        verbose_name='words in synonym group'
    )
    ne_synonym = models.BooleanField(
        verbose_name='is named-entity synonym set', default=False
    )

    def get_words(self):
        return self.words.split(COMMA)

    class Meta:
        db_table = "synonyms"
