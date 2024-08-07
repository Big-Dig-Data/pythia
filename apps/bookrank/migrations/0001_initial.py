# Generated by Django 2.1.4 on 2018-12-10 10:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BRModel',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                (
                    'params',
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        default={
                            'forward_topic_weighing': True,
                            'topic_type_to_weight_coef': {
                                'AU': 1.0,
                                'CAT': 1.0,
                                'GEN': 1.0,
                                'KW': 1.0,
                            },
                        },
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'BookRank model', 'verbose_name_plural': 'BookRank models'},
        ),
        migrations.CreateModel(
            name='BRModelInstance',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('stats', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('input_checksum', models.CharField(blank=True, max_length=64)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                (
                    'model',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='instances',
                        to='bookrank.BRModel',
                    ),
                ),
            ],
            options={
                'verbose_name': 'BookRank model instance',
                'verbose_name_plural': 'BookRank model instances',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=250)),
                (
                    'typ',
                    models.CharField(
                        choices=[
                            ('AU', 'Author'),
                            ('KW', 'Keyword'),
                            ('CAT', 'Category'),
                            ('GEN', 'Generated'),
                        ],
                        max_length=5,
                    ),
                ),
                (
                    'extra_data',
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TopicScore',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'work_score',
                    models.DecimalField(
                        decimal_places=6, help_text='Score from associated works', max_digits=15
                    ),
                ),
                (
                    'mi',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='topic_scores',
                        to='bookrank.BRModelInstance',
                    ),
                ),
                (
                    'topic',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='topic_scores',
                        to='bookrank.Topic',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='TopicSubType',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=100)),
                (
                    'topic_type',
                    models.CharField(
                        choices=[
                            ('AU', 'Author'),
                            ('KW', 'Keyword'),
                            ('CAT', 'Category'),
                            ('GEN', 'Generated'),
                        ],
                        max_length=5,
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name_plural': 'Topic sub-types'},
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('uid', models.CharField(max_length=64)),
                ('name', models.TextField(blank=True)),
                ('abstract', models.TextField(blank=True)),
                (
                    'extra_data',
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkCategory',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=250)),
            ],
            options={'verbose_name_plural': 'Work categories'},
        ),
        migrations.CreateModel(
            name='WorkScore',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'hit_score',
                    models.DecimalField(
                        decimal_places=6, help_text='Score from hits', max_digits=15
                    ),
                ),
                (
                    'topic_score',
                    models.DecimalField(
                        decimal_places=6, help_text='Score from associated topics', max_digits=15
                    ),
                ),
                (
                    'mi',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='work_scores',
                        to='bookrank.BRModelInstance',
                    ),
                ),
                (
                    'work',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='work_scores',
                        to='bookrank.Work',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='WorkSet',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('name', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='WorkTopic',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'weight',
                    models.DecimalField(
                        decimal_places=6,
                        help_text='Coefficient between 0-1 characterizing the strength of a bond between a work and a topic.',
                        max_digits=8,
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                (
                    'topic',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='worktopics',
                        to='bookrank.Topic',
                    ),
                ),
                (
                    'work',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='worktopics',
                        to='bookrank.Work',
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='work',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='bookrank.WorkCategory'
            ),
        ),
        migrations.AddField(
            model_name='work',
            name='topics',
            field=models.ManyToManyField(
                related_name='works', through='bookrank.WorkTopic', to='bookrank.Topic'
            ),
        ),
        migrations.AddField(
            model_name='work',
            name='work_set',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='works',
                to='bookrank.WorkSet',
            ),
        ),
        migrations.AddField(
            model_name='topic',
            name='subtyp',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to='bookrank.TopicSubType'
            ),
        ),
        migrations.AddField(
            model_name='topic',
            name='work_set',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='topics',
                to='bookrank.WorkSet',
            ),
        ),
        migrations.AddField(
            model_name='brmodelinstance',
            name='topics',
            field=models.ManyToManyField(
                related_name='mis', through='bookrank.TopicScore', to='bookrank.Topic'
            ),
        ),
        migrations.AddField(
            model_name='brmodelinstance',
            name='work_set',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='mis',
                to='bookrank.WorkSet',
            ),
        ),
        migrations.AddField(
            model_name='brmodelinstance',
            name='works',
            field=models.ManyToManyField(
                related_name='mis', through='bookrank.WorkScore', to='bookrank.Work'
            ),
        ),
        migrations.AlterUniqueTogether(name='work', unique_together={('uid', 'work_set')}),
    ]
