import datetime
from django.shortcuts import render, redirect, reverse
from .forms import *
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password

# AUTH

def landing_page(request):
    return render(request, 'landingpage.html')


# def login_view(request):
#     if request.method == 'POST':
#         no_hp = request.POST.get('no_hp')
#         password = request.POST.get('password')
#         user = authenticate(request, no_hp=no_hp, password=password)
#         print(f"Attempting to authenticate with: {no_hp} and {password}")
#         if user is not None:
#             login(request, user)
#             return redirect("main:show_main")  # Redirect ke halaman utama
#         else:
#             print("Invalid credentials")
#     return render(request, 'login.html')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect("/")
            response.set_cookie("user_logged_in", str(datetime.datetime.now()))
            return response
    else:
        form = AuthenticationForm(request)
    return render(request, "login.html", {"form": form})

# View untuk halaman memilih role
def choose_role(request):
    if request.method == 'GET':
        role = request.GET.get('role')  # Mendapatkan pilihan role dari GET
        if role == 'Pengguna':
            return redirect('authentication:register_pengguna')
        elif role == 'Pekerja':
            return redirect('authentication:register_pekerja')
    return render(request, 'choose_role.html')

def register_pengguna(request):
    print(request.method)
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        # print(request.POST) 
        if form.is_valid():
            # Simpan data User dengan role sebagai "pengguna"
            user = form.save(commit=False)
            user.password = make_password("password_baru")
            user.role = "pengguna"  # Set role di User
            user.save()

            return redirect('authentication:login')
        else:
            print(form.errors)  # Redirect ke halaman login setelah registrasi
    else:
        form = UserRegisterForm()

    return render(request, 'user_register.html', {'form': form})

def register_pekerja(request):
    # print("ppppppppppppppp")
    # print(request.method)
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        pekerja_form = WorkerRegisterForm(request.POST)

        print("User Form Valid: ", user_form.is_valid())  # Cek validitas form user
        print("Pekerja Form Valid: ", pekerja_form.is_valid())  # Cek validitas form pekerja
        
        if user_form.is_valid() and pekerja_form.is_valid():
            # Simpan data User dengan role sebagai "Pekerja"
            user = user_form.save(commit=False)
            user.password = make_password("password_baru")
            user.role = "pekerja"  # Set role di User
            user.save()

            # Buat Pekerja yang terkait dengan User yang baru dibuat
            pekerja = pekerja_form.save(commit=False)
            pekerja.id = user  # Hubungkan Pekerja dengan User
            pekerja.save()

            return redirect('authentication:login')
    else:
        # print('aaaaaa')
        user_form = UserRegisterForm()
        pekerja_form = WorkerRegisterForm()
    context = {'user_form': user_form, 'pekerja_form' : pekerja_form}
    return render(request, 'worker_register.html', context)



def logout_view(request):
    logout(request)
    return redirect('homepage')

