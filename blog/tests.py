from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import GamePost, Comment


class GamePostModelTest(TestCase):
    """Test GamePost model"""

    def setUp(self):
        """Create test user and post"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = GamePost.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            game_name='Test Game',
            category='fps',
            content='Test content',
            excerpt='Test excerpt',
            status=1
        )

    def test_post_creation(self):
        """Test post is created correctly"""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(str(self.post), 'Test Post | by testuser')

    def test_post_likes(self):
        """Test like functionality"""
        self.post.likes.add(self.user)
        self.assertEqual(self.post.number_of_likes(), 1)


class PostViewsTest(TestCase):
    """Test views"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = GamePost.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            game_name='Test Game',
            category='fps',
            content='Test content',
            status=1
        )

    def test_post_list_view(self):
        """Test post list displays"""
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_detail_view(self):
        """Test post detail page"""
        response = self.client.get(
            reverse('post_detail', args=['test-post'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')

    def test_create_post_requires_login(self):
        """Test creating post requires authentication"""
        response = self.client.get(reverse('post_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
