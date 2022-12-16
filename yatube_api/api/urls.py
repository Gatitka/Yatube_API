from api.views import (CommentViewSet, FollowCreateListViewSet, GroupViewSet,
                       PostViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('v1/posts', PostViewSet, basename='posts')
v1_router.register('v1/groups', GroupViewSet, basename='groups')
v1_router.register(r'v1/posts/(?P<post_id>\d+)/comments',
                   CommentViewSet,
                   basename='comments')
v1_router.register('v1/follow', FollowCreateListViewSet, basename='groups')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
