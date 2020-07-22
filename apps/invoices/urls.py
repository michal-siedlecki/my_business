from django.urls import path

from . import views
from .views import \
    InvoiceDetailView, \
    InvoiceCreateView, \
    InvoiceUpdateView, \
    InvoiceDeleteView, \
    InvoiceListView, \
    InvoiceDownloadView

urlpatterns = [
    path('invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoice/new/', InvoiceCreateView.as_view(), name='invoice-new'),
    path('invoice/<int:pk>/update', InvoiceUpdateView.as_view(), name='invoice-update'),
    path('invoice/<int:pk>/delete', InvoiceDeleteView.as_view(), name='invoice-delete'),
    path('invoice/<int:pk>/download', InvoiceDownloadView.as_view(), name='invoice-download'),
    path('', views.about, name='about'),
    path('about/', views.about, name='about'),
    path('dashboard/', InvoiceListView.as_view(), name='dashboard')
]
