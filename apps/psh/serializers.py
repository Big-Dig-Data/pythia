from rest_framework import serializers

from .models import PSHConcept


class PSHConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PSHConcept
        fields = ('pshid', 'name_cs', 'name_en')
