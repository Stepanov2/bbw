from django_filters import FilterSet
from .models import Post


class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'author': ['exact'],
            'publication_date': ['exact', 'year__exact'],
            'category': ['exact'],
            'tags': ['exact'],
            'is_article': ['exact']
        }