from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.utils import timezone
from .models import Post
from django.core.paginator import Paginator
import random
import string

def index(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    
    posts_per_page = 10
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, posts_per_page)
    page = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page)
    except:
        posts = paginator.page(1)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        posts_data = [{
            'username': post.user.username,
            'title': post.title,
            'body': post.body,
            'created_at': post.created_at.strftime("%B %d, %H:%M")
        } for post in posts]
        return JsonResponse({
            'posts': posts_data,
            'has_next': posts.has_next(),
            'total_pages': paginator.num_pages
        })
    
    return render(request, "app/home.html", {
        'posts': posts,
        'page_obj': posts,
    })


def addpost(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        
        if not title or not body:
            return JsonResponse({'success': False, 'error': 'Please fill in all fields'})
            
        if len(title) > 200:
            return JsonResponse({'success': False, 'error': 'Title must be less than 200 characters'})
            
        if len(body) > 10000:
            return JsonResponse({'success': False, 'error': 'Content must be less than 10000 characters'})
        
        try:
            post = Post.objects.create(
                user=request.user,
                title=title,
                body=body
            )
            post.save()
            
            return JsonResponse({
                'success': True,
                'username': request.user.username,
                'title': title,
                'body': body,
                'created_at': post.created_at.strftime("%B %d, %H:%M")
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An error occurred while creating the post'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
        
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
                    user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
                    if user != None:
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



def beta(request):

    def generate_random_string(length):
        letters = string.ascii_letters + string.digits + " "
        return ''.join(random.choice(letters) for _ in range(length))

    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'Not authorized'}, status=403)
        
    try:
        for _ in range(1000):
            title = generate_random_string(random.randint(10, 50))
            body = generate_random_string(random.randint(100, 500))
            
            post = Post.objects.create(
                user=request.user,
                title=title,
                body=body
            )
            post.save()
            
        return JsonResponse({'success': True, 'message': '1000 posts created successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)