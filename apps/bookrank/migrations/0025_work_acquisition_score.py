# Generated by Django 2.2.24 on 2021-10-11 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('bookrank', '0024_adds_static_score_on_et')]

    operations = [
        migrations.AddField(
            model_name='work', name='acquisition_score', field=models.IntegerField(default=0)
        )
    ]