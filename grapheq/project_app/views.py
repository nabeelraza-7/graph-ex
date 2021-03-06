import os
import numpy as np
# import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage

from .Solution import Solution
from script import predict_ex

# adding styles
plt.style.use('seaborn-darkgrid')
plt.rc('figure', autolayout=True)
plt.rc('axes', labelweight='bold', labelsize='large', titleweight='bold', titlesize=18, titlepad=10)

def home(request):
    return render(request, 'project_app/index.html')

def about_page(request):
    return render(request, "project_app/about_page.html")

def plot(request):
    equations_from_fields = request.POST.getlist('equation')
    
    # deleting plot.png if already exists 
    if os.path.exists('static/plot.png'):
        os.remove("static/plot.png")
    if len(equations_from_fields) != 0:
        plot_eq_fields(equations_from_fields)
        title = ""
        for i in equations_from_fields:
            if i == "": continue
            title += i + ", "
        context = {"title": title}
        return show_results(request, context)
    elif len(request.FILES) != 0 :
        uploaded_file = request.FILES['image_file']
        fs = FileSystemStorage()
        # deleting image.jpeg if already exists
        if os.path.exists('media/image.jpeg'):
            os.remove("media/image.jpeg")
        fs.save("image.jpeg", uploaded_file)
        detected = plot_eq_image()
        print(detected)
        context = {"title": detected}
        return show_results(request, context)
    return render(request, 'project_app/plot.html')

    

def plot_eq_fields(equations_from_fields):
    for i in equations_from_fields:
        if i == "": continue
        string = i
        plot = []
        for j in range(-500, 501):
            s = Solution(string.replace("x", str(j)))
            try:
                temp = np.float32(s.solve())
                plot.append(temp)
            except Exception:
                plot.append(np.nan)
        # plot = pd.DataFrame({"result": plot})
        plt.plot(range(-500, 501), plot)
        plt.xticks([-600, -400, -200, 0, 200, 400, 600])
        plt.savefig("static/plot.png", edgecolor="none")
    plt.close()

def plot_eq_image():
    text =predict_ex()
    plot = []
    for j in range(-500, 501):
        s = Solution(text.replace("x", "("+str(j)+")"))
        try:
            temp = np.float32(s.solve())
            plot.append(temp)
        except Exception:
            plot.append(np.nan)
    plt.plot(range(-500, 501), plot)
    plt.xticks([-600, -400, -200, 0, 200, 400, 600])
    plt.savefig("static/plot.png", edgecolor="none")
    plt.close()
    return text

def show_results(request, context):
    return render(request, 'project_app/results.html', context)

def user_login(request):
    # if user is loggedin go to home page
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password is incorrect.')
    return render(request, 'project_app/user_login.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')

def user_registration(request):
    # if user is loggedin go to home page
    if request.user.is_authenticated:
        return redirect('home')
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            print(user)
            messages.success(request, "Account successfully created for: " + user)
            return redirect('user_login')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
    context = {'form':form}
    return render(request, 'project_app/user_registration.html', context)