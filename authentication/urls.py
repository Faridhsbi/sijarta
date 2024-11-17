from django.urls import path
from .views import *

app_name = 'authentication'

urlpatterns = [
    path('', landing_page, name='landing'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('choose-role/', choose_role, name='choose_role'),
    path('register-pengguna/', register_pengguna, name='register_pengguna'),  # Form registrasi Pengguna
    path('register-pekerja/', register_pekerja, name='register_pekerja'),  # Form registrasi Pekerja

]