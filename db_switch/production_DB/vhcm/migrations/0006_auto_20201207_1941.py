# Generated by Django 3.1.2 on 2020-12-07 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vhcm', '0005_auto_20201207_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledgedatatraindatalink',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
