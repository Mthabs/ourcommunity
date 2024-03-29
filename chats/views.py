from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Post, Comment
from .forms import CommentForm, PostForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 6


class UserPostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=1).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 6

    def get_queryset(self):
        qs = super().get_queryset() 
        return qs.filter(author=self.request.user)



class PostDetail(View):

    def get(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if request.user.is_authenticated and post.likes.filter(id=request.user.id).exists():
            liked = True

        # Check if the commented query parameter exists
        commented = 'commented' in request.GET
        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "liked": liked,
                "comment_form": CommentForm(),
                "commented": commented
            },
        )

    @method_decorator(login_required)
    def post(self, request, slug, *args, **kwargs):
        queryset = Post.objects.filter(status=1)
        post = get_object_or_404(queryset, slug=slug)
        comments = post.comments.filter(approved=True).order_by("-created_on")
        liked = False
        if post.likes.filter(id=request.user.id).exists():
            liked = True

        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user.username
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(reverse('post_detail', kwargs={'slug': slug}) + '?commented=true')
        else:
            messages.error(request, "Invalid input. Please correct the errors below.")
            # Access form errors and handle them as needed
            for field, errors in comment_form.errors.items():
                for error in errors:
                    # You can customize the error handling here
                    messages.error(request, f"{field}: {error}")

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "comment_form": comment_form,
                "liked": liked
            },
        )

class PostLike(View):

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug]))

class CommentEdit(View):
    template_name = 'comment_edit.html'
    form_class = CommentForm

    @method_decorator(login_required)
    def get(self, request, post_slug, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, name=request.user.username)
        form = self.form_class(instance=comment)
        return render(request, self.template_name, {'form': form, 'comment': comment})

    @method_decorator(login_required)
    def post(self, request, post_slug, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, name=request.user.username)
        form = self.form_class(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully.")
            return redirect(reverse('post_detail', kwargs={'slug': post_slug}))
        return render(request, self.template_name, {'form': form, 'comment': comment})

class CommentDelete(View):
    template_name = 'comment_delete.html'

    @method_decorator(login_required)
    def get(self, request, post_slug, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, name=request.user.username)
        return render(request, self.template_name, {'comment': comment})

    @method_decorator(login_required)
    def post(self, request, post_slug, comment_id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=comment_id, post__slug=post_slug, name=request.user.username)
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect(reverse('post_detail', kwargs={'slug': post_slug}))


class PostCreate(View):
    template_name = 'post_add.html'
    form_class = PostForm

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  
            post.save()
            return HttpResponseRedirect(reverse_lazy('home'))
        return render(request, self.template_name, {'form': form})

class PostEdit(View):
    template_name = 'post_edit.html'
    form_class = PostForm

    @method_decorator(login_required)
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        # Check if the user has the permission to edit the post
        if request.user == post.author:
            form = self.form_class(instance=post)
            return render(request, self.template_name, {'form': form, 'post': post})
        else:
            messages.error(request, "You don't have permission to edit this post.")
            return redirect(reverse('post_detail', kwargs={'slug': slug}))

    @method_decorator(login_required)
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        # Check if the user has the permission to edit the post
        if request.user == post.author:
            form = self.form_class(request.POST, request.FILES, instance=post)
            if form.is_valid():
                form.save()
                messages.success(request, "Post updated successfully.")
                return redirect(reverse('post_detail', kwargs={'slug': slug}))
            return render(request, self.template_name, {'form': form, 'post': post})
        else:
            messages.error(request, "You don't have permission to edit this post.")
            return redirect(reverse('post_detail', kwargs={'slug': slug}))

class PostDelete(View):
    template_name = 'post_delete.html'

    @method_decorator(login_required)
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        # Check if the user has the permission to delete the post
        if request.user == post.author:
            return render(request, self.template_name, {'post': post})
        else:
            messages.error(request, "You don't have permission to delete this post.")
            return redirect(reverse('post_detail', kwargs={'slug': slug}))

    @method_decorator(login_required)
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        # Check if the user has the permission to delete the post
        if request.user == post.author:
            post.delete()
            messages.success(request, "Post deleted successfully.")
            return redirect(reverse('home'))
        else:
            messages.error(request, "You don't have permission to delete this post.")
            return redirect(reverse('post_detail', kwargs={'slug': slug}))