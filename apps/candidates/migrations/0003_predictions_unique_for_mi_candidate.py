# Generated by Django 2.1.7 on 2019-03-13 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookrank', '0006_more_bookrank_algos'),
        ('candidates', '0002_add_candidateprediction'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='candidateprediction', unique_together={('mi', 'candidate')}
        )
    ]