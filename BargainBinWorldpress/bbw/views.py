from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import *
# Create your views here.


class PostList(ListView):
    model = Post
    # ordering = '-publication_date'
    template_name = 'posts.html'
    context_object_name = 'posts'


class PostDetails(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


