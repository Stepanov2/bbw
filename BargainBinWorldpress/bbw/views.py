from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import *
# Create your views here.


class PostList(ListView):
    model = Post
    # ordering = '-publication_date'
    template_name = 'posts.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['view_title'] = 'Новости и всякое'
        return context


class PostDetails(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class NewsList(PostList):
    queryset = Post.objects.filter(is_article=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['view_title'] = 'Только новости; никакого всякого.'
        return context


class ArticleList(PostList):
    queryset = Post.objects.filter(is_article=True)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['view_title'] = 'Только всякое; никаких новостей.'
        return context
