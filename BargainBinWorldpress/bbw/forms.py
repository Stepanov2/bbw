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

        #adding user to group
        group = Group.objects.get(pk=1)
        group.user_set.add(user)

        # saving user and creating linked site_user
        siteuser = SiteUser.objects.create(user=user, display_username=self.potential_username)


        return user


# class UserUpdateForm(UserChangeForm):
#     class Meta:
#         model = User
#         # fields = ['_all_']
#
#
# class BBWUserUpdateForm(forms.ModelForm):
#     class Meta:
#         model = SiteUser
#         fields = ['display_username']

# class MakeMeAnAuthor(forms.Form)
#     I_Agree

class BBWBecomeAuthor(forms.Form):
    i_consent = forms.BooleanField()
    group = Group.objects.get(pk=2)

    def __init__(self, *args, **kwargs):
        super(BBWBecomeAuthor, self).__init__(*args, **kwargs)
        self.fields['i_consent'] = forms.BooleanField(label='',
                                                      initial=False,
                                                      help_text='Отметьте сий чекбокс, дабы стать автором')

    # def clean(self):
    #     cleaned_data = super().clean()
    #     # checking if user clicked the validation checkbox
    #     # consent = cleaned_data['i_consent']
    #     # if not consent:
    #     #     raise ValidationError('Чтобы стать автором нужно жмакнуть чекбокс!')
    #
    #     # checking for username uniqueness
    #     self.group = Group.objects.get(pk=2)
    #     if self.group in self.user.groups.all():
    #         raise ValidationError('Ты уже и так - автор, дурашка!')
    #
    #     return cleaned_data
    #
    # def save(self, request):
    #     user = super(BBWBecomeAuthor, self).save(request)
    #     print('fuckfuckfuck')
    #     self.group.user_set.add(self.user)
