# Generated by Django 2.2.16 on 2020-10-23 12:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [('core', '0002_singletonvalue')]

    operations = [
        migrations.AlterField(
            model_name='singletonvalue',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        )
    ]