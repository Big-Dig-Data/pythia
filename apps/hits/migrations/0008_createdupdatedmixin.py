# Generated by Django 2.2.16 on 2020-10-23 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('hits', '0007_topichit')]

    operations = [
        migrations.AddField(
            model_name='hitset', name='last_updated', field=models.DateTimeField(auto_now=True)
        ),
        migrations.AddField(
            model_name='topichit', name='last_updated', field=models.DateTimeField(auto_now=True)
        ),
        migrations.AddField(
            model_name='workhit', name='last_updated', field=models.DateTimeField(auto_now=True)
        ),
    ]
