# Generated by Django 2.2.23 on 2021-07-16 01:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('candidates', '0006_reimplements_app_models')]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='publisher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='candidates',
                to='bookrank.Publisher',
            ),
        )
    ]
