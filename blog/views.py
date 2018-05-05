from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post, Comment, User, Author
from .forms import PostForm, CommentForm, AuthorForm
from django.db.models import Q
from django.views import View
from django.contrib.auth import login, authenticate
from .forms import SignUpForm


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == "POST":
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
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
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
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)


@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_draft_list')


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
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
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)


def search(request):
    q = request.GET.get('q')
    if q:
        result_search = Post.objects.filter(
            Q(author__user_id__username__icontains=q) | Q(title__icontains=q) | Q(text__icontains=q)
        )
        return render(request, 'blog/search.html', {'result_search': result_search, 'q': q})
    return render(request, 'blog/search.html')


class AuthorView(View):
    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        form = AuthorForm(instance=author)
        return render(request, 'blog/author.html', context={'form': form})

    def post(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        form = AuthorForm(request.POST, request.FILES, instance=author)

        if form.is_valid():
            form.save()

        return render(request, 'blog/author.html', context={'form': form})


class AuthorInfoView(View):
    def get(self, request, pk):
        author = get_object_or_404(Author, pk=pk)
        gender = {k: v for (k, v) in Author.GENDER_CHOICES}

        if author.gender:
            author.gender = gender[author.gender]
        return render(request, 'blog/author_info.html', context={'author': author})


class SignUpView(View):
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            person = Author.objects.create(user_id=user)
            person.last_name = form.cleaned_data.get('last_name')
            person.first_name = form.cleaned_data.get('first_name')
            person.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('post_list')
        return render(request, 'blog/signup.html', {'form': form})

    def get(self, request):
        form = SignUpForm()
        return render(request, 'blog/signup.html', {'form': form})
