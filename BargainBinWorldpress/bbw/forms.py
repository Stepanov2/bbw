from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from .models import Post, SiteUser
from django.forms import Textarea, SplitDateTimeWidget, SelectDateWidget, SplitDateTimeField, HiddenInput
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User, Group



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


class BBWSignupForm(SignupForm):
    display_username = forms.CharField(max_length=100, label="Имя пользователя, отображаемое на сайте", required=True)
    potential_username = ''

    def clean(self):

        cleaned_data = super().clean()
        self.potential_username = cleaned_data['display_username']

        # checking for username uniqueness
        if SiteUser.objects.filter(display_username=self.potential_username):
            raise ValidationError('Пользователь с таким ником уже существует.')

        return cleaned_data

    def save(self, request):

        user = super(BBWSignupForm, self).save(request)
        print('saving_saving_saving')
        #adding user to group
        group = Group.objects.get(pk=1)
        group.user_set.add(user)

        # saving user and creating linked site_user
        siteuser = SiteUser.objects.create(user=user, display_username=self.potential_username)

        return user


class BBWBecomeAuthor(forms.Form):
    i_consent = forms.BooleanField()
    group = Group.objects.get(pk=2)

    def __init__(self, *args, **kwargs):
        super(BBWBecomeAuthor, self).__init__(*args, **kwargs)
        self.fields['i_consent'] = forms.BooleanField(label='',
                                                      initial=False,
                                                      help_text='Отметьте сий чекбокс, дабы стать автором')


