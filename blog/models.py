from django.db import models
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    height_image = models.IntegerField(blank=True, null=True)
    width_image = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='posts', height_field='height_image', width_field='width_image', blank=True, null=True)
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
    post = models.ForeignKey('blog.Post', related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('Comment', related_name='replies', null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return self.text
