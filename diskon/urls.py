from django.urls import path
import diskon.views

app_name = 'diskon'

urlpatterns = [
    path('', diskon.views.discount_page, name='discount_page'),
    path('purchase-voucher/', diskon.views.purchase_voucher_ajax, name='purchase_voucher')
]