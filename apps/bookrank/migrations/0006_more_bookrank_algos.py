# Generated by Django 2.1.5 on 2019-03-12 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('bookrank', '0005_brmodel_algorithm')]

    operations = [
        migrations.AlterField(
            model_name='brmodel',
            name='algorithm',
            field=models.CharField(
                choices=[
                    ('fair', 'Fair'),
                    ('fair_tunable', 'Fair + tunable'),
                    ('charitable', 'Charitable'),
                ],
                default='charitable',
                max_length=32,
            ),
        )
    ]
