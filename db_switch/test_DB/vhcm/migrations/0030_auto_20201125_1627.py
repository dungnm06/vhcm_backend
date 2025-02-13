# Generated by Django 3.1.2 on 2020-11-25 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vhcm', '0029_auto_20201124_2328'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='reject_reason',
            new_name='processor_note',
        ),
        migrations.RenameField(
            model_name='report',
            old_name='intent',
            new_name='reported_intent',
        ),
        migrations.AddField(
            model_name='report',
            name='foward_intent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='vhcm.knowledgedata', verbose_name='knowledge data that issue forwarded to'),
        ),
    ]
