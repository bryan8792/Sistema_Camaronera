
from django.urls import path
from .views.login import *
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('', loginFormView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]