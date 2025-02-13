# Generated by Django 3.1.2 on 2020-12-08 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vhcm', '0006_auto_20201207_1941'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_password_uid',
            field=models.TextField(db_index=True, null=True, verbose_name='uid for reset password process'),
        ),
        migrations.AddField(
            model_name='user',
            name='reset_password_uid_expire',
            field=models.DateTimeField(null=True, verbose_name='reset password uid expire time'),
        ),
    ]
