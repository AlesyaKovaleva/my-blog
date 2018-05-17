from django.test import TestCase
from mock import patch, Mock
from django.utils.timezone import now

from .models import Author, Post


class PostTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create()

    def test_publish(self):
        post = Post.objects.create(title='This is a Post', author=self.author)
        self.assertIsNone(post.published_date)
        post.publish()
        self.assertNotEqual(post.published_date, None)
        self.assertGreater(now(), post.published_date)

    def test_publish_mocked(self):
        post = Post.objects.create(title='This is a Post', author=self.author)
        self.assertIsNone(post.published_date)
        expected_date = now()
        # мокаем метод который вызывается при публикации поста
        # чтобы он нам выдавал наше значение определенное выше
        with patch('blog.models.timezone.now', new=Mock(return_value=expected_date)):
            post.publish()
        self.assertEqual(post.published_date, expected_date)
