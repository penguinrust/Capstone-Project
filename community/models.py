from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Game categories
CATEGORY_CHOICES = [
    ('fps', 'First-Person Shooter'),
    ('rpg', 'Role-Playing Game'),
    ('moba', 'MOBA'),
    ('battle_royale', 'Battle Royale'),
    ('strategy', 'Strategy'),
    ('sports', 'Sports'),
    ('racing', 'Racing'),
    ('adventure', 'Adventure'),
    ('other', 'Other'),
]

STATUS_CHOICES = [
    (0, 'Draft'),
    (1, 'Published'),
]


class GamePost(models.Model):
    """
    Model for user-created gaming posts (reviews, tips, discussions)
    """
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='game_posts'
    )
    game_name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default='other'
    )
    featured_image = CloudinaryField('image', blank=True, null=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    likes = models.ManyToManyField(
        User, related_name='post_likes', blank=True
    )

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.title} | by {self.author}"

    def number_of_likes(self):
        return self.likes.count()


class Comment(models.Model):
    """
    Model for comments on game posts
    """
    post = models.ForeignKey(
        GamePost, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='commenter'
    )
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
