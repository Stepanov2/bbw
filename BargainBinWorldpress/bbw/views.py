from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, SiteUser
from .filters import PostFilter
from .forms import PostForm, ArticleForm, NewsForm, BBWBecomeAuthor  # UserUpdateForm, BBWUserUpdateForm


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
    template_name = 'posts.html'
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


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('bbw.add_post')
    permission_denied_message = 'Вы не автор - уйдите отседова!'  # не работаит:'-(((
    form_class = PostForm
    model = Post
    template_name = 'edit_post.html'
    # success_url = reverse_lazy('all_posts')


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('bbw.change_post')
    permission_denied_message = 'Вы не автор - уйдите отседова!'
    form_class = PostForm
    model = Post
    template_name = 'edit_post.html'
    # success_url = reverse_lazy('all_posts')


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('bbw.delete_post')
    permission_denied_message = 'Вы не автор - уйдите отседова!'
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('all_posts')


class ArticleCreate(PostCreate):
    form_class = ArticleForm


class NewsCreate(PostCreate):
    form_class = NewsForm


@login_required
def become_author(request):
    form = BBWBecomeAuthor(request.POST)
    authors = Group.objects.get(pk=2)
    fail_message = ''  # also works as success message =)
    if authors in request.user.groups.all():
        fail_message = 'Ты и так уже автор, дуражка! '

    elif request.POST:
        if not request.POST['i_consent']:
            fail_message = 'Ты не нажал галочку, дуражка!'
        else:
            request.user.groups.add(authors)
            fail_message = 'Поздравляем, теперь вы - автор! Перо покупаете за свой счёт!'

    return render(request, 'become_author.html', context={'form': form, 'fail_message': fail_message})


# class UserSettings(LoginRequiredMixin, UpdateView):
#     template_name = 'profile.html'
#     context_object_name = 'user'
#     model = SiteUser
#     form_class = BBWUserUpdateForm
#
#     def get_success_url(self):
#         return '/profile/' + str(self.get_object().pk)
#
#     def get_context_data(self, **kwargs):
#         context = super(UserSettings, self).get_context_data(**kwargs)
#         context['user_form'] = UserUpdateForm(instance=self.request.user)
#         return context
