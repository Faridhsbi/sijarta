from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect

# Create your views here.
def show_pekerjaan(request): # PLACEHOLDER
    user = request.user
    if user.role != 'pekerja':
        messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('main:show_main')
    
    kategori1 = {'kategori': 'Home Cleaning', 'subkategori': ['Setrika', 'Daily Cleaning', 'Pembersihan Dapur']}
    kategori2 = {'kategori': 'Massage', 'subkategori': ['Foot massage', 'Back massage', 'Arm massage', 'Full package']}
    kategori3 = {'kategori': 'Deep Cleaning', 'subkategori': ['Cuci kasur', 'Cuci sofa']}

    pekerjaan1 = {'id': 1, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika', 'nama_pelanggan': 'Budi', 'tanggal_pemesanan': '10-11-2024', 'tanggal_pekerjaan': '20-11-2024', 'total_biaya': 150000}
    pekerjaan2 = {'id': 2, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika', 'nama_pelanggan': 'Caca', 'tanggal_pemesanan': '15-11-2024', 'tanggal_pekerjaan': '22-11-2024', 'total_biaya': 100000}
    pekerjaan3 = {'id': 3, 'kategori': 'Home Cleaning', 'subkategori': 'Daily Cleaning', 'nama_pelanggan': 'Ala', 'tanggal_pemesanan': '11-11-2024', 'tanggal_pekerjaan': '14-11-2024', 'total_biaya': 100}
    pekerjaan4 = {'id': 4, 'kategori': 'Home Cleaning', 'subkategori': 'Pembersihan Dapur', 'nama_pelanggan': 'Walah', 'tanggal_pemesanan': '9-11-2024', 'tanggal_pekerjaan': '13-11-2024', 'total_biaya': 125000}

    pekerjaan5 = {'id': 5, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'nama_pelanggan': 'asdsadv', 'tanggal_pemesanan': '15-11-2024', 'tanggal_pekerjaan': '16-11-2024', 'total_biaya': 130250}
    pekerjaan6 = {'id': 6, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'nama_pelanggan': 'AAA', 'tanggal_pemesanan': '10-12-2024', 'tanggal_pekerjaan': '20-12-2024', 'total_biaya': 500000}
    pekerjaan7 = {'id': 7, 'kategori': 'Massage', 'subkategori': 'Arm massage', 'nama_pelanggan': 'efea', 'tanggal_pemesanan': '19-11-2024', 'tanggal_pekerjaan': '20-11-2024', 'total_biaya': 300000}
    
    # pekerjaan8 = {'kategori': 'Deep Cleaning', 'subkategori': 'Cuci kasur', 'nama_pelanggan': 'Budi', 'tanggal_pemesanan': '10-11-2024', 'tanggal_pekerjaan': '20-11-2024', 'total_biaya': 150000}


    context = {
        'no_hp' : '0857111',
        'saldo_mypay' : 200000,
        'kategori' : [kategori1, kategori2, kategori3],
        'pekerjaan' : [pekerjaan1, pekerjaan2, pekerjaan3, pekerjaan4, pekerjaan5, pekerjaan6, pekerjaan7],
    }

    return render(request, 'pekerjaan.html', context)

def show_status_pekerjaan(request): # PLACEHOLDER
    user = request.user
    if user.role != 'pekerja':
        messages.error(request, "Anda tidak memiliki izin untuk mengakses halaman ini.")
        return redirect('main:show_main')
    

    kategori1 = {'kategori': 'Home Cleaning', 'subkategori': ['Setrika', 'Daily Cleaning', 'Pembersihan Dapur']}
    kategori2 = {'kategori': 'Massage', 'subkategori': ['Foot massage', 'Back massage', 'Arm massage', 'Full package']}
    kategori3 = {'kategori': 'Deep Cleaning', 'subkategori': ['Cuci kasur', 'Cuci sofa']}

    pekerjaan1 = {'id': 1, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika', 'nama_pelanggan': 'Budi', 'tanggal_pemesanan': '10-11-2024', 'tanggal_pekerjaan': '20-11-2024', 'total_biaya': 150000, 'status': 'Menunggu Pekerja Berangkat'}
    pekerjaan2 = {'id': 2, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika', 'nama_pelanggan': 'Caca', 'tanggal_pemesanan': '15-11-2024', 'tanggal_pekerjaan': '22-11-2024', 'total_biaya': 100000, 'status': 'Pekerja Tiba Di Lokasi'}

    pekerjaan5 = {'id': 5, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'nama_pelanggan': 'asdsadv', 'tanggal_pemesanan': '15-11-2024', 'tanggal_pekerjaan': '16-11-2024', 'total_biaya': 130250, 'status': 'Pelayanan Jasa Sedang Dilakukan'}
    pekerjaan7 = {'id': 7, 'kategori': 'Massage', 'subkategori': 'Arm massage', 'nama_pelanggan': 'efea', 'tanggal_pemesanan': '19-11-2024', 'tanggal_pekerjaan': '20-11-2024', 'total_biaya': 300000, 'status': 'Pesanan Selesai'}
    
    context = {
        'no_hp' : '0857111',
        'saldo_mypay' : 200000,
        'kategori' : [kategori1, kategori2, kategori3],
        'pekerjaan' : [pekerjaan1, pekerjaan2, pekerjaan5, pekerjaan7],
    }

    return render(request, 'status_pekerjaan.html', context)
