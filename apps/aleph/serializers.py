from rest_framework import serializers

from .models import AlephEntry


class AlephEntrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AlephEntry
        fields = ('uid', 'raw_data')
