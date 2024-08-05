# Generated by Django 2.1.5 on 2019-01-29 09:29

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('title', models.CharField(max_length=500)),
                (
                    'id_in_source',
                    models.CharField(help_text='ID used in the source document', max_length=30),
                ),
                (
                    'data',
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict, help_text='Data converted to our internal format'
                    ),
                ),
                (
                    'raw_data',
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict, help_text='Data as present in the source'
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=120)),
                ('url', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='source',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='candidates.Source'
            ),
        ),
    ]
