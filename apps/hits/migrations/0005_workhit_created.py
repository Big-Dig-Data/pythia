# Generated by Django 2.2.6 on 2019-10-09 13:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [('hits', '0004_workhit_typ')]

    operations = [
        migrations.AddField(
            model_name='workhit',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        )
    ]