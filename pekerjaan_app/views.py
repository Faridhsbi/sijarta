import uuid
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
    user_role = get_cookie(request, 'user_role')
    linkfoto = ''
    if user_role == 'Pekerja':
        linkfoto = execute_query("SELECT linkfoto FROM sijarta.pekerja WHERE id = %s", [user_id])[0][0]
    else:
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
        'nama': user_name,
        'kategori': kategori_dict,
        'user_role': user_role,
        'pekerjaan': filtered_pekerjaan,
        'link_foto': linkfoto,
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



def show_status_pekerjaan(request):
    user_id = get_cookie(request, 'user_id')
    user_name = get_cookie(request, 'user_name')
    user_role = get_cookie(request, 'user_role')
    linkfoto = ''
    if user_role == 'Pekerja':
        linkfoto = execute_query("SELECT linkfoto FROM sijarta.pekerja WHERE id = %s", [user_id])[0][0]
    else:
        return redirect('main:show_main')
    
    status = execute_query('''
    SELECT status FROM sijarta.status_pesanan
    WHERE status != 'Menunggu Pembayaran'
    AND status != 'Mencari Pekerja'
    AND status != 'Terjadi Kesalahan pada Sistem'
    ''')
    # status_list = [s[0] for s in status]
    print(status)

    query_pekerjaan = '''
    SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
    FROM sijarta.tr_pemesanan_jasa tr
    JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
    JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
    JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
    WHERE tr.idpekerja = %s
    AND sp.status = 'Selesai'
    '''
    pekerjaan_selesai = execute_query(query_pekerjaan, [user_id])

    query_pekerjaan = '''
    SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
    FROM sijarta.tr_pemesanan_jasa tr
    JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
    JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
    JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
    WHERE tr.idpekerja = %s
    AND sp.status = 'Dibatalkan'
    '''
    pekerjaan_dibatalkan = execute_query(query_pekerjaan, [user_id])

    query_pekerjaan = '''
    SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
    FROM sijarta.tr_pemesanan_jasa tr
    JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
    JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
    JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
    WHERE tr.idpekerja = %s
    AND sp.status = 'Sedang Dikerjakan'
    AND tr.id NOT IN(
    SELECT tr.id FROM sijarta.tr_pemesanan_jasa
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
    WHERE sp.status = 'Selesai' OR sp.status = 'Dibatalkan'
    )
    '''
    pekerjaan_sedang_dikerjakan = execute_query(query_pekerjaan, [user_id])
    query_pekerjaan = '''
    SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
    FROM sijarta.tr_pemesanan_jasa tr
    JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
    JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
    JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
    WHERE tr.idpekerja = %s
    AND sp.status = 'Menunggu Pekerja'
    AND tr.id NOT IN(
    SELECT tr.id FROM sijarta.tr_pemesanan_jasa
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
    WHERE sp.status = 'Sedang Dikerjakan' OR sp.status = 'Dibatalkan' OR sp.status = 'Selesai'
    )
    '''
    pekerjaan_menunggu_pekerja = execute_query(query_pekerjaan, [user_id])

    if 'status' in request.GET and 'kategori' in request.GET:
        print(request.GET['status'])
        print(request.GET['status'] == '')
        print(request.GET['kategori'])
        print(request.GET['kategori'] == '')
        selected_status = request.GET['status']
        selected_kategori = request.GET['kategori']
        selected_kategori = "%" + selected_kategori.lower() + "%"

        query_pekerjaan = '''
        SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
        FROM sijarta.tr_pemesanan_jasa tr
        JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
        JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
        JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
        JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
        JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
        WHERE tr.idpekerja = %s
        AND sp.status = 'Selesai'
        AND LOWER(namasubkategori) LIKE %s
        '''
        pekerjaan_selesai = execute_query(query_pekerjaan, [user_id, selected_kategori])

        query_pekerjaan = '''
        SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
        FROM sijarta.tr_pemesanan_jasa tr
        JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
        JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
        JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
        JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
        JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
        WHERE tr.idpekerja = %s
        AND sp.status = 'Dibatalkan'
        AND LOWER(namasubkategori) LIKE %s
        '''
        pekerjaan_dibatalkan = execute_query(query_pekerjaan, [user_id, selected_kategori])

        query_pekerjaan = '''
        SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
        FROM sijarta.tr_pemesanan_jasa tr
        JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
        JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
        JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
        JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
        JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
        WHERE tr.idpekerja = %s
        AND sp.status = 'Sedang Dikerjakan'
        AND tr.id NOT IN(
        SELECT tr.id FROM sijarta.tr_pemesanan_jasa
        JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
        JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
        WHERE sp.status = 'Selesai' OR sp.status = 'Dibatalkan'
        ) AND LOWER(namasubkategori) LIKE %s
        '''
        pekerjaan_sedang_dikerjakan = execute_query(query_pekerjaan, [user_id, selected_kategori])


        query_pekerjaan = '''
        SELECT DISTINCT tr.id, namasubkategori, p.nama, sesi, totalbiaya, tglpemesanan, tglpekerjaan, sp.status
        FROM sijarta.tr_pemesanan_jasa tr
        JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
        JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
        JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
        JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
        JOIN sijarta.pengguna p ON tr.idpelanggan = p.id
        WHERE tr.idpekerja = %s
        AND sp.status = 'Menunggu Pekerja'
        AND tr.id NOT IN(
        SELECT tr.id FROM sijarta.tr_pemesanan_jasa
        JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
        JOIN sijarta.status_pesanan sp ON tr_status.idstatus = sp.id
        WHERE sp.status = 'Sedang Dikerjakan' OR sp.status = 'Dibatalkan' OR sp.status = 'Selesai'
        ) AND LOWER(namasubkategori) LIKE %s
        '''
        pekerjaan_menunggu_pekerja = execute_query(query_pekerjaan, [user_id, selected_kategori])

        if selected_status == 'Selesai':
            pekerjaan_dibatalkan = []
            pekerjaan_menunggu_pekerja = []
            pekerjaan_sedang_dikerjakan = []
        elif selected_status == 'Dibatalkan':
            pekerjaan_menunggu_pekerja = []
            pekerjaan_sedang_dikerjakan = []
            pekerjaan_selesai = []
        elif selected_status == 'Sedang Dikerjakan':
            pekerjaan_menunggu_pekerja = []
            pekerjaan_selesai = []
            pekerjaan_dibatalkan = []
        elif selected_status == 'Menunggu Pekerja':
            pekerjaan_selesai = []
            pekerjaan_dibatalkan = []
            pekerjaan_sedang_dikerjakan = []


    context = {
        'user_id': user_id,
        'nama': user_name,
        'user_role': user_role,
        'link_foto': linkfoto,
        'status_pekerjaan': status,
        'pekerjaan_selesai': pekerjaan_selesai,
        'pekerjaan_dibatalkan': pekerjaan_dibatalkan,
        'pekerjaan_sedang_dikerjakan': pekerjaan_sedang_dikerjakan,
        'pekerjaan_menunggu_pekerja': pekerjaan_menunggu_pekerja,
    }
    return render(request, 'status_pekerjaan.html', context)

def handle_update_status(request):
    print("tesTES")
    if request.method == 'POST':
        pekerjaan_id = request.POST.get('pekerjaan_id')
        new_status = request.POST.get('new_status')

        # Update the status of the pekerjaan in the database
        print(pekerjaan_id, new_status)
        execute_query("SET SEARCH_PATH TO sijarta")
        execute_query('DROP EXTENSION "uuid-ossp"')
        execute_query('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        # transaction_id = str(uuid.uuid4())
        query_update_status = '''
            INSERT INTO sijarta.tr_pemesanan_status VALUES
            (%s, (SELECT Id FROM sijarta.status_pesanan WHERE status= %s), CURRENT_TIMESTAMP)
            '''
        execute_query(query_update_status, [pekerjaan_id, new_status])

        # Redirect back to the status pekerjaan page
        return redirect('pekerjaan_app:show_status_pekerjaan')

    return redirect('pekerjaan_app:show_status_pekerjaan')