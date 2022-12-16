from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from posts.models import Comment, Follow, Group, Post
from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .permissions import AuthorOrReadOnlyAnon, ReadOnlyAll
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrReadOnlyAnon,)
    pagination_class = LimitOffsetPagination

    def create(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnlyAnon,)

    def get_queryset(self,):
        post_id = self.kwargs.get("post_id")
        new_queryset = Comment.objects.filter(post=post_id)
        return new_queryset

    def create(self, request, post_id):
        post_id = self.kwargs.get("post_id")
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user,
                            post=get_object_or_404(Post, id=post_id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (ReadOnlyAll,)


class FollowCreateListViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):

    serializer_class = FollowSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self,):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request):
        context = {'request': request}
        serializer = FollowSerializer(data=request.data, context=context)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            author = serializer.validated_data['following']
            if not Follow.objects.filter(user=user, following=author):
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
