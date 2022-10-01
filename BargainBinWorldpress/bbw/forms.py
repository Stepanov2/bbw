from django import forms
from django.core.exceptions import ValidationError
from .models import Post
from django.forms import Textarea, SplitDateTimeWidget, SelectDateWidget, SplitDateTimeField, HiddenInput


class PostForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['publication_date'] = SplitDateTimeField()

    class Meta:
        model = Post
        fields = ['title', 'is_article', 'category', 'author', 'content', 'tags', 'published', 'publication_date']
        widgets = {'publication_date': SelectDateWidget}
            # 'publication_date': SplitDateTimeWidget(date_attrs={"type": "date"}, time_attrs={"type": "time"})

    def clean(self):

        cleaned_data = super().clean()

        if not cleaned_data['tags']:
            raise ValidationError('Выберите хотя бы один тег.')
        return cleaned_data


class ArticleForm(PostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_article'].widget = HiddenInput(attrs={'value': True})
        # self.fields['publication_date'] = SplitDateTimeField()


class NewsForm(PostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_article'].widget = HiddenInput(attrs={'value': False})
