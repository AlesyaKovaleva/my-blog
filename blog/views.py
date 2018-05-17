from django.db.models import Q, Count, Sum
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.utils.decorators import method_decorator

from .forms import SignUpForm, PostForm, CommentForm, AuthorForm
from .models import Post, Comment, Author, LikeDislike

import json

from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType


def post_list(request):
    if 'sorted_by_comment' in request.GET:
        posts = Post.objects.filter(published_date__lte=timezone.now())\
            .annotate(Count('comments')).order_by('-comments__count')
        sorted_by = 'comment'
    elif 'sorted_by_likes' in request.GET:
        posts = Post.objects.filter(published_date__lte=timezone.now()).annotate(Sum('votes__vote')).order_by(
            '-votes__vote__sum', '-published_date')
        sorted_by = 'likes'
    else:
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        sorted_by = 'date'

    return render(request, 'blog/post_list.html', {'posts': posts, 'sorted_by': sorted_by})


def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if post.published_date is None:
        if not request.user.is_authenticated:
            return render(request, 'blog/temp_errors/404.html', context={'error': 'Not found'})
        elif post.author != request.user.author:
            return render(request, 'blog/temp_errors/404.html', context={'error': 'You do not have permissions'},
                          status=403)

    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.author
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if post.author != request.user.author:
        return render(request, 'blog/temp_errors/404.html', context={'error': 'You do not have permissions'},
                      status=403)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.author
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True, author=request.user.author).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def post_publish(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if post.author != request.user.author:
        return render(request, 'blog/temp_errors/404.html', context={'error': 'You do not have permissions'},
                      status=403)

    post.publish()
    return redirect('post_list')


@login_required
def post_remove(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if post.author != request.user.author:
        return render(request, 'blog/temp_errors/404.html', context={'error': 'You do not have permissions'},
                      status=403)

    post.delete()
    return redirect('post_draft_list')


@login_required
def add_comment_to_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.author

            if 'parent_comment' in request.GET:
                parent_comment_id = request.GET['parent_comment']
                parent_comment = Comment.objects.get(pk=parent_comment_id)
                comment.parent_comment = parent_comment

            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})


@login_required
def comment_approve(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if not request.user.has_perm('blog.approve_comment'):
        return render(request, 'blog/temp_errors/404.html', context={'error': 'You do not have permissions'},
                      status=403)

    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist as e:
        return render(request, 'blog/temp_errors/404.html', context={'error': e})

    if request.user.has_perm('blog.delete_comment') or comment.author == request.user.author:
        comment.delete()
        return redirect('post_detail', pk=comment.post.pk)

    return render(request, 'blog/temp_errors/404.html', context={'error': 'You do not have permissions'},
                  status=403)


def search(request):
    q = request.GET.get('q')
    if q:
        result_search = Post.objects.filter(
            (Q(title__icontains=q) | Q(text__icontains=q))
            & Q(published_date__lte=timezone.now())
        )
        author_search = Author.objects.filter(
            Q(user_id__username__icontains=q) | Q(last_name__icontains=q) |
            Q(first_name__icontains=q) | Q(nickname__icontains=q)
        )
        return render(
            request, 'blog/search.html', {'q': q, 'result_search': result_search, 'author_search': author_search}
        )
    return render(request, 'blog/search.html')


class AuthorView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AuthorView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist as e:
            return render(request, 'blog/temp_errors/404.html', context={'error': e})

        if author.user_id != request.user:
            return render(request, 'blog/temp_errors/404.html', context={'error': 'Forbidden'}, status=403)

        form = AuthorForm(instance=author)
        return render(request, 'blog/author.html', context={'form': form})

    def post(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist as e:
            return render(request, 'blog/temp_errors/404.html', context={'error': e})

        form = AuthorForm(request.POST, request.FILES, instance=author)

        if form.is_valid():
            form.save()
            return redirect('author', pk=author.pk)

        return render(request, 'blog/author.html', context={'form': form})


class AuthorInfoView(View):
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist as e:
            return render(request, 'blog/temp_errors/404.html', context={'error': e})

        gender = {k: v for (k, v) in Author.GENDER_CHOICES}

        if author.gender:
            author.gender = gender[author.gender]

        posts = Post.objects.filter(author=author.pk, published_date__lte=timezone.now()).order_by('-published_date')
        return render(request, 'blog/author_info.html', context={'author': author, 'posts': posts})


class SignUpView(View):
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            author = Author.objects.create(user_id=user)
            author.last_name = form.cleaned_data.get('last_name')
            author.first_name = form.cleaned_data.get('first_name')
            author.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('post_list')
        return render(request, 'registration/signup.html', {'form': form})

    def get(self, request):
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})


class VotesView(View):
    model = None  # Модель данных - Статьи или Комментарии
    vote_type = None  # Тип комментария Like/Dislike

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        try:
            likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id,
                                                  user=request.user)
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
                result = True
            else:
                likedislike.delete()
                result = False
        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)
            result = True

        return HttpResponse(
            json.dumps({
                "result": result,
                "like_count": obj.votes.likes().count(),
                "dislike_count": obj.votes.dislikes().count(),
                "sum_rating": obj.votes.sum_rating()
            }),
            content_type="application/json"
        )
