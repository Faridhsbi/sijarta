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


class EmailOrPhoneBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            # Coba cari user berdasarkan no_hp
            user = User.objects.get(no_hp=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

def login_view(request):
    if request.method == 'POST':
        no_hp = request.POST.get('no_hp')
        password = request.POST.get('password')

        # Gunakan no_hp sebagai username untuk autentikasi
        user = authenticate(request, username=no_hp, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login berhasil! Selamat datang kembali.")
            return redirect("main:show_main")
        else:
            messages.error(request, "Nomor HP atau password salah. Silakan coba lagi.")
    
    return render(request, 'login.html')

def choose_role(request):
    if request.method == 'GET':
        role = request.GET.get('role')
        if role == 'Pengguna':
            return redirect('authentication:register_pengguna')
        elif role == 'Pekerja':
            return redirect('authentication:register_pekerja')
    return render(request, 'choose_role.html')

def register_pengguna(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.no_hp  # Set username sama dengan no_hp
            user.role = "pengguna"
            user.save()
            
            # Buat objek Pengguna
            pengguna = Pengguna(id=user, level="Bronze")  # Set level default
            pengguna.save()
            
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('authentication:login')
        else:
            messages.error(request, 'Terjadi kesalahan dalam registrasi.')
    else:
        form = UserRegisterForm()

    return render(request, 'user_register.html', {'form': form})

def register_pekerja(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        pekerja_form = WorkerRegisterForm(request.POST)

        if user_form.is_valid() and pekerja_form.is_valid():
            # Simpan User
            user = user_form.save(commit=False)
            user.username = user.no_hp  # Set username sama dengan no_hp
            user.role = "pekerja"
            user.save()

            # Simpan Pekerja
            pekerja = pekerja_form.save(commit=False)
            pekerja.id = user
            pekerja.save()

            messages.success(request, 'Registrasi pekerja berhasil! Silakan login.')
            return redirect('authentication:login')
        else:
            messages.error(request, 'Terjadi kesalahan dalam registrasi.')
    else:
        user_form = UserRegisterForm()
        pekerja_form = WorkerRegisterForm()

    context = {
        'user_form': user_form,
        'pekerja_form': pekerja_form
    }
    return render(request, 'worker_register.html', context)



def logout_view(request):
    logout(request)
    return redirect('authentication:login')

