import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.models import *
from django.db import connection
from django.http import JsonResponse
import json

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

# def show_mypay(request): # PLACEHOLDER
#     # user = request.user
#     # transaksi1 = {'nominal': 15000, 'tanggal': '20-10-2024', 'kategori': 'Transfer MyPay'}
#     # transaksi2 = {'nominal': -100000, 'tanggal': '16-11-2024', 'kategori': 'Pemesanan Jasa'}
#     # transaksi3 = {'nominal': 15000, 'tanggal': '12-12-2024', 'kategori': 'TopUp MyPay'}
#     user_id = get_cookie(request, 'user_id')
#     if not user_id:
#         return redirect('/auth/login')
#     user_name = None
#     if user_id:
#         query = "SELECT nama FROM SIJARTA.pengguna WHERE id = %s"
#         params = [user_id]
#         result = execute_query(query, params)
#         if result:
#             user_name = result[0][0]

#     query = "SELECT * FROM SIJARTA.tr_mypay WHERE userid = %s"
#     params = [user_id]
#     result = execute_query(query, params)
#     if result:
#         transaksi_mypay = result


#     context = {
#         'no_hp' : '0857111',
#         'saldo_mypay' : 200000,
#         # 'transaksi1' : transaksi1,
#         # 'transaksi2' : transaksi2,
#         # 'transaksi3' : transaksi3,
#         'transaksi_mypay': transaksi_mypay, 
#     }

    # return render(request, 'mypay.html', context)
def show_mypay(request):
    user_id = get_cookie(request, 'user_id')
    user_name = get_cookie(request, 'user_name')
    if not user_id:
        return redirect('authentication:login')
    user_role = get_cookie(request, 'user_role')
    linkfoto = ''
    if user_role == 'Pekerja':
        linkfoto = execute_query("SELECT linkfoto FROM sijarta.pekerja WHERE id = %s", [user_id])[0][0]

    # user
    query_user = "SELECT nohp, saldomypay FROM SIJARTA.pengguna WHERE id = %s"
    params_user = [user_id]
    result_user = execute_query(query_user, params_user)
    print(result_user)
    if result_user:
        no_hp, saldo_mypay = result_user[0]
    else:
        no_hp, saldo_mypay = None, None

    execute_query("SET search_path TO SIJARTA")

    # transaksi
    query_transactions = '''
    SELECT tr.id, tr.tgl, tr.nominal, kat.nama
    FROM sijarta.tr_mypay tr 
    JOIN sijarta.kategori_tr_mypay kat ON kat.id = tr.kategoriid 
    WHERE userid = %s
    ORDER BY tr.tgl DESC
    '''
    params_transactions = [user_id]
    transactions = execute_query(query_transactions, params_transactions)
    print(transactions)
    print("TESTESTESTESTESTESTESTES")


    context = {
        'no_hp': no_hp,
        'saldo_mypay': saldo_mypay,
        'transactions': transactions,
        'user_id': user_id,
        'nama': user_name,
        'user_role': user_role,
        'link_foto': linkfoto,
    }

    return render(request, 'mypay.html', context)

# def new_transaction(request): # PLACEHOLDER 
#     user = request.user
#     jasa1 = {'id': 1, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika','total_biaya': 150000}
#     jasa2 = {'id': 2, 'kategori': 'Home Cleaning', 'subkategori': 'Setrika', 'total_biaya': 100000}
#     jasa3 = {'id': 3, 'kategori': 'Home Cleaning', 'subkategori': 'Daily Cleaning','total_biaya': 100}
#     jasa4 = {'id': 4, 'kategori': 'Home Cleaning', 'subkategori': 'Pembersihan Dapur', 'total_biaya': 125000}

#     jasa5 = {'id': 5, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'total_biaya': 130250}
#     jasa6 = {'id': 6, 'kategori': 'Massage', 'subkategori': 'Foot massage', 'total_biaya': 500000}
#     jasa7 = {'id': 7, 'kategori': 'Massage', 'subkategori': 'Arm massage', 'total_biaya': 300000}

#     context = {
#         'nama' : 'Budi',
#         'tanggal_transaksi' : '20-10-2024',
#         'saldo_mypay' : 200000,
#         'kategori': ['Membayar Pemesanan Jasa', 'TopUp MyPay', 'Transfer MyPay', 'Withdrawal'],
#         'jasa' : [jasa1, jasa2, jasa3, jasa4, jasa5, jasa6, jasa7],
#     }
#     # if request.method == 'POST':
#     # dll.. dari form
#     return render(request, 'new_transaction.html', context)

