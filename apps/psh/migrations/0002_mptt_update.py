# Generated by Django 2.2.6 on 2019-10-08 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('psh', '0001_initial')]

    operations = [
        migrations.AlterField(
            model_name='pshconcept', name='level', field=models.PositiveIntegerField(editable=False)
        ),
        migrations.AlterField(
            model_name='pshconcept', name='lft', field=models.PositiveIntegerField(editable=False)
        ),
        migrations.AlterField(
            model_name='pshconcept', name='rght', field=models.PositiveIntegerField(editable=False)
        ),
    ]
