# Generated by Django 2.2.23 on 2021-08-29 20:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('candidates', '0008_adds_subjects_to_candidates'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBookmarkedCandidate',
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
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='UserBlacklistedCandidate',
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
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='blacklisted_by',
            field=models.ManyToManyField(
                blank=True,
                related_name='blacklisted_candidates',
                through='candidates.UserBlacklistedCandidate',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='candidate',
            name='bookmarked_by',
            field=models.ManyToManyField(
                blank=True,
                related_name='bookmarked_candidates',
                through='candidates.UserBookmarkedCandidate',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
