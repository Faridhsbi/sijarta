from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from .models import User


def show_profile_pengguna(request):
    context = {
        'nama' : 'Budi',
        'jenis_kelamin' : 'Laki-laki',
        'no_hp' : "0857111",
        'tgl_lahir' : "01-10-2005",
        'alamat' : "jakarta",
        'saldo_mypay'  : 200000,
        'link_foto' : "https://st2.depositphotos.com/4211323/8820/v/950/depositphotos_88205990-stock-illustration-stop-tyrannosaurus-red-is-dangerous.jpg"
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
    if user.role == 'pengguna':
        return render(request, 'profile_pengguna.html', {'user': user})
    elif user.role == 'pekerja':
        return render(request, 'profile_pekerja.html', {'user': user})
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
        return redirect('profile')

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
        return redirect('profile')

    return render(request, 'edit_profile_pekerja.html', {'user': user})



