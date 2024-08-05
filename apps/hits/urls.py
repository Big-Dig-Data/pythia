from django.urls import path, include

from . import views

app_name = "hits"

urlpatterns = [
    # workhit views
    path(
        'workhit/stats/<uuid:workset_uuid>/lang',
        views.LangWorkStatsView.as_view(),
        name='lang-work-stats',
    ),
    path(
        'workhit/stats/<uuid:workset_uuid>/owner_institution',
        views.OwnerInstitutionWorkStatsView.as_view(),
        name='owner-institution-work-stats',
    ),
    path(
        'workhit/stats/<uuid:workset_uuid>/work_category',
        views.WorkCategoryWorkStatsView.as_view(),
        name='work-category-work-stats',
    ),
    path(
        'workhit/stats/<uuid:workset_uuid>/<topic_type>',
        views.ExplicitTopicsHitStatsView.as_view(),
        name='explicit-topic-hit-stats',
    ),
    # time data
    path(
        'workhit/time-stats/<work_id>/',
        views.WorkHitsInTimeStatsView.as_view(),
        name='workhits-in-time',
    ),
    path(
        'workhit/topic-time-stats/',
        views.ExplicitTopicsInTimeStatsView.as_view(),
        name='explicit-topic-in-time-stats',
    ),
    # total hits
    path('workhit/hits/<work_id>/', views.WorkHitsWorkDetailView.as_view(), name='work-hits'),
    # histogram
    path(
        'workhit/histogram/<uuid:workset_uuid>/<topic_type>',
        views.ExplicitTopicsHitHistogramView.as_view(),
        name='explicit-topic-hit-histogram',
    ),
    # top works
    path(
        'workhit/works/<uuid:workset_uuid>/top_works',
        views.ImportantWorksView.as_view(),
        name='top-works',
    ),
    # top works per topic type with filter
    path(
        'workhit/works/<uuid:workset_uuid>/<topic_type>',
        views.ExplicitTopicsImportantWorksView.as_view(),
        name='explicit-topic-top-works',
    ),
]
