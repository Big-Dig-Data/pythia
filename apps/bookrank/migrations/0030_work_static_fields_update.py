# Generated by Django 3.2.8 on 2022-05-27 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('bookrank', '0029_work_acquisition_date')]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='absolute_growth',
            field=models.IntegerField(
                default=0, help_text='Difference between `score_past_yr` and `score_yr_b4`'
            ),
        ),
        migrations.AlterField(
            model_name='work',
            name='relative_growth',
            field=models.FloatField(
                blank=True, help_text='`absolute_growth` divided by `score_yr_b4`', null=True
            ),
        ),
        migrations.AlterField(
            model_name='work',
            name='score_past_yr',
            field=models.IntegerField(default=0, help_text='Sum of hits for one year from now'),
        ),
        migrations.AlterField(
            model_name='work',
            name='score_yr_b4',
            field=models.IntegerField(
                default=0, help_text='Sum of hits between two years and one year from now'
            ),
        ),
    ]