# Generated by Django 2.2.23 on 2021-06-30 21:51

from decimal import Decimal
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('source_data', '0001_initial'),
        ('bookrank', '0023_work_isbn'),
        ('candidates', '0005_delete_candidate_and_source_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='AuthorCandidate',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                )
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('isbn', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=500)),
                ('abstract', models.TextField(blank=True)),
                ('edition', models.IntegerField(blank=True, null=True)),
                ('supplier', models.CharField(blank=True, max_length=200)),
                ('availability', models.IntegerField(blank=True, null=True)),
                (
                    'price',
                    models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10),
                ),
                ('price_currency', models.CharField(blank=True, max_length=10)),
                ('extra_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                (
                    'agent',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='candidates.Agent',
                    ),
                ),
                (
                    'authors',
                    models.ManyToManyField(
                        blank=True,
                        related_name='candidates',
                        through='candidates.AuthorCandidate',
                        to='bookrank.Author',
                    ),
                ),
                (
                    'data_record',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to='source_data.DataRecord'
                    ),
                ),
            ],
            options={'abstract': False},
        ),
        migrations.CreateModel(
            name='LanguageCandidate',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'candidate',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='candidates.Candidate'
                    ),
                ),
                (
                    'topic',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='bookrank.Language'
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='languages',
            field=models.ManyToManyField(
                blank=True,
                related_name='candidates',
                through='candidates.LanguageCandidate',
                to='bookrank.Language',
            ),
        ),
        migrations.AddField(
            model_name='candidate',
            name='publisher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='bookrank.Publisher',
            ),
        ),
        migrations.AddField(
            model_name='authorcandidate',
            name='candidate',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='candidates.Candidate'
            ),
        ),
        migrations.AddField(
            model_name='authorcandidate',
            name='topic',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to='bookrank.Author'
            ),
        ),
    ]
