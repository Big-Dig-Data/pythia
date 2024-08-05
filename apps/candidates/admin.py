from django.contrib import admin

from candidates.models import Candidate, Agent, CandidatesSettings

admin.site.register(Agent)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):

    list_display = ['isbn', 'title', 'get_authors', 'get_lang']
    search_fields = ['isbn', 'title']
    readonly_fields = ['publisher', 'data_record']

    def get_authors(self, obj: Candidate) -> str:
        return '; '.join(obj.authors.values_list('name', flat=True))

    get_authors.short_description = 'Authors'

    def get_lang(self, obj: Candidate) -> str:
        return ', '.join(obj.languages.values_list('name', flat=True))

    get_lang.short_description = 'Language'


@admin.register(CandidatesSettings)
class CandidateSettingsAdmin(admin.ModelAdmin):

    list_display = ['pk', 'user', 'name', 'internal']
    readonly_fields = ['user']
