from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Post

def index(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    
    posts = Post.objects.all().order_by('-created_at')
    return render(request, "app/home.html", {'posts': posts})


def addpost(request):
    if not request.user.is_authenticated:
        return redirect("/login")
            
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        
        if title and body:
            post = Post.objects.create(
                user=request.user,
                title=title,
                body=body
            )
            post.save()
    
    return redirect('/')
        
def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    
    context = {
        "error": ""
    }
    if request.method == 'POST':
        if request.POST.get('username', False) and request.POST.get('password', False):
            if request.POST['username'].strip() != "" and request.POST['password'].strip() != "":
                try:
                    user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
                    if user is not None:
                        auth_login(request, user)
                        return redirect("/")
                    else:
                        context['error'] = "The username or password you entered are incorrect"

                except Exception as e:
                    context['error'] = e
            else:
                context['error'] = "Please enter all the fields"
        else:
            context['error'] = "Please enter all the fields"
    return render(request, 'auth/login.html', context)

def signup(request):
    if request.user.is_authenticated:
        return redirect("/")
    
    context = {
        "error": ""
    }

    if request.method == 'POST':
        if request.POST.get('email', False) and request.POST.get('username', False) and request.POST.get('password', False):
            if request.POST['email'].strip() != "" and request.POST['username'].strip() != "" and request.POST['password'].strip() != "":
                try:
                    validate_email(request.POST['email'].strip())
                except ValidationError as e:
                    context['error'] = "Email is not valid"
                else:
                    try:
                        if len(User.objects.filter(username = request.POST['username'])) > 0:
                            context['error'] = "Username already exists"
                        else:
                            if len(User.objects.filter(email = request.POST['email'])) > 0:
                                context['error'] = "Email already exists"
                            else:
                                user = User.objects.create_user(request.POST['username'], request.POST['email'].strip(), request.POST['password'])
                                user.save()
                                auth_login(request, user)
                                return redirect("/")
                    except Exception as e:
                        context['error'] = e
            else:
                context['error'] = "Please enter all the fields"
        else:
            context['error'] = "Please enter all the fields"

    return render(request, "auth/signup.html", context)






def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)

    return redirect("/login")