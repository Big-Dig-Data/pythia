# Generated by Django 2.1.5 on 2019-01-17 14:56

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='PSHConcept',
            fields=[
                (
                    'pshid',
                    models.CharField(max_length=8, primary_key=True, serialize=False, unique=True),
                ),
                ('name_cs', models.CharField(max_length=200)),
                ('name_en', models.CharField(max_length=200)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                (
                    'parent',
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='children',
                        to='psh.PSHConcept',
                    ),
                ),
            ],
            options={'abstract': False},
        )
    ]
