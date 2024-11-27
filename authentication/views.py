import datetime
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
# from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
# from django.contrib.auth.hashers import check_password
from django.db import connection

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        else:
            return cursor.rowcount

def set_cookie(response, key, value, days_expire=7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie(key, value, max_age=max_age, expires=expires, httponly=True)

def login_view(request):
    if request.method == 'POST':
        no_hp = request.POST.get('no_hp')
        password = request.POST.get('password')
        query = "SELECT id, pwd, nama FROM SIJARTA.pengguna WHERE nohp = %s"
        params = [no_hp]
        result = execute_query(query, params)
        if result:
            user_id, stored_password, user_name = result[0]
            if password == stored_password:  # Compare plain-text passwords
                response = redirect("main:show_main")
                response.set_cookie('user_id', user_id)
                response.set_cookie('user_name', user_name)
                return response
            else:
                return redirect('authentication:login')
        else:
            return redirect('authentication:login')
    return render(request, 'login.html')


def choose_role(request):
    return render(request, 'choose_role.html')

def register_pengguna(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        password = request.POST.get('password1')  # Store plain-text password
        jenis_kelamin = request.POST.get('jenis_kelamin')
        no_hp = request.POST.get('no_hp')
        tgl_lahir = request.POST.get('tgl_lahir')
        alamat = request.POST.get('alamat')
        query = """
        INSERT INTO SIJARTA.pengguna (nama, password, jenis_kelamin, no_hp, tgl_lahir, alamat, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'pengguna')
        """
        params = [nama, password, jenis_kelamin, no_hp, tgl_lahir, alamat]
        execute_query(query, params)
        return redirect('authentication:login')
    return render(request, 'user_register.html')

def register_pekerja(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        password = request.POST.get('password1')  # Store plain-text password
        jenis_kelamin = request.POST.get('jenis_kelamin')
        no_hp = request.POST.get('no_hp')
        tgl_lahir = request.POST.get('tgl_lahir')
        alamat = request.POST.get('alamat')
        nama_bank = request.POST.get('nama_bank')
        nomor_rekening = request.POST.get('nomor_rekening')
        npwp = request.POST.get('npwp')
        link_foto = request.POST.get('link_foto')
        query_user = """
        INSERT INTO SIJARTA.pengguna (nama, password, jenis_kelamin, no_hp, tgl_lahir, alamat, role)
        VALUES (%s, %s, %s, %s, %s, %s, 'pekerja') RETURNING id
        """
        params_user = [nama, password, jenis_kelamin, no_hp, tgl_lahir, alamat]
        user_id = execute_query(query_user, params_user)[0][0]
        query_pekerja = """
        INSERT INTO pekerja (id, nama_bank, nomor_rekening, npwp, link_foto)
        VALUES (%s, %s, %s, %s, %s)
        """
        params_pekerja = [user_id, nama_bank, nomor_rekening, npwp, link_foto]
        execute_query(query_pekerja, params_pekerja)
        return redirect('authentication:login')
    return render(request, 'worker_register.html')

def logout_view(request):
    response = redirect('authentication:login')
    response.delete_cookie('user_id')  # Delete the authentication cookie
    return response

def landing_page(request):
    return render(request, 'landingpage.html')
