from django import forms
from .models import GamePost, Comment
from django.utils.text import slugify


class GamePostForm(forms.ModelForm):
    """
    Form for creating and editing game posts
    """
    class Meta:
        model = GamePost
        fields = [
            'title', 'game_name', 'category', 
            'featured_image', 'excerpt', 'content', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'game_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter game name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'required': False  # ← Make it optional
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description (optional)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your post content here...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make featured_image not required
        self.fields['featured_image'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Auto-generate slug from title
        if not instance.slug:
            instance.slug = slugify(instance.title)
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to posts
    """
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            }),
        }
        labels = {
            'body': 'Comment'
        }