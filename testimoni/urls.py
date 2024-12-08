from django.urls import path
import testimoni.views

app_name = 'testimoni'

urlpatterns = [
    path('<uuid:pemesanan_id>/', testimoni.views.tambah_testimoni, name='form_testimoni'),
    path('delete/<uuid:pemesanan_id>/', testimoni.views.delete_testimoni, name='delete_testimoni'),
]