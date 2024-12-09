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
def show_subkategori(request, subcategory_id):
    user_id = get_cookie(request, 'user_id')  # Ambil user_id dari cookies
    if not user_id:
        return redirect('authentication:login')  # Redirect jika tidak ada user_id
    
    # ambil name dan role user
    user_name = execute_query("SELECT nama FROM sijarta.pengguna WHERE id=%s", [user_id])[0][0]
    role = get_user_role(user_id)

    # Fetch subcategory details
    subcategory_details_query = """
        SELECT namaSubkategori, deskripsi FROM sijarta.subkategori_jasa WHERE id = %s
    """
    subcategory_details = execute_query(subcategory_details_query, [subcategory_id])

    # Fetch services offered in this subcategory
    services_query = """
        SELECT sesi, harga FROM sijarta.sesi_layanan WHERE subkategoriid = %s
    """
    raw_services = execute_query(services_query, [subcategory_id])
    services = [{'sesi': service[0], 'harga': service[1]} for service in raw_services]

    category_id_query = """
            SELECT KategoriJasaId
            FROM sijarta.subkategori_jasa
            WHERE Id = %s
        """
    
    category_id = execute_query(category_id_query, [subcategory_id])

    # Fetch workers in this subcategory
    workers_query = """
            SELECT peng.nama, pekerja.rating, pekerja.linkfoto 
            FROM sijarta.pengguna AS peng
            JOIN sijarta.pekerja ON peng.id = pekerja.id
            JOIN sijarta.pekerja_kategori_jasa AS pkj ON pkj.pekerjaid = pekerja.id
            WHERE pkj.kategorijasaid = %s
        """
    raw_workers = execute_query(workers_query, [category_id][0])
    workers = [{'nama': worker[0], 'rating': worker[1], 'linkfoto': worker[2]} for worker in raw_workers]
    
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
               'testimoni_all': testimoni_with_stars,
               'subcategory_details': subcategory_details[0] if subcategory_details else (None, None),
                'services': services,
                'workers': workers,}
    
    context_pekerja = {'nama': user_name,
                         'user_role': role,
                         'testimoni_all': testimoni_with_stars,
                         'subcategory_details': subcategory_details[0] if subcategory_details else (None, None),
                        'services': services,
                        'workers': workers,
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
    # Fetch data pemesanan
    pemesanan_query = """
SELECT 
    jasa.Id AS pemesanan_id,
    jasa.TglPemesanan,
    jasa.TotalBiaya,
    kategori.NamaKategori,
    status.Status
FROM 
    sijarta.tr_pemesanan_jasa AS jasa
JOIN 
    sijarta.sesi_layanan AS sesi ON jasa.IdKategoriJasa = sesi.SubkategoriId AND jasa.Sesi = sesi.Sesi
JOIN 
    sijarta.subkategori_jasa AS subkategori ON sesi.SubkategoriId = subkategori.Id
JOIN 
    sijarta.kategori_jasa AS kategori ON subkategori.KategoriJasaId = kategori.Id
JOIN 
    sijarta.tr_pemesanan_status AS tr_status ON jasa.Id = tr_status.IdTrPemesanan
JOIN 
    sijarta.status_pesanan AS status ON tr_status.IdStatus = status.Id
WHERE 
    jasa.IdPelanggan = %s
ORDER BY 
    jasa.TglPemesanan DESC;

"""
    check_have_testimoni = "SELECT trpj.id FROM sijarta.testimoni t JOIN sijarta.tr_pemesanan_jasa trpj ON t.idTrPemesanan = trpj.id where trpj.idPelanggan = %s"
    pemesanan_data = execute_query(pemesanan_query, [user_id])

    have_testimoni = execute_query(check_have_testimoni, [user_id])[0]
    print(have_testimoni)

    context = {
        'nama': user_name,
        'user_role': role,
        'pemesanan': [{'no': idx + 1,
                       'nama_layanan': p[3],
                       'tanggal_pemesanan': p[1].strftime('%Y-%m-%d'),
                       'total_biaya': f"Rp {p[2]:,.0f}",
                       'status': p[4],
                       'pemesanan_id': p[0],
                       'ada_testimoni': p[0] in have_testimoni} for idx, p in enumerate(pemesanan_data)]
    }

    return render(request, "pemesanan_jasa.html", context)


# def create_schema(schema_name):
#     conn = psycopg2.connect("dbname=your_database user=your_username password=your_password")
#     cur = conn.cursor()
#     cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
#     conn.commit()
#     conn.close()
#     return render(request, "homepage.html", context)
