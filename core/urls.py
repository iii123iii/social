from django.urls import path
from . import views

urlpatterns = [

    #auth
    path("login", views.login, name="login"),
    path("signup", views.signup, name="signup"),
    path("logout", views.logout, name="signup"),
    
    #core
    path("", views.index, name="index"),
    path("addpost", views.addpost, name="Add post"),
    path("account", views.index, name="account"),



    
    path("beta", views.beta, name="beta"),
]