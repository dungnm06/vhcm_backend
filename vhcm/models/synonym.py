from django.db import models
from vhcm.common.constants import COMMA


# Fields
ID = 'synonym_id'
MEANING = 'meaning'
WORDS = 'words'


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

    def get_words(self):
        return self.words.split(COMMA)

    class Meta:
        db_table = "synonyms"
