from rest_framework import serializers

from bookrank.serializers import (
    LanguageSerializer,
    AuthorSerializer,
    PublisherSerializer,
    SubjectCategorySerializer,
    LanguageSimpleSerializer,
    AuthorSimpleSerializer,
    PublisherSimpleSerializer,
    SubjectCategorySimpleSerializer,
)
from .models import Candidate, Agent, CandidatesSettings


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('pk', 'name', 'email')


class CandidateSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    subjects = SubjectCategorySerializer(many=True, read_only=True)
    agent = AgentSerializer(read_only=True)
    liked = serializers.BooleanField(read_only=True)
    disliked = serializers.BooleanField(read_only=True)
    score = serializers.FloatField(read_only=True)

    class Meta:
        model = Candidate
        fields = (
            'pk',
            'isbn',
            'title',
            'authors',
            'publication_year',
            'languages',
            'publisher',
            'subjects',
            'abstract',
            'edition',
            'agent',
            'supplier',
            'availability',
            'price',
            'price_currency',
            'liked',
            'disliked',
            'score',
            'product_format',
        )


class CandidateExportSerializer(serializers.ModelSerializer):
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    languages = LanguageSimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    subjects = SubjectCategorySimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = ('isbn', 'title', 'authors', 'languages', 'publisher', 'subjects')


class CandidatesSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatesSettings
        fields = ('name', 'settings_obj', 'pk', 'internal')
