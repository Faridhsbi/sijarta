from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import psycopg2

# # Create your views here.

@login_required(login_url='/auth')
def show_main(request):
    context = {"user": request.user}   
    return render(request, "main.html", context)


def create_schema(schema_name):
    conn = psycopg2.connect("dbname=your_database user=your_username password=your_password")
    cur = conn.cursor()
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
    conn.commit()
    conn.close()
