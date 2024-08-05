from rest_framework import serializers
from rest_framework.fields import FloatField, IntegerField, CharField

from .models import (
    Work,
    WorkCategory,
    WorkSet,
    Publisher,
    Author,
    Language,
    OwnerInstitution,
    SubjectCategory,
)


class WorkSetSerializer(serializers.ModelSerializer):

    work_count = serializers.IntegerField(read_only=True, help_text="Number of works in workset")

    class Meta:
        model = WorkSet
        fields = ('uuid', 'name', 'description', 'work_count')


class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCategory
        fields = ('pk', 'name')


class WorkSimpleSerializer(serializers.ModelSerializer):

    category = WorkCategorySerializer(read_only=True)

    class Meta:
        model = Work
        fields = ('pk', 'uid', 'name', 'category')


class WorkSimpleScoreSerializer(WorkSimpleSerializer):

    score = IntegerField(read_only=True)

    class Meta(WorkSimpleSerializer.Meta):
        fields = WorkSimpleSerializer.Meta.fields + ('score',)


class ExplicitTopicSerializer(serializers.ModelSerializer):

    similarity = FloatField(read_only=True)  # available when doing a search
    score = IntegerField(read_only=True)  # available when doing a search
    score_past_yr = IntegerField(read_only=True)
    score_yr_b4 = IntegerField(read_only=True)
    absolute_growth = IntegerField(read_only=True)
    relative_growth = FloatField(read_only=True)

    class Meta:
        fields = (
            'pk',
            'name',
            'work_set',
            'score',
            'similarity',
            'normalized_score',
            'score_past_yr',
            'score_yr_b4',
            'absolute_growth',
            'relative_growth',
        )


class PublisherSerializer(ExplicitTopicSerializer):
    class Meta(ExplicitTopicSerializer.Meta):
        model = Publisher


class AuthorSerializer(ExplicitTopicSerializer):
    class Meta(ExplicitTopicSerializer.Meta):
        model = Author


class SubjectCategorySerializer(ExplicitTopicSerializer):
    root_node = CharField(read_only=True)

    class Meta(ExplicitTopicSerializer.Meta):
        model = SubjectCategory
        fields = ('pk', 'name', 'work_set', 'score', 'similarity', 'root_node', 'normalized_score')


class OwnerIntitutionSerializer(ExplicitTopicSerializer):
    class Meta(ExplicitTopicSerializer.Meta):
        model = OwnerInstitution


class LanguageSerializer(ExplicitTopicSerializer):
    class Meta(ExplicitTopicSerializer.Meta):
        model = Language


class WorkSerializer(serializers.ModelSerializer):

    category = WorkCategorySerializer(read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    similarity = FloatField(read_only=True)
    score = IntegerField(read_only=True)

    class Meta:
        model = Work
        fields = (
            'pk',
            'uid',
            'name',
            'category',
            'lang',
            'owner_institution',
            'start_yop',
            'end_yop',
            'authors',
            'similarity',
            'score',
        )


class WorkDetailedSerializer(serializers.ModelSerializer):

    category = WorkCategorySerializer(read_only=True)
    publishers = PublisherSerializer(many=True, read_only=True)
    authors = AuthorSerializer(many=True, read_only=True)
    subject_categories = SubjectCategorySerializer(many=True, read_only=True)
    lang = LanguageSerializer(read_only=True)
    owner_institution = OwnerIntitutionSerializer(read_only=True)
    isbn = serializers.ListField(child=serializers.CharField())
    score = IntegerField(read_only=True)

    class Meta:
        model = Work
        fields = (
            'pk',
            'uid',
            'isbn',
            'name',
            'category',
            'lang',
            'owner_institution',
            'start_yop',
            'end_yop',
            'publishers',
            'authors',
            'subject_categories',
            'cover_image_url',
            'abstract',
            'score',
            'catalog_date',
            'acquisition_score',
            'acquisition_date',
        )


class ETGrowthSerializer(serializers.ModelSerializer):
    score_past_yr = IntegerField(read_only=True)
    score_yr_b4 = IntegerField(read_only=True)
    absolute_growth = IntegerField(read_only=True)
    relative_growth = FloatField(read_only=True)

    class Meta:
        fields = (
            'pk',
            'name',
            'score_past_yr',
            'score_yr_b4',
            'absolute_growth',
            'relative_growth',
        )


class AuthorGrowthSerializer(ETGrowthSerializer):
    class Meta(ETGrowthSerializer.Meta):
        model = Author


class PublisherGrowthSerializer(ETGrowthSerializer):
    class Meta(ETGrowthSerializer.Meta):
        model = Publisher


class SubjectCategoryGrowthSerializer(ETGrowthSerializer):
    class Meta(ETGrowthSerializer.Meta):
        model = SubjectCategory


class LanguageGrowthSerializer(ETGrowthSerializer):
    class Meta(ETGrowthSerializer.Meta):
        model = Language


class WorkGrowthSerializer(serializers.ModelSerializer):
    publishers = PublisherGrowthSerializer(many=True, read_only=True)
    authors = AuthorGrowthSerializer(many=True, read_only=True)
    subject_categories = SubjectCategoryGrowthSerializer(many=True, read_only=True)
    lang = LanguageGrowthSerializer(read_only=True)
    score_past_yr = IntegerField(read_only=True)
    score_yr_b4 = IntegerField(read_only=True)
    absolute_growth = IntegerField(read_only=True)
    relative_growth = FloatField(read_only=True)

    class Meta:
        model = Work
        fields = (
            'pk',
            'name',
            'lang',
            'publishers',
            'authors',
            'subject_categories',
            'score_past_yr',
            'score_yr_b4',
            'absolute_growth',
            'relative_growth',
        )


class ETSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name',)


class LanguageSimpleSerializer(ETSimpleSerializer):
    class Meta(ETSimpleSerializer.Meta):
        model = Language


class PublisherSimpleSerializer(ETSimpleSerializer):
    class Meta(ETSimpleSerializer.Meta):
        model = Publisher


class AuthorSimpleSerializer(ETSimpleSerializer):
    class Meta(ETSimpleSerializer.Meta):
        model = Author


class SubjectCategorySimpleSerializer(ETSimpleSerializer):
    class Meta(ETSimpleSerializer.Meta):
        model = SubjectCategory
