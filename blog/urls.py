from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

from django.contrib.auth.decorators import login_required
from .models import LikeDislike, Post, Comment

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('drafts/', views.post_draft_list, name='post_draft_list'),
    path('post/<int:pk>/publish/', views.post_publish, name='post_publish'),
    path('post/<int:pk>/remove/', views.post_remove, name='post_remove'),
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:pk>/approve/', views.comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', views.comment_remove, name='comment_remove'),
    path('search/', views.search, name='search'),
    path('author/<int:pk>/', views.AuthorView.as_view(), name='author'),
    path('author_info/<int:pk>/', views.AuthorInfoView.as_view(), name='author_info'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path(
        'api/post/<int:pk>/like/',
        login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.LIKE)),
        name='post_like'
    ),
    path(
        'api/post/<int:pk>/dislike/',
        login_required(views.VotesView.as_view(model=Post, vote_type=LikeDislike.DISLIKE)),
        name='post_dislike'
         ),
    path(
        'api/comment/<int:pk>/like/',
        login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.LIKE)),
        name='comment_like'
    ),
    path(
        'api/comment/<int:pk>/dislike/',
        login_required(views.VotesView.as_view(model=Comment, vote_type=LikeDislike.DISLIKE)),
        name='comment_dislike'
    ),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
