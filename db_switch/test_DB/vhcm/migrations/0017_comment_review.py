# Generated by Django 3.1.2 on 2020-11-20 03:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vhcm', '0016_auto_20201119_0407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.SmallIntegerField(choices=[(1, 'accept'), (2, 'reject'), (3, 'draft')], db_index=True, verbose_name='review action types')),
                ('review_detail', models.TextField(verbose_name='review detail')),
                ('cdate', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('knowledge_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_kd', to='vhcm.knowledgedata')),
                ('review_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_user', to=settings.AUTH_USER_MODEL, verbose_name='review user')),
            ],
            options={
                'db_table': 'knowledge_data_review',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('comment', models.TextField(verbose_name='comment text')),
                ('status', models.SmallIntegerField(choices=[(1, 'viewable'), (2, 'deleted')], verbose_name='comment viewable status')),
                ('cdate', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('mdate', models.DateTimeField(auto_now=True, verbose_name='modified date')),
                ('knowledge_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_kd', to='vhcm.knowledgedata', verbose_name='knowledge data the comment belong to')),
                ('reply_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_mentioned_comment', to='vhcm.comment', verbose_name='mentioned comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_user', to=settings.AUTH_USER_MODEL, verbose_name='comment user')),
            ],
            options={
                'db_table': 'knowledge_data_comment',
            },
        ),
    ]
