from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey('blog.Author', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    height_image = models.IntegerField(blank=True, null=True)
    width_image = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='posts', height_field='height_image',
                              width_field='width_image', blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def root_comments(self):
        return self.comments.filter(parent_comment=None)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('Comment', related_name='replies',
                                       null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey('blog.Author', on_delete=models.DO_NOTHING)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text


class Author(models.Model):
    GENDER_CHOICES = (
        ('M', 'Мужской'),
        ('F', 'Женский'),
    )
    user_id = models.OneToOneField(User, related_name='author', null=True, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=200, null=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True, choices=GENDER_CHOICES)
    author_info = models.TextField(null=True, blank=True)
    avatar_height = models.IntegerField(blank=True, null=True)
    avatar_width = models.IntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', height_field='avatar_height',
                               width_field='avatar_width', blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name,)
