from django.urls import path
from .views import *




urlpatterns = [
    path('', PostList.as_view(), name='all_posts'),
    path('search', SearchView.as_view(), name='search_posts'),
    path('posts', PostList.as_view()),
    path('news', NewsList.as_view(), name='news_posts'),
    path('articles', ArticleList.as_view(), name='non_news_posts'),
    path('posts/<int:pk>', PostDetails.as_view(), name='show_post'),
    path('posts/new', PostCreate.as_view(), name='new_post'),
    path('posts/new_article', ArticleCreate.as_view(), name='new_article'),
    path('posts/new_news', NewsCreate.as_view(), name='new_news'),
    path('posts/edit/<int:pk>', PostUpdate.as_view(), name='edit_post'),
    path('posts/delete/<int:pk>', PostDelete.as_view(), name='delete_post'),
    path('become_author', become_author, name='become_author'),
    path('subscriptions', EmailSubscriptionsView.as_view(), name='subscriptions')
]

