from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from .filters import PostFilter
from .forms import PostForm, ArticleForm, NewsForm

# Create your views here.


class PostList(ListView):
    model = Post
    ordering = '-publication_date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['view_title'] = 'Новости и всякое'
        context['filterset'] = self.filterset
        return context


class SearchView(PostList):
    template_name = 'search.html'

    @property
    def is_there_a_request(self):
        return len(self.filterset.data)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Generating somewhat user-comprehensible title
        context['view_title'] = 'Искать по сайту: ' + str({key: value for (key, value)
                                                          in self.filterset.data.items() if value})[1:-1]
        context['filterset'] = self.filterset

        # No need to display posts if user haven't submitted the form yet
        context['show_results'] = self.is_there_a_request
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

# ============ begin forms ============


class PostCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'edit_post.html'
    # success_url = reverse_lazy('all_posts')


class PostUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'edit_post.html'
    # success_url = reverse_lazy('all_posts')


class PostDelete(DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('all_posts')


class ArticleCreate(PostCreate):
    form_class = ArticleForm


# class ArticleUpdate(PostUpdate):
#     form_class = ArticleForm
#

class NewsCreate(PostCreate):
    form_class = NewsForm


# class NewsUpdate(PostUpdate):
#     form_class = NewsForm


