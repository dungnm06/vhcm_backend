# Generated by Django 3.1.2 on 2020-11-23 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vhcm', '0026_auto_20201123_0000'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='chat_session_id',
            new_name='id',
        ),
    ]
