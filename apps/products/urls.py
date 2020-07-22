from django.urls import path

from .views import ProductCreateView, ProductListView, ProductUpdateView, ProductDeleteView

urlpatterns = [

    path('product/new', ProductCreateView.as_view(), name='product-new'),
    path('products', ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/update', ProductUpdateView.as_view(), name='product-update'),
    path('product/<int:pk>/delete', ProductDeleteView.as_view(), name='product-delete')

]
