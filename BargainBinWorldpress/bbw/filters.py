from django_filters import FilterSet
from .models import Post


class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'author': ['exact'],
            'is_article': ['exact'],
            'title': ['contains'],
            'content': ['contains'],
            'publication_date': ['exact', 'year__exact'],
            'category': ['exact'],
            'tags': ['exact'],

        }
        