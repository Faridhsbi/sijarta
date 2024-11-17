from django.urls import path
from .views import *

app_name = 'userprofile'

urlpatterns = [
    path('', profile_view, name='profile'),
    path('edit-pengguna/', edit_profile_pengguna, name='edit_profile_pengguna'),
    path('edit-pekerja/', edit_profile_pekerja, name='edit_profile_pekerja'),

    
    path('show-edit-pengguna/', show_edit_pengguna, name='show_edit_pengguna'),
    path('show-edit-pekerja/', show_edit_pekerja, name='show_edit_pekerja'),
    path('pengguna/', show_profile_pengguna, name='show_pengguna'),
    path('pekerja/', show_profile_pekerja, name='show_pekerja'),
    path('mypay/', show_mypay, name='show_mypay'),
    path('new-transaction/', new_transaction, name='new_transaction'),
]
