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
from psycopg2 import DatabaseError
import json
from datetime import datetime, timedelta

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT") or "RETURNING" in query.strip().upper():
            # Jika query adalah SELECT atau mengandung RETURNING, ambil hasilnya
            return cursor.fetchall()
        else:
            # Jika query lain, kembalikan jumlah baris yang terpengaruh
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

def set_message(response, message, level="info"):
    """
    Simpan pesan ke dalam cookie.
    
    :param response: HttpResponse object
    :param message: Pesan yang ingin ditampilkan
    :param level: Level pesan (e.g., "info", "success", "warning", "error")
    """
    # Ambil pesan yang sudah ada dalam cookie
    messages = response.cookies.get('messages')
    if messages:
        messages = json.loads(messages.value)
    else:
        messages = []

    # Tambahkan pesan baru
    messages.append({"message": message, "level": level})
    # print(message)
    print("level", level)
    # Simpan kembali ke dalam cookie
    response.set_cookie(
        "messages",
        json.dumps(messages),
        max_age=3600,  # Valid selama 1 jam
        httponly=True,
    )


def get_messages(request, response):
    messages = request.COOKIES.get("")
    print("cek", messages)
    if messages:
        messages = json.loads(messages)
        response.delete_cookie("messages")  # Hapus cookie setelah diambil
    else:
        messages = []
    return messages


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
                # Check role: Pelanggan or Pekerja
                query_pelanggan = "SELECT COUNT(*) FROM SIJARTA.pelanggan WHERE id = %s"
                query_pekerja = "SELECT COUNT(*) FROM SIJARTA.pekerja WHERE id = %s"
                is_pelanggan = execute_query(query_pelanggan, [user_id])[0][0] > 0
                is_pekerja = execute_query(query_pekerja, [user_id])[0][0] > 0

                role = "Pelanggan" if is_pelanggan else "Pekerja" if is_pekerja else None

                # Redirect or return error if no role
                if not role:
                    return redirect('authentication:login')

                response = redirect("main:show_main")
                response.set_cookie('user_id', user_id)
                response.set_cookie('user_name', user_name)
                response.set_cookie('user_role', role)
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
        try:
            nama = request.POST.get('nama')
            password = request.POST.get('password1')  # Store plain-text password
            jenis_kelamin = request.POST.get('jenis_kelamin')
            no_hp = request.POST.get('no_hp')
            tgl_lahir = request.POST.get('tgl_lahir')
            alamat = request.POST.get('alamat')

            # Query untuk tabel pengguna dengan RETURNING
            query_pengguna = """
            INSERT INTO SIJARTA.pengguna (id, nama, pwd, jeniskelamin, nohp, tgllahir, alamat, saldomypay)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, 0)
            RETURNING id
            """
            params_pengguna = [nama, password, jenis_kelamin, no_hp, tgl_lahir, alamat]
            
            # Dapatkan ID pengguna yang baru dibuat
            result = execute_query(query_pengguna, params_pengguna)
            new_user_id = result[0][0]  # Ambil ID dari hasil query RETURNING
            
            # Query untuk tabel pelanggan
            query_pelanggan = """
            INSERT INTO SIJARTA.pelanggan (id, level)
            VALUES (%s, %s)
            """
            params_pelanggan = [new_user_id, "Bronze"]
            
            # Masukkan data ke tabel pelanggan
            execute_query(query_pelanggan, params_pelanggan)

            return redirect('authentication:login')
        except Exception as e:
            print(f"Error: {e}")
            response = render(request, 'user_register.html', {'error': 'Error registering user.'})
            set_message(response, f"Terjadi kesalahan: {e}", level="error")
            return response
        
    return render(request, 'user_register.html')



def register_pekerja(request):
    if request.method == 'POST':
        try:
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
            SET search_path TO SIJARTA;
            INSERT INTO SIJARTA.pengguna (id, nama, pwd, jeniskelamin, nohp, tgllahir, alamat, saldomypay)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, 0) RETURNING id
            """
            params_user = [nama, password, jenis_kelamin, no_hp, tgl_lahir, alamat]
            user_id = execute_query(query_user, params_user)[0][0]
            query_pekerja = """
            INSERT INTO SIJARTA.pekerja (id, namabank, nomorrekening, npwp, linkfoto, rating, jmlpesananselesai)
            VALUES (%s, %s, %s, %s, %s, 0.0, 0)
            """
            params_pekerja = [user_id, nama_bank, nomor_rekening, npwp, link_foto]
            execute_query(query_pekerja, params_pekerja)
            return redirect('authentication:login')
        except Exception as e:
            print(f"Error: {e}")
            response = render(request, 'worker_register.html', {'error': 'Error registering Worker.'})
            set_message(response, f"Terjadi kesalahan: {e}", level="error")
            return response
        
    return render(request, 'worker_register.html')

def logout_view(request):
    response = redirect('authentication:login')
    response.delete_cookie('user_id')  # Delete the authentication cookie
    return response

def landing_page(request):
    return render(request, 'landingpage.html')