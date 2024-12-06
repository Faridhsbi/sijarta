from django.urls import path
from pekerjaan_app.views import *

app_name = 'pekerjaan_app'

urlpatterns = [
    path('', show_pekerjaan, name='show_pekerjaan'),
    path('status/', show_status_pekerjaan, name='show_status_pekerjaan'),
    path('kerjakan/', handle_kerjakan_pesanan, name='handle_kerjakan_pesanan'),
]
