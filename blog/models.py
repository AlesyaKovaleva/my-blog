from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils import timezone


class Post(models.Model):
    author = models.ForeignKey('blog.Author', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст', blank=True, null=True)
    height_image = models.IntegerField(blank=True, null=True)
    width_image = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='posts', height_field='height_image',
                              width_field='width_image', blank=True, null=True, verbose_name='Фото')
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    votes = GenericRelation('blog.LikeDislike', related_query_name='posts')

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

    class Meta:
        permissions = (
            ('approve_comment', 'Can approve comments',),
        )

    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('Comment', related_name='replies',
                                       null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey('blog.Author', on_delete=models.DO_NOTHING)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
    votes = GenericRelation('blog.LikeDislike', related_query_name='comments')

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
    nickname = models.CharField(max_length=200, null=True, blank=True, verbose_name='Ник/Имя пользователя:')
    first_name = models.CharField(max_length=200, verbose_name='Имя:')
    last_name = models.CharField(max_length=200, verbose_name='Фамилия:')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения:')
    country = models.CharField(max_length=200, null=True, blank=True, verbose_name='Страна:')
    gender = models.CharField(max_length=1, null=True, blank=True, choices=GENDER_CHOICES, verbose_name='Пол:')
    author_info = models.TextField(null=True, blank=True, verbose_name='Информация:')
    avatar_height = models.IntegerField(blank=True, null=True)
    avatar_width = models.IntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars', height_field='avatar_height', width_field='avatar_width',
                               blank=True, default='avatars/default-user.png', verbose_name='Фото:')

    @property
    def can_approve(self):
        return self.user_id.has_perm('blog.approve_comment')

    @property
    def can_delete(self):
        return self.user_id.has_perm('blog.delete_comment')

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name,)


class LikeDislikeManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        # Забираем queryset с записями больше 0
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        # Забираем queryset с записями меньше 0
        return self.get_queryset().filter(vote__lt=0)

    def sum_rating(self):
        # Забираем суммарный рейтинг
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0

    def posts(self):
        return self.get_queryset().filter(content_type__model='posts').order_by('-posts__published_date')

    def comments(self):
        return self.get_queryset().filter(content_type__model='comment').order_by('-comments__created_date')


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Не нравится'),
        (LIKE, 'Нравится'),
    )

    vote = models.SmallIntegerField(verbose_name='Голос', choices=VOTES)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()
