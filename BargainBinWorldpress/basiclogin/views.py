from django.shortcuts import render

# Create your views here.

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .forms import RegisterForm


class MyLoginView(LoginView):

    template_name = 'login.html'
    redirect_authenticated_user = True
    redirect_field_name = 'next'


class BaseRegisterView(CreateView):
    model = User
    form_class = RegisterForm
    success_url = '/'
    template_name = 'signup.html'


class MyLogoutView(LogoutView):

    template_name = 'logout.html'
