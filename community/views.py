from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import (
    LoginRequiredMixin, UserPassesTestMixin
)
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.decorators import login_required
from django.views import View
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import GamePost, Comment
from .forms import GamePostForm, CommentForm


class PostListView(ListView):
    """
    Display list of all published game posts with search and filter functionality.
    """
    model = GamePost
    template_name = 'community/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        """Filter posts by status, search query, and category."""
        queryset = GamePost.objects.filter(status=1)

        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(game_name__icontains=query) |
                Q(content__icontains=query)
            )

        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        """Add search query and selected category to template context."""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class PostDetailView(DetailView):
    """
    Display a single post with its approved comments and like status.
    Also handles comment submission via POST request.
    """
    model = GamePost
    template_name = 'community/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        """Only show published posts."""
        return GamePost.objects.filter(status=1)

    def get_context_data(self, **kwargs):
        """Add comments, comment form, and like status to context."""
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.filter(approved=True)
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['liked'] = post.likes.filter(
                id=self.request.user.id
            ).exists()
        else:
            context['liked'] = False
        return context

    def post(self, request, *args, **kwargs):
        """Handle comment submission from authenticated users."""
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to comment.')
            return redirect('account_login')

        post = self.get_object()
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', slug=post.slug)

        return self.get(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new game post. Only authenticated users can create posts.
    """
    model = GamePost
    form_class = GamePostForm
    template_name = 'community/post_form.html'

    def form_valid(self, form):
        """Set the post author to the current user."""
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the newly created post."""
        return reverse('post_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        """Add action type to context for template rendering."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Create'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit an existing game post. Only the post author can edit.
    """
    model = GamePost
    form_class = GamePostForm
    template_name = 'community/post_form.html'

    def test_func(self):
        """Check if the current user is the post author."""
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        """Display error message if user tries to edit another user's post."""
        messages.error(self.request, 'You can only edit your own posts!')
        post = self.get_object()
        return redirect('post_detail', slug=post.slug)

    def form_valid(self, form):
        """Display success message on successful update."""
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the updated post."""
        return reverse('post_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        """Add action type to context for template rendering."""
        context = super().get_context_data(**kwargs)
        context['action'] = 'Edit'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a game post. Only the post author can delete.
    """
    model = GamePost
    template_name = 'community/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        """Check if the current user is the post author."""
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        """Display error message if user tries to delete another user's post."""
        messages.error(self.request, 'You can only delete your own posts!')
        post = self.get_object()
        return redirect('post_detail', slug=post.slug)

    def delete(self, request, *args, **kwargs):
        """Display success message on successful deletion."""
        messages.success(request, 'Post deleted successfully!')
        return super().delete(request, *args, **kwargs)


class PostLikeView(LoginRequiredMixin, View):
    """
    Toggle like/unlike on a post. Only authenticated users can like posts.
    """
    def post(self, request, slug):
        """Add or remove like from the post."""
        post = get_object_or_404(GamePost, slug=slug)

        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            messages.info(request, 'Post unliked!')
        else:
            post.likes.add(request.user)
            messages.success(request, 'Post liked!')

        return redirect('post_detail', slug=slug)


class MyPostsView(LoginRequiredMixin, ListView):
    """
    Display all posts created by the current user.
    """
    model = GamePost
    template_name = 'community/my_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        """Filter posts by current user."""
        return GamePost.objects.filter(author=self.request.user)


@login_required
def delete_comment(request, comment_id):
    """
    Delete a comment. Can be deleted by the comment author or staff members.
    
    Args:
        request: HTTP request object
        comment_id: ID of the comment to delete
        
    Returns:
        Redirect to post detail page with success or error message
    """
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if user is staff/admin or comment owner
    if request.user.is_staff or comment.author == request.user:
        post_slug = comment.post.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('post_detail', slug=post_slug)
    else:
        messages.error(
            request,
            "You don't have permission to delete this comment."
        )
        return redirect('post_detail', slug=comment.post.slug)
