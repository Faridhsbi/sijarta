from datetime import date, timedelta
import json
from uuid import uuid4
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from main.views import get_cookie
from django.views.decorators.csrf import csrf_exempt

def get_user_role(user_id):
    query = "SELECT EXISTS (SELECT 1 FROM sijarta.pelanggan WHERE id = %s)"
    result = execute_query(query, [user_id])
    if result[0][0] == True:
        return "Pelanggan"
    return "Pekerja"

def check_balance(user_id, required_amount):
    """
    Cek saldo pengguna berdasarkan user_id.
    Mengembalikan True jika saldo cukup, False jika tidak.
    """
    query = """
        SELECT saldo 
        FROM sijarta.pengguna 
        WHERE id = %s
    """
    result = execute_query(query, [user_id])
    if result and result[0][0] >= required_amount:
        return True
    return False

@csrf_exempt
def purchase_voucher_ajax(request):
    """
    Handle AJAX untuk pembelian voucher.
    """
    if request.method == "POST":
        data = json.loads(request.body)  # Parse JSON data
        user_id = data.get("user_id")
        voucher_id = data.get("voucher_id")
        payment_method_id = data.get("payment_method_id")
        print(voucher_id)
        print(user_id)

        # Query untuk mendapatkan informasi voucher
        voucher_query = """
            SELECT harga, jmlhariberlaku, kuotapenggunaan 
            FROM sijarta.voucher 
            WHERE kode = %s
        """
        voucher = execute_query(voucher_query, [voucher_id])
        
        if not voucher:
            return JsonResponse({"success": False, "message": "Voucher tidak ditemukan."}, status=404)

        harga_voucher, jml_hari_berlaku, kuota = voucher[0]
        today = date.today()
        expiry_date = today + timedelta(days=jml_hari_berlaku)

        # Jika metode bayar bukan MyPay, langsung berhasil
        method_query = """
            SELECT nama 
            FROM sijarta.metode_bayar 
            WHERE id = %s
        """
        method = execute_query(method_query, [payment_method_id])[0][0]

        if method != "MyPay":
            save_transaction(user_id, voucher_id, payment_method_id, harga_voucher, jml_hari_berlaku, False)
            return JsonResponse({"success": True, 
                                 "message": "Pembelian berhasil!",
                                 "voucher_code": voucher_id,
                                 "expiry_date": expiry_date,
                                 "usage_quota": kuota})

        # Jika metode bayar adalah MyPay, cek saldo
        user_balance_query = """
            SELECT saldoMyPay 
            FROM sijarta.pengguna 
            WHERE id = %s
        """
        user_balance = execute_query(user_balance_query, [user_id])[0][0]
        print("MYPAY BALANCE USER: "+ str(user_balance))

        if user_balance < harga_voucher:
            return JsonResponse({"success": False, "message": "Maaf, saldo Anda tidak cukup untuk membeli voucher ini."})

        # Jika saldo cukup, lakukan transaksi
        save_transaction(user_id, voucher_id, payment_method_id, harga_voucher, jml_hari_berlaku, True)
        return JsonResponse({"success": True, 
                             "message": "Pembelian berhasil menggunakan MyPay!",
                             "voucher_code": voucher_id,
                             "expiry_date": expiry_date,
                             "usage_quota": kuota})


def save_transaction(user_id, voucher_id, payment_method_id, price, validity_days, isUsingMyPay):
    """
    Menyimpan transaksi pembelian voucher ke database.
    """
    transaction_id = str(uuid4())
    transaction_id2 = str(uuid4())
    today = date.today()
    expiry_date = today + timedelta(validity_days)

    query = """
        INSERT INTO sijarta.tr_pembelian_voucher 
        (id, tglawal, tglakhir, telahdigunakan, idpelanggan, idvoucher, idmetodebayar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    if isUsingMyPay:
        # Insert transaksi
        query_update_saldo = '''
            UPDATE sijarta.pengguna
            SET saldomypay = saldomypay + %s
            WHERE id = %s
            '''
        
        execute_query(query_update_saldo, [-1*price, user_id])
        transaction_category = "Membeli voucher"
        query_insert_transaction = '''
            INSERT INTO sijarta.tr_mypay VALUES
            (%s, %s, CURRENT_DATE, %s, (SELECT tr.Id FROM sijarta.KATEGORI_TR_MYPAY tr WHERE tr.nama = %s))
            '''
        execute_query(query_insert_transaction, [transaction_id2, user_id, -1*price, transaction_category])

    print("INSERT INTO SIJARTA.TR_PEMBELIAN_VOUCHER :"+query)
    result = execute_query(query, [transaction_id, today, expiry_date, 0, user_id, voucher_id, payment_method_id])
    print(result)

def discount_page(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id
    
    # ambil name dan role user
    user_name = execute_query("SELECT nama FROM sijarta.pengguna WHERE id=%s", [user_id])[0][0]
    role = get_user_role(user_id)
    if role != "Pelanggan":
        return redirect('main:show_main')
    
    query_promo = "SELECT * FROM sijarta.promo"
    query_voucher = """
        SELECT 
            d.kode, 
            d.potongan, 
            d.mintrpemesanan, 
            v.jmlhariberlaku, 
            v.kuotapenggunaan, 
            v.harga
        FROM 
            sijarta.diskon d
        JOIN 
            sijarta.voucher v 
        ON 
            d.kode = v.kode
    """

    payment_methods_query = """
        SELECT id, nama
        FROM sijarta.metode_bayar
    """

    result_promo = execute_query(query_promo)
    result_voucher = execute_query(query_voucher)
    result_payment_methods = execute_query(payment_methods_query)

    print(result_payment_methods)
    print(result_promo)
    print(result_voucher)

    formatted_voucher = [
        {
            "kode": item[0],
            "potongan": item[1],
            "min_transaksi": item[2],
            "hari_berlaku": item[3],
            "kuota_penggunaan": item[4],
            "harga": item[5],
        }
        for item in result_voucher
    ]

    context = {'promos': result_promo,
               'vouchers': formatted_voucher,
               'payment_methods': result_payment_methods,
               'user_id': user_id,
               'nama': user_name,
               'user_role': role}
    return render(request, "discount_page.html", context)

def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            print(cursor.fetchall)
            return cursor.fetchall()
        else:
            return cursor.rowcount
