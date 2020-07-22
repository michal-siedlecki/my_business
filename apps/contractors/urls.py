from django.urls import path

from .views import ContractorCreateView, ContractorListView, ContractorUpdateView, ContractorDeleteView

urlpatterns = [
    path('contractor/new', ContractorCreateView.as_view(), name='contractor-new'),
    path('contractors', ContractorListView.as_view(), name='contractor-list'),
    path('contractor/<int:pk>/update', ContractorUpdateView.as_view(), name='contractor-update'),
    path('contractor/<int:pk>/delete', ContractorDeleteView.as_view(), name='contractor-delete')
]
