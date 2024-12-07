from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import psycopg2
from django.db import connection
# # Create your views here.
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


# @login_required(login_url='/auth')
def show_main(request):
    user_id = get_cookie(request, 'user_id')
    user_role = get_cookie(request, 'user_role')
    if not user_id:
        return redirect('/auth/')
    user_name = None
    if user_id:
        query = "SELECT nama FROM SIJARTA.pengguna WHERE id = %s"
        params = [user_id]
        result = execute_query(query, params)
        if result:
            user_name = result[0][0]
    context = {
        'user_id': user_id,
        'user_name': user_name,
        'user_role' : user_role
    }
    print(user_name)
    return render(request, "homepage.html", context)

# @login_required(login_url='/auth')
def show_subkategori(request):
    context = {"user": request.user}   
    if request.user.role == "pengguna" :
        return render(request, "subkategori_pengguna.html", context)
    else :
        return render(request, "subkategori_pekerja.html", context)

# @login_required(login_url='/auth')
def show_pemesananjasa(request):
    context = {"user": request.user}   
    if request.user.role == "pengguna" :
        return render(request, "pemesanan_jasa.html", context)

# def create_schema(schema_name):
#     conn = psycopg2.connect("dbname=your_database user=your_username password=your_password")
#     cur = conn.cursor()
#     cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
#     conn.commit()
#     conn.close()
#     return render(request, "homepage.html", context)
