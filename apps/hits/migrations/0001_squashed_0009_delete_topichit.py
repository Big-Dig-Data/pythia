# Generated by Django 2.2.23 on 2021-05-20 10:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [
        ('hits', '0001_initial'),
        ('hits', '0002_hit_target_id_textfield'),
        ('hits', '0003_workhit'),
        ('hits', '0004_workhit_typ'),
        ('hits', '0005_workhit_created'),
        ('hits', '0006_hittype_slug'),
        ('hits', '0007_topichit'),
        ('hits', '0008_createdupdatedmixin'),
        ('hits', '0009_delete_topichit'),
    ]

    initial = True

    dependencies = [('bookrank', '0009_topic_typ_index'), ('bookrank', '0006_more_bookrank_algos')]

    operations = [
        migrations.CreateModel(
            name='HitSet',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=120)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='HitType',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(default='', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Hit',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('target_id', models.TextField()),
                ('score', models.IntegerField(default=1, help_text='Size or number of the hit(s)')),
                (
                    'date',
                    models.DateField(
                        blank=True,
                        help_text='May be empty in cases where date is not known',
                        null=True,
                    ),
                ),
                (
                    'hitset',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='hits.HitSet'
                    ),
                ),
                (
                    'typ',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='hits.HitType'
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='WorkHit',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('value', models.IntegerField(default=1)),
                (
                    'date',
                    models.DateField(
                        blank=True,
                        help_text='May be empty in cases where date is not known',
                        null=True,
                    ),
                ),
                (
                    'work',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='bookrank.Work'
                    ),
                ),
                (
                    'typ',
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.CASCADE, to='hits.HitType'
                    ),
                ),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='hitset', name='last_updated', field=models.DateTimeField(auto_now=True)
        ),
        migrations.AddField(
            model_name='workhit', name='last_updated', field=models.DateTimeField(auto_now=True)
        ),
    ]