from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from core.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        our_user = authenticate(username=username,password=password)
        if our_user is not None:
            login(request,our_user)
            return redirect('/')
        messages.info(request,"OOP'S Login failed!!")
    return render(request,'accounts/login.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        conform_password = request.POST.get('conform_password', '').strip()

        if not username or not email or not password or not conform_password:
            messages.error(request, "All fields are required!")
            return redirect('user_register')
        
        if password == conform_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username Already Exists!!")
                return redirect('user_register')  
            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request,"Email Already Exists!!")
                    return redirect('user_register')  
                else:
                    user = User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                    #after login user come here
                    our_user = authenticate(username=username,password=password)
                    if our_user is not None:
                        login(request,user)
                        return redirect('/')
        else:
            messages.info(request,"Password mistmatch!!")
            return redirect('user_register')        

    return render(request,'accounts/register.html')

def user_logout(request):
    logout(request)
    return redirect('/')