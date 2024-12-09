from django.urls import path
from main.views import show_main, show_subkategori, show_pemesananjasa, join_subcategory, create_pemesanan, cancel_pemesanan

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    # path('subkategori/', show_subkategori, name='show_subkategori'),
    path('subkategori/<uuid:subcategory_id>/', show_subkategori, name='show_subkategori'),
    path('<uuid:subcategory_id>/join/', join_subcategory, name='join'),
    path('pemesananjasa/', show_pemesananjasa, name='show_pemesananjasa'),
    path('create-pemesanan/', create_pemesanan, name='create_pemesanan'),
    path('cancel_pemesanan/', cancel_pemesanan, name='cancel_pemesanan'),
]