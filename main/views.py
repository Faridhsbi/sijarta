from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import psycopg2
from django.db import connection

# # Create your views here.
def get_cookie(request, key):
    return request.COOKIES.get(key)

def get_user_role(user_id):
    query = "SELECT EXISTS (SELECT 1 FROM sijarta.pelanggan WHERE id = %s)"
    result = execute_query(query, [user_id])
    if result[0][0] == True:
        return "Pelanggan"
    return "Pekerja"

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


# @login_required(login_url='/auth')
from django.shortcuts import render, redirect

def show_main(request):
    user_id = get_cookie(request, 'user_id')
    if not user_id:
        return redirect('/auth/')
    
    user_role = get_user_role(user_id)
    user_name = None
    if user_id:
        # Fetch user's name
        user_query = "SELECT nama FROM SIJARTA.pengguna WHERE id = %s"
        user_result = execute_query(user_query, [user_id])
        if user_result:
            user_name = user_result[0][0]

    linkfoto = ''
    if user_role == 'Pekerja':
        # Fetch photo link for workers
        foto_query = "SELECT linkfoto FROM sijarta.pekerja WHERE id = %s"
        foto_result = execute_query(foto_query, [user_id])
        if foto_result:
            linkfoto = foto_result[0][0]

    # Fetch categories and their subcategories
    categories_query = "SELECT id, namakategori FROM sijarta.kategori_jasa"
    categories = execute_query(categories_query)
    subcategories_query = "SELECT id, namasubkategori, kategorijasaid FROM sijarta.subkategori_jasa"
    subcategories = execute_query(subcategories_query)

    # Organize subcategories by their parent category
    subcategories_by_category = {}
    for subcategory in subcategories:
        category_list = subcategories_by_category.setdefault(subcategory[2], [])
        category_list.append({
            "id": subcategory[0],
            "name": subcategory[1]
        })

    categories_with_subcategories = [
        {
            "id": category[0],
            "name": category[1],
            "subcategories": subcategories_by_category.get(category[0], [])
        } for category in categories
    ]

    # Prepare context with all necessary data
    context = {
        'user_id': user_id,
        'nama': user_name,
        'user_role': user_role,
        'link_foto': linkfoto,
        'categories': categories_with_subcategories
    }

    print(user_name)  # Optional: remove or comment this out in production for security
    return render(request, "homepage.html", context)


# # @login_required(login_url='/auth')
# def show_subkategori(request):
#     context = {"user": request.user}   
#     if request.user.role == "pengguna" :
#         return render(request, "subkategori_pengguna.html", context)
#     else :
#         return render(request, "subkategori_pekerja.html", context)

# ini yang baru tar - Daffa
def show_subkategori(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id
    
    # ambil name dan role user
    user_name = execute_query("SELECT nama FROM sijarta.pengguna WHERE id=%s", [user_id])[0][0]
    role = get_user_role(user_id)
    
    testimoni_all_query = """
        SELECT pelanggan.nama AS Pelanggan, pekerja.nama AS Pekerja, 
               subkategori_jasa.NamaSubkategori AS KategoriJasa, 
               testimoni.Tgl, testimoni.teks, testimoni.Rating
        FROM sijarta.TESTIMONI testimoni
        JOIN sijarta.TR_PEMESANAN_JASA pemesanan ON testimoni.IdTrPemesanan = pemesanan.Id
        JOIN sijarta.PENGGUNA pelanggan ON pemesanan.IdPelanggan = pelanggan.Id
        JOIN sijarta.PENGGUNA pekerja ON pemesanan.IdPekerja = pekerja.Id
        JOIN sijarta.SUBKATEGORI_JASA subkategori_jasa ON pemesanan.IdKategoriJasa = subkategori_jasa.Id"""
    

    testimoni_pekerja_query = """
        SELECT pelanggan.nama AS Pelanggan, pekerja.nama AS Pekerja, 
               subkategori_jasa.NamaSubkategori AS KategoriJasa, 
               testimoni.Tgl, testimoni.teks, testimoni.Rating
        FROM sijarta.TESTIMONI testimoni
        JOIN sijarta.TR_PEMESANAN_JASA pemesanan ON testimoni.IdTrPemesanan = pemesanan.Id
        JOIN sijarta.PENGGUNA pelanggan ON pemesanan.IdPelanggan = pelanggan.Id
        JOIN sijarta.PENGGUNA pekerja ON pemesanan.IdPekerja = pekerja.Id
        JOIN sijarta.SUBKATEGORI_JASA subkategori_jasa ON pemesanan.IdKategoriJasa = subkategori_jasa.Id
        WHERE pekerja.nama = %s"""
    linkfoto = ''
    if (role == "Pelanggan"):
        testimoni_all_result = execute_query(testimoni_all_query)
        print(testimoni_all_result)
        # Add stars for each rating
        testimoni_with_stars = [
        {
            "nama_pelanggan": t[0],
            "nama_pekerja": t[1],
            "nama_jasa": t[2],
            "tanggal": t[3],
            "review": t[4],
            "stars": "⭐" * t[5],  # Generate stars based on rating
        }
        for t in testimoni_all_result
        ]
    else:
        testimoni_pekerja_result = execute_query(testimoni_pekerja_query, [user_name])
        print(testimoni_pekerja_result)
        linkfoto = execute_query("SELECT linkfoto FROM sijarta.pekerja WHERE id = %s", [user_id])[0][0]
        # Add stars for each rating
        testimoni_with_stars = [
        {
            "nama_pelanggan": t[0],
            "nama_pekerja": t[1],
            "nama_jasa": t[2],
            "tanggal": t[3],
            "review": t[4],
            "stars": "⭐" * t[5],  # Generate stars based on rating
        }
        for t in testimoni_pekerja_result
        ]

    
    
    context_pelanggan = {'nama': user_name,
               'user_role': role,
               'testimoni_all': testimoni_with_stars}
    
    context_pekerja = {'nama': user_name,
                         'user_role': role,
                         'testimoni_all': testimoni_with_stars,
                         'link_foto': linkfoto}
    
    if role == "Pelanggan":
        return render(request, "subkategori_pengguna.html", context_pelanggan)
    else:
        return render(request, "subkategori_pekerja.html", context_pekerja)

# @login_required(login_url='/auth')
def show_pemesananjasa(request):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id
    
    # ambil name dan role user
    user_name = execute_query("SELECT nama FROM sijarta.pengguna WHERE id=%s", [user_id])[0][0]
    role = get_user_role(user_id)
    dummy_uuid = str(uuid4()) # buat ngetes testimoni

    if role != "Pelanggan":
        return redirect('main:show_main')
    context = {'nama': user_name,
               'user_role': role,
               'pemesanan_id': dummy_uuid}   

    return render(request, "pemesanan_jasa.html", context)

# def create_schema(schema_name):
#     conn = psycopg2.connect("dbname=your_database user=your_username password=your_password")
#     cur = conn.cursor()
#     cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
#     conn.commit()
#     conn.close()
#     return render(request, "homepage.html", context)
