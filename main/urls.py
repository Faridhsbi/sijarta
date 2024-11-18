from django.urls import path
from main.views import show_main, show_subkategori, show_pemesananjasa

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('subkategori/', show_subkategori, name='show_subkategori'),
    path('pemesananjasa/', show_pemesananjasa, name='show_pemesananjasa')
]