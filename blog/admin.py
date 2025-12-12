from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import GamePost, Comment


@admin.register(GamePost)
class GamePostAdmin(admin.ModelAdmin):
    """
    Admin interface for GamePost model
    """
    list_display = ('title', 'game_name', 'author', 'category', 'status', 'created_on')
    list_filter = ('status', 'category', 'created_on')
    search_fields = ('title', 'game_name', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_on'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model
    """
    list_display = ('author', 'post', 'created_on', 'approved')
    list_filter = ('approved', 'created_on')
    search_fields = ('author__username', 'body')
    actions = ['approve_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
