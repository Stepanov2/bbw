from django.urls import path
from .views import MyLoginView, MyLogoutView, BaseRegisterView

urlpatterns = [
    path('login/',
         MyLoginView.as_view(),
         name='login'),
    path('logout/',
         MyLogoutView.as_view(),
         name='logout'),
    path('signup/',
         BaseRegisterView.as_view(),
         name='signup'),
]