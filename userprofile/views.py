from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.models import *
from django.db import connection

from main.views import get_cookie
# # Create your views here.


def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            print(cursor.fetchall)
            return cursor.fetchall()
        else:
            return cursor.rowcount


def show_profile_pengguna(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id

    query = "SELECT nama, jeniskelamin, nohp, tgllahir, alamat, saldomypay FROM sijarta.pengguna WHERE id = %s"
    query_pelanggan = "SELECT * FROM sijarta.pelanggan WHERE id = %s"
    params = [user_id]

    result = execute_query(query, params)
    result2 = execute_query(query_pelanggan, params)

    print(f"User ID from cookie: {user_id}")
    print("Pengguna result:", result)
    print("Pelanggan result:", result2)

    if not result:
        return redirect('authentication:login')  # Redirect jika data tidak ditemukan

    context = {
        'nama': result[0][0],
        'jenis_kelamin': result[0][1],
        'no_hp': result[0][2],
        'tgl_lahir': result[0][3],
        'alamat': result[0][4],
        'saldo_mypay': result[0][5],
        'level': result2[0][1] if result2 else 'Bronze',  # Add level if exists
    }

    return render(request, 'profile_pengguna.html', context)


def show_profile_pekerja(request):
    context = {
        'nama' : 'Budi',
        'jenis_kelamin' : 'Laki-laki',
        'no_hp' : "0857111",
        'tgl_lahir' : "01-10-2005",
        'alamat' : "jakarta",
        'saldo_mypay'  : 200000,
        'link_foto' : "https://static.promediateknologi.id/crop/0x0:0x0/x/photo/p2/140/2024/01/20/20240120_021207-662695297.jpg",
        'nama_bank' : "OVO",
        'no_rekening' : "123456789",
        "npwp" : "98776431",
        "rating" : 4.0,
        "jml_pesanan_selesai" : 5,
        "kategori1" : "Cuci Dapur",
        "kategori2" : "Bersihkan Kamar",
    }
    return render(request, 'profile_pekerja.html', context)

def show_edit_pengguna(request):
    context = {
        'nama' : 'Budi',
        'jenis_kelamin' : 'Laki-laki',
        'no_hp' : "0857111",
        'tgl_lahir' : "01-10-2005",
        'alamat' : "jakarta",
        'link_foto' : "https://st2.depositphotos.com/4211323/8820/v/950/depositphotos_88205990-stock-illustration-stop-tyrannosaurus-red-is-dangerous.jpg"

        # 'saldo_mypay'  : 200000,
    }
    return render(request, 'edit_profile_pengguna.html', context)

def show_edit_pekerja(request):
    context = {
        'nama' : 'Budi',
        'jenis_kelamin' : 'Laki-laki',
        'no_hp' : "0857111",
        'tgl_lahir' : "01-10-2005",
        'alamat' : "jakarta",
        'saldo_mypay'  : 200000,
        'nama_bank' : "OVO",
        'no_rekening' : "123456789",
        "npwp" : "98776431",
        'link_foto' : "https://static.promediateknologi.id/crop/0x0:0x0/x/photo/p2/140/2024/01/20/20240120_021207-662695297.jpg",

        # "rating" : 4.0,
        # "jml_pesanan_selesai" : 5,
        # "kategori1" : "Cuci Dapur",
        # "kategori2" : "Bersihkan Kamar",
    }
    return render(request, 'edit_profile_pekerja.html', context)



def profile_view(request):
    user = request.user
    print(user.nama)  # Debug data pengguna
    if user.role == 'pengguna':
        # Load relasi Pengguna
        pengguna = Pengguna.objects.select_related('id').get(id=user)
        context = {
            'saldo_mypay' : 350000,
            'user': user,
            'pengguna': pengguna,
            'level': pengguna.level
        }
        return render(request, 'profile_pengguna.html', context)
        
    elif user.role == 'pekerja':
        # Load relasi Pekerja
        pekerja = Pekerja.objects.select_related('id').get(id=user)
        context = {
            'saldo_my_pay' : 2000000,
            'user': user,
            'pekerja': pekerja,
            'nama_bank': pekerja.nama_bank,
            'nomor_rekening': pekerja.nomor_rekening,
            'npwp': pekerja.npwp,
            'link_foto': pekerja.link_foto,
            'rating': pekerja.rating + 3.5,
            'jml_pesanan_selesai': pekerja.jml_pesanan_selesai + 2,
            'kategori1' : "Deep Cleaning",
            'kategori2' : "Home Cleaning",
        }
        return render(request, 'profile_pekerja.html', context)
    else:
        messages.error(request, "Role tidak dikenali.")
        return redirect('home')

def edit_profile_pengguna(request):
    user = request.user
    if user.role != 'pengguna':
        messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('profile')

    if request.method == 'POST':
        user.nama = request.POST.get('nama')
        user.jenis_kelamin = request.POST.get('jenis_kelamin')
        user.no_hp = request.POST.get('no_hp')
        user.tgl_lahir = request.POST.get('tgl_lahir')
        user.alamat = request.POST.get('alamat')
        user.save()
        messages.success(request, "Profil pengguna berhasil diperbarui.")
        return redirect('userprofile:profile')

    return render(request, 'edit_profile_pengguna.html', {'user': user})

def edit_profile_pekerja(request):
    user = request.user
    if user.role != 'pekerja':
        messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('profile')

    if request.method == 'POST':
        user.nama = request.POST.get('nama')
        user.jenis_kelamin = request.POST.get('jenis_kelamin')
        user.no_hp = request.POST.get('no_hp')
        user.tgl_lahir = request.POST.get('tgl_lahir')
        user.alamat = request.POST.get('alamat')
        user.nama_bank = request.POST.get('nama_bank')
        user.nomor_rekening = request.POST.get('nomor_rekening')
        user.npwp = request.POST.get('npwp')
        user.link_foto = request.POST.get('link_foto')
        user.save()
        messages.success(request, "Profil pekerja berhasil diperbarui.")
        return redirect('userprofile:profile')

    return render(request, 'edit_profile_pekerja.html', {'user': user})

def show_mypay(request): # PLACEHOLDER
    user = request.user
    transaksi1 = {'nominal': 15000, 'tanggal': '20-10-2024', 'kategori': 'Transfer MyPay'}
    transaksi2 = {'nominal': -100000, 'tanggal': '16-11-2024', 'kategori': 'Pemesanan Jasa'}
    transaksi3 = {'nominal': 15000, 'tanggal': '12-12-2024', 'kategori': 'TopUp MyPay'}

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