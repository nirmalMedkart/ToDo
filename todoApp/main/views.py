from django.contrib import messages
from django.shortcuts import redirect, render
from .models import *
from dateutil import parser
from django.contrib.auth import login, authenticate, logout
import datetime
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
# from django.views.decorators.cache import cache_control

# Create your views here.
@login_required(login_url="login")
def index(request):
    tasks = Task.objects.filter(members=request.user)
    for task in tasks:
        if task.start_date and task.end_date:
            Scheduled_task(task.id,task.start_date, task.end_date)
    context = {'tasks':tasks}
    return render(request,'index.html', context)

def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password1 = request.POST.get('password')
            password2 = request.POST.get('password2')

            if User.objects.filter(username=username).first():
                messages.error(request, "User is exist.")

            if User.objects.filter(email=email).first():
                messages.error(request, "User is exist.")
            
            if len(password1) < 6:
                messages.error(request, "Password length is aleast 6 characters.")

            if password1 != password2:
                messages.error(request, "Passwords are not same.")
            
            user = User.objects.create(username=username, email=email)
            user.set_password(password1)
            
            if user:
                user.save()
                messages.success(request, "Register successfully.")
    else:
        return redirect("home")
    return render(request, 'register.html')


def signin(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("home")
            else:
                messages.error(request,"Invalid username or password.")
    else:
        return redirect("home")
        
    return render(request, 'login.html')

@login_required(login_url="login")
def createTask(request):
    users = User.objects.all()
    if request.method == 'POST':
        user=request.user
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        members = request.POST.getlist('members')
        s_date = request.POST.get('s_date')
        e_date = request.POST.get('e_date')

        # print(members)
        # start_date =  datetime.datetime.combine(datetime.date(str(s_date)), datetime.time(str(s_time)))
        # end_date =  datetime.datetime.combine(datetime.date(str(e_date)), datetime.time(str(e_time)))
        task = Task.objects.create(
            user=user,
            title=title,
            desc=desc,
            )
        if s_date:
            task.start_date = s_date
            task.end_date = e_date
        users=[]
        for i in members:
            task.members.add(i)
            user = User.objects.get(id=i)
            users.append(user.email)
        task.save()
        if task:
            messages.success(request,"Task created successfully")  
        

            subject = 'New task'
            message = f'{title}\n{desc}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = users
            send_mail( subject, message, email_from, recipient_list )
            return redirect('home')

    context = {"users":users}
    return render(request,'createtask.html',context)

@login_required(login_url="login")
def removeTask(request, id):
    task = Task.objects.get(id=id)
    if request.user != task.user:
            messages.error(request,"You can not authorized for this operation")
            return redirect("home")
    task.delete()
    return redirect('home')

@login_required(login_url="login")
def editTask(request, id):
    users = User.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        start_date = request.POST.get('s_date')
        end_date = request.POST.get('e_date')
        members = request.POST.get('members')
        data = Task.objects.get(id=id)
        if request.user != data.user:
            messages.error(request,"You can not authorized for this operation")
            return redirect("home")
        if data.ended == True:
            messages.error(request,"Task was already ended.")
            return redirect("home")
        if title:
            data.title = title
        if desc:
            data.desc = desc
        if members:
            data.members.add(members)
            user = User.objects.get(id=members)
            subject = 'New task'
            message = f'{title}\n{desc}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list )

        if start_date:
            data.start_date = start_date
        if end_date:
            data.end_date = end_date
        data.save()
        messages.success(request,"Task is updated.")
        return redirect('home')
    context = {"users":users}
    return render(request,'updatetask.html',context)

@login_required(login_url="login")
def startTask(request, id):
    task = Task.objects.get(id=id)
    if request.user != task.user:
        messages.error(request,"You can not authorized for this operation")
        return redirect("home")
    task.started = True
    task.ended = False
    if task:
        task.save()
    return redirect('home')

@login_required(login_url="login")
def endTask(request, id):
    task = Task.objects.get(id=id)
    if request.user != task.user:
        messages.error(request,"You can not authorized for this operation")
        return redirect("home")
    task.ended = True
    task.started = False
    if task:
        task.save()
    return redirect('home')

@login_required(login_url="login")
def task(request, id):
    task = Task.objects.filter(id=id)
    context={"task":task}
    return render(request,'taskview.html',context)

def signout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect('login')



def Scheduled_task(id,s_date,e_date):
    task=Task.objects.get(id=id)
    s_date = str(s_date)
    e_date = str(e_date)
    if datetime.datetime.now().timestamp() >= parser.parse(s_date).timestamp():
        task.started = True
        task.ended = False
        task.save()
    
    if datetime.datetime.now().timestamp() >= parser.parse(e_date).timestamp():
        task.started = False
        task.ended = True
        task.save()