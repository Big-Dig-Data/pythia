from django.urls import path, include

from rest_framework_nested import routers

from . import views

app_name = "bookrank"


router = routers.SimpleRouter()
router.register(r'workset', views.WorkSetViewSet)

workset_router = routers.NestedSimpleRouter(router, r'workset', lookup='workset')
workset_router.register(r'works', views.WorkViewSet, basename='works')
workset_router.register(r'works_table', views.WorkDataTableViewSet, basename='works_table')
workset_router.register(r'works_growth_table', views.WorkGrowthTable, basename='works_growth_table')

explicit_topic_types = '|'.join(views.ExplicitTopicViewSet.topic_type_to_model.keys())
workset_router.register(
    fr'(?P<topic_type>{explicit_topic_types})',
    views.ExplicitTopicViewSet,
    basename='explicit_topics',
)
workset_router.register(
    fr'et_filters/(?P<topic_type>{explicit_topic_types})',
    views.ETFilterViewSet,
    basename='et_filters',
)

urlpatterns = [
    # REST API
    path('', include(router.urls)),
    path('', include(workset_router.urls)),
    path(
        'workset/<workset_uuid>/subjects/<root_node_uid>/',
        views.FullSubjectTreeView.as_view(),
        name='full_subject_tree',
    ),
]
