# Generated by Django 3.2.8 on 2021-11-10 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('source_data', '0001_initial')]

    operations = [
        migrations.AlterField(
            model_name='datarecord',
            name='extracted_data',
            field=models.JSONField(
                blank=True, default=dict, help_text='Any data of interest extracted from raw data'
            ),
        ),
        migrations.AlterField(
            model_name='datarecord',
            name='other_ids',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]