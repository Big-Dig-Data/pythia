# Generated by Django 2.2.23 on 2021-05-20 09:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('bookrank', '0021_createdupdatedmixin'), ('hits', '0009_delete_topichit')]

    operations = [
        migrations.RemoveField(model_name='worktopic', name='topic'),
        migrations.RemoveField(model_name='worktopic', name='work'),
        migrations.RemoveField(model_name='work', name='topics'),
        migrations.DeleteModel(name='Topic'),
        migrations.DeleteModel(name='TopicSubType'),
        migrations.DeleteModel(name='WorkTopic'),
    ]