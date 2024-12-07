from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.models import *
from django.db import connection

from main.views import get_cookie
# # Create your views here.
def get_cookie(request, key):
    print("User Role:", request.COOKIES.get('user_role'))
    return request.COOKIES.get(key)

def get_message(request):
    message = request.COOKIES.get('message')
    if message:
        response = render(request, "homepage.html", {"message": message})
        response.delete_cookie('message')  # Remove the message after displaying it
        return response
    return render(request, "homepage.html")

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            # print(cursor.fetchall)
            return cursor.fetchall()
        else:
            return cursor.rowcount


def show_profile_pengguna(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    user_role = get_cookie(request, 'user_role')
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id

    query = "SELECT nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay FROM sijarta.pengguna WHERE id = %s"
    # query = "SELECT * FROM sijarta.pengguna WHERE id = %s"

    query_pelanggan = "SELECT * FROM sijarta.pelanggan WHERE id = %s"
    params = [user_id]

    result = execute_query(query, params)
    result2 = execute_query(query_pelanggan, params)

    # print(f"User ID from cookie: {user_id}")
    # print("Pengguna result:", result)
    # print("Pelanggan result:", result2)

    context = {
        'nama': result[0][0],
        'jenis_kelamin': 'Laki-laki' if result[0][1] == "L" else "Perempuan",
        'no_hp': result[0][2],
        'tgl_lahir': result[0][3],
        'alamat': result[0][4],
        'saldo_mypay': result[0][5],
        'level': result2[0][1],  # Add level if exists
        'user_id' : user_id,
        'user_role': user_role,
    }

    return render(request, 'profile_pengguna.html', context)


def show_profile_pekerja(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    user_role = get_cookie(request, 'user_role')
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id

    query = "SELECT nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay FROM sijarta.pengguna WHERE id = %s"
    # query = "SELECT * FROM sijarta.pengguna WHERE id = %s"

    query_pekerja = "SELECT npwp, nomorrekening, rating, jmlpesananselesai, linkfoto FROM sijarta.pekerja WHERE id = %s"
    params = [user_id]

    result = execute_query(query, params)
    result2 = execute_query(query_pekerja, params)

    query_kategori_jasa ='''
    SELECT namakategori FROM SIJARTA.kategori_jasa
    JOIN SIJARTA.pekerja_kategori_jasa ON kategorijasaid = kategori_jasa.id 
    JOIN SIJARTA.pekerja ON pekerjaid = PEKERJA.id
    WHERE pekerja.id = %s
    '''
    kategori_jasa = execute_query(query_kategori_jasa, params)
    kategori_jasa_list = [item[0] for item in kategori_jasa]  # Ambil nilai dari tuple
    # kategori_jasa_str = ', '.join(kategori_jasa_list)  # Gabungkan menjadi satu string
    print(kategori_jasa_list)
    # print(f"User ID from cookie: {user_id}")
    # print("Pengguna result:", result)
    # print("Pelanggan result:", result2)

    context = {
        'nama': result[0][0],
        'jenis_kelamin': 'Laki-laki' if result[0][1] == "L" else "Perempuan",
        'no_hp': result[0][2],
        'tgl_lahir': result[0][3],
        'alamat': result[0][4],
        'saldo_mypay': result[0][5],
        'npwp' : result2[0][0],
        'nomor_rekening' : result2[0][1],
        'rating' : result2[0][2],
        'jml_pesanan_selesai' : result2[0][3],
        'kategori_jasa' : kategori_jasa_list,
        'link_foto' : result2[0][4],
        'user_id' : user_id,
        'user_role': user_role,
    }

    return render(request, 'profile_pekerja.html', context)


def edit_profile_pengguna(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    user_role = get_cookie(request, 'user_role')
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id
    
    if user_role != 'Pelanggan':
        # messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('userprofile:show_pengguna')

    if request.method == 'POST':
        nama = request.POST['nama']
        jenis_kelamin = request.POST['jenis_kelamin']
        no_hp = request.POST['no_hp']
        tgl_lahir = request.POST['tgl_lahir']
        alamat = request.POST['alamat']
        query_edit = '''
        UPDATE SIJARTA.pengguna SET nama = %s, jeniskelamin = %s, nohp = %s, tgllahir = %s, alamat = %s
        WHERE id = %s
        '''
        params = [nama, jenis_kelamin, no_hp, tgl_lahir, alamat, user_id]

        result = execute_query(query_edit, params)
        # messages.success(request, "Profil pengguna berhasil diperbarui.")
        return redirect('userprofile:show_pengguna')
    
    query = "SELECT nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay FROM sijarta.pengguna WHERE id = %s"
    query_pelanggan = "SELECT * FROM sijarta.pelanggan WHERE id = %s"
    params = [user_id]

    result = execute_query(query, params)
    result2 = execute_query(query_pelanggan, params)

    context = {
        'nama': result[0][0],
        'jenis_kelamin': 'Laki-laki' if result[0][1] == "L" else "Perempuan",
        'no_hp': result[0][2],
        'tgl_lahir': result[0][3],
        'alamat': result[0][4],
        'saldo_mypay': result[0][5],
        'level': result2[0][1],  # Add level if exists
        'user_id' : user_id,
        'user_role': user_role,
    }
    return render(request, 'edit_profile_pengguna.html', context)

def edit_profile_pekerja(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    user_role = get_cookie(request, 'user_role')
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id

    query = "SELECT nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay FROM sijarta.pengguna WHERE id = %s"
    # query = "SELECT * FROM sijarta.pengguna WHERE id = %s"

    query_pekerja = "SELECT npwp, nomorrekening, rating, jmlpesananselesai, linkfoto FROM sijarta.pekerja WHERE id = %s"
    params = [user_id]

    result = execute_query(query, params)
    result2 = execute_query(query_pekerja, params)

    query_kategori_jasa ='''
    SELECT namakategori FROM SIJARTA.kategori_jasa
    JOIN SIJARTA.pekerja_kategori_jasa ON kategorijasaid = kategori_jasa.id 
    JOIN SIJARTA.pekerja ON pekerjaid = PEKERJA.id
    WHERE pekerja.id = %s
    '''
    kategori_jasa = execute_query(query_kategori_jasa, params)
    kategori_jasa_list = [item[0] for item in kategori_jasa]  # Ambil nilai dari tuple
    # kategori_jasa_str = ', '.join(kategori_jasa_list)  # Gabungkan menjadi satu string
    print(kategori_jasa_list)
    # print(f"User ID from cookie: {user_id}")
    # print("Pengguna result:", result)
    # print("Pelanggan result:", result2)

    context = {
        'nama': result[0][0],
        'jenis_kelamin': 'Laki-laki' if result[0][1] == "L" else "Perempuan",
        'no_hp': result[0][2],
        'tgl_lahir': result[0][3],
        'alamat': result[0][4],
        'saldo_mypay': result[0][5],
        'npwp' : result2[0][0],
        'nomor_rekening' : result2[0][1],
        'rating' : result2[0][2],
        'jml_pesanan_selesai' : result2[0][3],
        'kategori_jasa' : kategori_jasa_list,
        'link_foto' : result2[0][4],
        'user_id' : user_id,
        'user_role': user_role,
    }

    if request.method == 'POST':
        nama = request.POST.get('nama')
        jenis_kelamin = request.POST.get('jenis_kelamin')
        no_hp = request.POST.get('no_hp')
        tgl_lahir = request.POST.get('tgl_lahir')
        alamat = request.POST.get('alamat')
        nama_bank = request.POST.get('nama_bank')
        nomor_rekening = request.POST.get('nomor_rekening')
        npwp = request.POST.get('npwp')
        link_foto = request.POST.get('link_foto')

        query_edit = '''
        UPDATE SIJARTA.pengguna SET nama = %s, jeniskelamin = %s, nohp = %s, tgllahir = %s, alamat = %s
        WHERE id = %s;
        UPDATE SIJARTA.pekerja SET namabank = %s, nomorrekening = %s, npwp = %s, linkfoto = %s
        WHERE id = %s;
        '''
        params = [nama, jenis_kelamin, no_hp, tgl_lahir, alamat, user_id,
                  nama_bank, nomor_rekening, npwp, link_foto, user_id]

        result = execute_query(query_edit, params)
        return redirect('userprofile:show_pekerja')

    return render(request, 'edit_profile_pekerja.html', context)

def show_mypay(request): # PLACEHOLDER
    # user = request.user
    # transaksi1 = {'nominal': 15000, 'tanggal': '20-10-2024', 'kategori': 'Transfer MyPay'}
    # transaksi2 = {'nominal': -100000, 'tanggal': '16-11-2024', 'kategori': 'Pemesanan Jasa'}
    # transaksi3 = {'nominal': 15000, 'tanggal': '12-12-2024', 'kategori': 'TopUp MyPay'}
    user_id = get_cookie(request, 'user_id')


    query = "SELECT nama FROM SIJARTA.pengguna WHERE id = %s"
    params = [user_id]
    result = execute_query(query, params)
    if result:
        user_name = result[0][0]

    context = {
        'no_hp' : '0857111',
        'saldo_mypay' : 200000,
        'transaksi1' : transaksi1,
        'transaksi2' : transaksi2,
        'transaksi3' : transaksi3,
    }

    return render(request, 'mypay.html', context)

def new_transaction(request): # PLACEHOLDER 
    user = request.user
    jasa1 = {'id': 1, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika','total_biaya': 150000}
    jasa2 = {'id': 2, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika', 'total_biaya': 100000}
    jasa3 = {'id': 3, 'kategori': 'Home Cleaning', 'subkategori': 'Daily Cleaning','total_biaya': 100}
    jasa4 = {'id': 4, 'kategori': 'Home Cleaning', 'subkategori': 'Pembersihan Dapur', 'total_biaya': 125000}

    jasa5 = {'id': 5, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'total_biaya': 130250}
    jasa6 = {'id': 6, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'total_biaya': 500000}
    jasa7 = {'id': 7, 'kategori': 'Massage', 'subkategori': 'Arm massage', 'total_biaya': 300000}

    context = {
        'nama' : 'Budi',
        'tanggal_transaksi' : '20-10-2024',
        'saldo_mypay' : 200000,
        'kategori': ['Membayar Pemesanan Jasa', 'TopUp MyPay', 'Transfer MyPay', 'Withdrawal'],
        'jasa' : [jasa1, jasa2, jasa3, jasa4, jasa5, jasa6, jasa7],
    }
    # if request.method == 'POST':
    # dll.. dari form
    return render(request, 'new_transaction.html', context)