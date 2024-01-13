from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post

class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        test_user = User.objects.create_user(username='testuser', password='testpassword')
        Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=test_user,
            Content='This is a test post content.',
            excerpt='This is a test post excerpt.',
            status=1  # Published
        )

    def test_title_max_length(self):
        post = Post.objects.get(id=1)
        max_length = post._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_slug_max_length(self):
        post = Post.objects.get(id=1)
        max_length = post._meta.get_field('slug').max_length
        self.assertEqual(max_length, 200)

    def test_content(self):
        post = Post.objects.get(id=1)
        content = post.Content
        self.assertEqual(content, 'This is a test post content.')

    def test_excerpt_blank(self):
        post = Post.objects.get(id=1)
        excerpt = post.excerpt
        self.assertEqual(excerpt, 'This is a test post excerpt.')

    def test_created_on_auto_now_add(self):
        post = Post.objects.get(id=1)
        created_on = post.created_on
        self.assertIsNotNone(created_on)

    def test_number_of_likes(self):
        post = Post.objects.get(id=1)
        self.assertEqual(post.number_of_likes(), 0)  # Initially, no likes