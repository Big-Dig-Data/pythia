# Generated by Django 2.2.6 on 2019-10-16 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('bookrank', '0010_work_lang')]

    operations = [
        migrations.AddField(
            model_name='work',
            name='catalog_date',
            field=models.DateField(
                help_text='Date on which this work was added into the catalogue', null=True
            ),
        )
    ]