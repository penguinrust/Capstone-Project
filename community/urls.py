from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.PostListView.as_view(),
        name='post_list'
    ),
    path(
        'post/<slug:slug>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='post_create'),
    path(
        'post/<slug:slug>/edit/',
        views.PostUpdateView.as_view(),
        name='post_edit'
    ),
    path(
        'post/<slug:slug>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),
    path(
        'post/<slug:slug>/like/',
        views.PostLikeView.as_view(),
        name='post_like'
    ),
    path(
        'my-posts/',
        views.MyPostsView.as_view(),
        name='my_posts'
    ),
    # Add this new URL for deleting comments
    path(
        'comment/delete/<int:comment_id>/',
        views.delete_comment,
        name='delete_comment'
    ),
]
