from django.urls import path
from .views import *

urlpatterns = [
    path('', invoice_list, name='invoice_list'),
    path('invoice/<int:pk>/', invoice_detail, name='invoice_detail'),
    path('invoice/create/', invoice_create, name='invoice_create'),
    path('invoice/<int:pk>/update/', invoice_update, name='invoice_update'),
    path('invoice/<int:pk>/delete/', invoice_delete, name='invoice_delete'),
    path('invoice/<int:pk>/pdf/', invoice_pdf, name='invoice_pdf'),
]
