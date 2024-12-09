from django.shortcuts import render, redirect
from main.views import execute_query, get_cookie, get_user_role

def tambah_testimoni(request, pemesanan_id):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id
    
    # ambil name dan role user
    user_name = execute_query("SELECT nama FROM sijarta.pengguna WHERE id=%s", [user_id])[0][0]
    role = get_user_role(user_id)
    if role != "Pelanggan":
        return redirect('main:show_main')
    
    error_msg = ""

    if request.method == 'POST':
        # Mengambil rating dan teks review dari form
        rating = request.POST.get('rating')
        teks = request.POST.get('teks')

        # Pastikan rating valid
        if rating and teks:
                # Query untuk menyimpan data testimoni ke database PostgreSQL
            execute_query("""
                        INSERT INTO TESTIMONI (IdTrPemesanan, Tgl, Teks, Rating)
                        VALUES (%s, CURRENT_DATE, %s, %s)""", [pemesanan_id, teks, rating])

            print(rating + " " + teks)
            return redirect('main:show_pemesananjasa')  # Ganti dengan URL yang sesuai
        else:
            error_msg = "Rating dan/atau Komentar tidak boleh kosong"
    
    context = {'pemesanan_id': pemesanan_id, 
                'nama': user_name,
                'user_role': role,
                'error_msg': error_msg}

    return render(request, 'form_testimoni.html', context)

def delete_testimoni(request, pemesanan_id):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login') 
    
    user_name = execute_query("SELECT nama FROM sijarta.pengguna WHERE id=%s", [user_id])[0][0]
    role = get_user_role(user_id)

    if role != "Pelanggan":
        return redirect('main:show_main')
    
    print("is it here?")
    check_query = "SELECT idPelanggan from sijarta.TR_PEMESANAN_JASA WHERE id=%s"
    check_result = execute_query(check_query, [pemesanan_id])[0][0]
    
    if user_id != str(check_result):
        return redirect('main:show_pemesananjasa')
    
    print("did it go here nah?")
    delete_query = "DELETE FROM sijarta.TESTIMONI WHERE IdTrPemesanan=%s"
    execute_query(delete_query, [pemesanan_id])
    print("TEST GOT DELETED IF HERE YES IT DID")
    return redirect('main:show_pemesananjasa')