def new_transaction(request):
    user_id = get_cookie(request, 'user_id')
    user_name = get_cookie(request, 'user_name')
    if not user_id:
        return redirect('authentication:login')

    # Fetch saldo mypay
    query_user = "SELECT saldomypay FROM SIJARTA.pengguna WHERE id = %s"
    params_user = [user_id]
    result = execute_query(query_user, params_user)
    print(result)
    if result:
        saldo_mypay = result[0][0]
    else:
        saldo_mypay = None, None
    
    execute_query("SET search_path TO SIJARTA")

    linkfoto = ''
    user_role = get_cookie(request, 'user_role')
    if user_role == 'Pekerja':
        linkfoto = execute_query("SELECT linkfoto FROM sijarta.pekerja WHERE id = %s", [user_id])[0][0]

    # Fetch kategori transaksi
    if user_role == 'Pekerja':
        query_kategori_transaksi = "SELECT id, nama FROM sijarta.kategori_tr_mypay WHERE nama != 'Membayar transaksi jasa' AND nama != 'Menerima honor transaksi jasa'"
    else:
        query_kategori_transaksi = "SELECT id, nama FROM sijarta.kategori_tr_mypay WHERE nama != 'Menerima honor transaksi jasa'"
    kategori_transaksi = execute_query(query_kategori_transaksi)

    # Fetch jasa
    query_jasa = '''SELECT DISTINCT tr.id, namakategori, namasubkategori, totalbiaya FROM sijarta.tr_pemesanan_jasa tr
    JOIN sijarta.subkategori_jasa skj ON tr.idkategorijasa = skj.id
    JOIN sijarta.kategori_jasa kj ON kj.id = skj.kategorijasaid
    JOIN sijarta.tr_pemesanan_status tr_status ON tr_status.idtrpemesanan = tr.id
    WHERE tr.idpelanggan = %s AND
    tr_status.idtrpemesanan IN 
    (SELECT tr_status2.idtrpemesanan FROM 
    sijarta.tr_pemesanan_status tr_status2
    JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
    WHERE sp.status = 'Menunggu Pembayaran')
    AND 
    tr_status.idtrpemesanan NOT IN
    (SELECT tr_status2.idtrpemesanan FROM 
    sijarta.tr_pemesanan_status tr_status2
    JOIN sijarta.status_pesanan sp ON sp.id = tr_status2.idstatus
    WHERE sp.status = 'Terjadi Kesalahan pada Sistem'
    OR sp.status = 'Mencari pekerja'
    OR sp.status = 'Dibatalkan')
    '''
    jasa = execute_query(query_jasa, [user_id])
    pemesanan_jasa = [
        (str(pekerjaan[0]), pekerjaan[1], pekerjaan[2], float(pekerjaan[3]))
        for pekerjaan in jasa
    ]

    tanggal = execute_query("SELECT CURRENT_DATE")

    # Fetch semua bank
    query_nama_bank = "SELECT DISTINCT namabank FROM sijarta.PEKERJA"
    nama_bank = execute_query(query_nama_bank)

    # Prepare context
    context = {
        'pemesanan_jasa': json.dumps(pemesanan_jasa),  
        'user_id': user_id,
        'nama': user_name,
        'saldo_mypay': saldo_mypay,
        'kategori_transaksi': kategori_transaksi,   # menampilkan kategori transaksi yang dapat dilakukan
        'tanggal_transaksi': tanggal[0][0],
        'nama_bank': [bank[0] for bank in nama_bank],  # ambil nama bank
        'user_role': user_role,
        'link_foto': linkfoto,
    }

    if request.method == 'POST':
        transaction_category = request.POST.get('transaction_category')
        # Generate UUID in Python
        transaction_id = str(uuid.uuid4())
        nominal = float(request.POST.get('nominal'))  

        query_update_saldo = '''
            UPDATE pengguna
            SET saldomypay = saldomypay + %s
            WHERE id = %s
            '''
        if nominal <= 0:
            response = redirect('userprofile:new_transaction')
            response.set_cookie('message', 'Nominal harus lebih besar dari 0.', max_age=5)
            return response

        if transaction_category == 'Topup MyPay':
            # Update saldo mypay
            execute_query(query_update_saldo, [nominal, user_id])

            # Insert transaksi
            query_insert_transaction = '''
            INSERT INTO sijarta.tr_mypay VALUES
            (%s, %s, CURRENT_DATE, %s, (SELECT tr.Id FROM sijarta.KATEGORI_TR_MYPAY tr WHERE tr.nama = %s))
            '''
            execute_query(query_insert_transaction, [transaction_id, user_id, nominal, transaction_category])

            response = redirect('userprofile:new_transaction')
            response.set_cookie('message', 'Topup MyPay berhasil.', max_age=5)
            return response
        elif transaction_category == 'Membayar transaksi jasa':
            jasa_id = request.POST.get('jasa')
            # validasi saldo
            if saldo_mypay < nominal:
                response = redirect('userprofile:new_transaction')
                response.set_cookie('message', 'Saldo MyPay tidak mencukupi.', max_age=5)
                return response

            # Update status
            query_update_status = '''
            INSERT INTO sijarta.tr_pemesanan_status VALUES
            (%s, (SELECT Id FROM sijarta.STATUS_PESANAN WHERE Status='Mencari Pekerja'), CURRENT_TIMESTAMP)
            '''
            execute_query(query_update_status, [jasa_id])

            nominal *= -1  # Make nominal negative for payment
            # Insert transaksi
            query_insert_transaction = '''
            INSERT INTO sijarta.tr_mypay VALUES
            (%s, %s, CURRENT_DATE, %s, (SELECT tr.Id FROM sijarta.KATEGORI_TR_MYPAY tr WHERE tr.nama = %s))
            '''
            execute_query(query_insert_transaction, [transaction_id, user_id, nominal, transaction_category])

            # update saldo
            execute_query(query_update_saldo, [nominal, user_id])
            
            response = redirect('userprofile:new_transaction')
            response.set_cookie('message', 'Pembayaran transaksi jasa berhasil.', max_age=5)
            return response
        elif transaction_category == 'Transfer MyPay ke pengguna lain':
            no_hp_tujuan = request.POST.get('no_hp_tujuan') 

            # Validate saldo
            if saldo_mypay < nominal:
                response = redirect('userprofile:new_transaction')
                response.set_cookie('message', 'Saldo MyPay tidak mencukupi.', max_age=5)
                return response

            result = execute_query("SELECT id FROM sijarta.pengguna WHERE nohp = %s", [no_hp_tujuan])
            user_id_lain = result[0][0]
            # Insert transaction terhadap user lain
            query_insert_transaction = '''
            INSERT INTO sijarta.tr_mypay VALUES
            (%s, %s, CURRENT_DATE, %s, (SELECT tr.Id FROM sijarta.KATEGORI_TR_MYPAY tr WHERE tr.nama = %s))
            '''
            execute_query(query_insert_transaction, [transaction_id, user_id_lain, nominal, transaction_category])
            execute_query(query_update_saldo, [nominal, user_id_lain])

            # Insert transaction terhadap user sendiri
            transaction_id = str(uuid.uuid4())
            nominal *= -1
            execute_query(query_insert_transaction, [transaction_id, user_id, nominal, transaction_category])
            execute_query(query_update_saldo, [nominal, user_id])

            
            response = redirect('userprofile:new_transaction')
            response.set_cookie('message', 'Transfer MyPay ke pengguna lain berhasil.', max_age=5)

            return response
        elif transaction_category == 'Withdrawal MyPay ke rekening bank':
            nama_bank = request.POST.get('nama_bank')
            nomor_rekening = request.POST.get('nomor_rekening') # tidak dipedulikan
            
            
            # Validate saldo
            if saldo_mypay < nominal:
                response = redirect('userprofile:new_transaction')
                response.set_cookie('message', 'Saldo MyPay tidak mencukupi.', max_age=5)
                return response
            # Update saldo mypay
            nominal *= -1
            execute_query(query_update_saldo, [nominal, user_id])

            # Insert transaction
            query_insert_transaction = '''
            INSERT INTO sijarta.tr_mypay VALUES
            (%s, %s, CURRENT_DATE, %s, (SELECT tr.Id FROM sijarta.KATEGORI_TR_MYPAY tr WHERE tr.nama = %s))
            '''
            execute_query(query_insert_transaction, [transaction_id, user_id, nominal, transaction_category])

            response = redirect('userprofile:new_transaction')
            response.set_cookie('message', 'Withdrawal berhasil.', max_age=5)
            return response

        return redirect('userprofile:new_transaction')

    return render(request, 'new_transaction.html', context)