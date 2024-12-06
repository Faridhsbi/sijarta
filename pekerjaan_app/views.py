from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import connection
import json
from django.http import JsonResponse
# Create your views here.
def get_cookie(request, key):
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
            return cursor.fetchall()
        else:
            return cursor.rowcount


def show_pekerjaan(request):
    user_id = get_cookie(request, 'user_id')
    user_name = get_cookie(request, 'user_name')
    role = execute_query("SELECT * FROM sijarta.pekerja WHERE id = %s", [user_id])
    if role:
        role = 'pekerja'
    else:
        role = 'pengguna'

    if role != 'pekerja':
        return redirect('main:show_main')

    query_kategori = '''
    SELECT id, namakategori FROM sijarta.kategori_jasa kj
    WHERE kj.id IN
    (SELECT kategorijasaid
    FROM sijarta.pekerja_kategori_jasa pkj
    WHERE pkj.pekerjaid = %s)
    '''
    kategori = execute_query(query_kategori, [user_id])

    query_subkategori = '''
    SELECT skj.id, skj.namasubkategori, skj.kategorijasaid, kj.id, kj.namakategori
    FROM sijarta.subkategori_jasa skj
    JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
    ''' 
    subkategori = execute_query(query_subkategori)

    # Convert kategori and subkategori to a more usable format
    kategori_dict = {}
    for kat in kategori:
        kategori_dict[kat[1]] = []

    for subkat in subkategori:
        kategori_dict[subkat[4]].append(subkat[1])

    
    # Handle filtering
    filtered_pekerjaan = []
    if 'kategori' in request.GET and 'subkategori' in request.GET:
        selected_kategori = request.GET['kategori']
        selected_subkategori = request.GET['subkategori']
        print(selected_kategori)
        print(selected_subkategori)
        if selected_subkategori != '':
            print('case: 1')
            query_pekerjaan = '''
            SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan
            FROM sijarta.tr_pemesanan_jasa tr
            JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
            JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
            JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
            JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
            JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
            WHERE kj.id IN
            (SELECT kategorijasaid
            FROM sijarta.pekerja_kategori_jasa pkj
            WHERE pkj.pekerjaid = %s)
            AND tr_status.idtrpemesanan NOT IN 
            (SELECT tr_status2.idtrpemesanan FROM 
                sijarta.tr_pemesanan_status tr_status2
                JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
                WHERE sp.status = 'Terjadi Kesalahan pada Sistem'
                OR sp.status = 'Menunggu Pekerja'
                OR sp.status = 'Dibatalkan')
            AND
                tr_status.idtrpemesanan IN 
                (SELECT tr_status2.idtrpemesanan FROM 
                sijarta.tr_pemesanan_status tr_status2
                JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
                WHERE sp.status = 'Mencari Pekerja')
            AND namasubkategori = %s
            '''
            filtered_pekerjaan = execute_query(query_pekerjaan, [user_id, selected_subkategori])
        elif selected_kategori != '':
            print('case: 2')
            query_pekerjaan = '''
            SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan
            FROM sijarta.tr_pemesanan_jasa tr
            JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
            JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
            JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
            JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
            JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
            WHERE kj.id IN
            (SELECT kategorijasaid
            FROM sijarta.pekerja_kategori_jasa pkj
            WHERE pkj.pekerjaid = %s)
            AND tr_status.idtrpemesanan NOT IN 
            (SELECT tr_status2.idtrpemesanan FROM 
                sijarta.tr_pemesanan_status tr_status2
                JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
                WHERE sp.status = 'Terjadi Kesalahan pada Sistem'
                OR sp.status = 'Menunggu Pekerja'
                OR sp.status = 'Dibatalkan')
            AND
                tr_status.idtrpemesanan IN 
                (SELECT tr_status2.idtrpemesanan FROM 
                sijarta.tr_pemesanan_status tr_status2
                JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
                WHERE sp.status = 'Mencari Pekerja')
            AND namakategori = %s
            '''
            filtered_pekerjaan = execute_query(query_pekerjaan, [user_id, selected_kategori])
        else: # jika tidak memilih keduanya
            print('case: 3')
            query_pekerjaan = '''
            SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan
            FROM sijarta.tr_pemesanan_jasa tr
            JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
            JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
            JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
            JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
            JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
            WHERE kj.id IN
            (SELECT kategorijasaid
            FROM sijarta.pekerja_kategori_jasa pkj
            WHERE pkj.pekerjaid = %s)
            AND tr_status.idtrpemesanan NOT IN 
            (SELECT tr_status2.idtrpemesanan FROM 
                sijarta.tr_pemesanan_status tr_status2
                JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
                WHERE sp.status = 'Terjadi Kesalahan pada Sistem'
                OR sp.status = 'Menunggu Pekerja'
                OR sp.status = 'Dibatalkan')
            AND
                tr_status.idtrpemesanan IN 
                (SELECT tr_status2.idtrpemesanan FROM 
                sijarta.tr_pemesanan_status tr_status2
                JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
                WHERE sp.status = 'Mencari Pekerja')
            '''
            filtered_pekerjaan = execute_query(query_pekerjaan, [user_id])
        print(filtered_pekerjaan)
    context = {
        'user_id': user_id,
        'user_name': user_name,
        'kategori': kategori_dict,
        'role': role,
        'pekerjaan': filtered_pekerjaan,
    }

    return render(request, 'pekerjaan.html', context)

def handle_kerjakan_pesanan(request):
    if request.method == 'POST':
        pekerjaan_id = request.POST.get('pekerjaan_id')
        pekerjaan_sesi = execute_query("SELECT sesi FROM sijarta.tr_pemesanan_jasa WHERE id = %s", [pekerjaan_id])[0][0]

        pekerja_id = get_cookie(request, 'user_id')
        execute_query("SET SEARCH_PATH TO sijarta")
        query_update_status = '''
            INSERT INTO sijarta.tr_pemesanan_status VALUES
            (%s, (SELECT Id FROM sijarta.STATUS_PESANAN WHERE Status='Menunggu Pekerja'), CURRENT_TIMESTAMP)
            '''
        execute_query(query_update_status, [pekerjaan_id])

        sesi = str(pekerjaan_sesi) + "d"
        query_update_transaksi = '''
        UPDATE sijarta.tr_pemesanan_jasa 
        SET tglpekerjaan = CURRENT_DATE,
        idpekerja = %s,
        waktupekerjaan = %s
        WHERE id = %s;
        '''
        execute_query(query_update_transaksi, [pekerja_id, sesi, pekerjaan_id])
        # Redirect back to the pekerjaan list
        return redirect('pekerjaan_app:show_pekerjaan')

    return redirect('pekerjaan_app:show_pekerjaan')

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
