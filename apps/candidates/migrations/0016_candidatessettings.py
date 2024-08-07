# Generated by Django 3.2.8 on 2022-01-19 22:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('candidates', '0015_candidate_product_format'),
    ]

    operations = [
        migrations.CreateModel(
            name='CandidatesSettings',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=100)),
                ('internal', models.BooleanField(default=False)),
                ('settings_obj', models.JSONField(null=True)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='candidates_settings',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]
