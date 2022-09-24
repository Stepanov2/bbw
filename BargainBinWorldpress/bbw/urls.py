from django.urls import path
from .views import *

urlpatterns = [
    path('', PostList.as_view()),
    path('news', NewsList.as_view()),
    path('articles', ArticleList.as_view()),
    path('posts/<int:pk>', PostDetails.as_view()),
]

