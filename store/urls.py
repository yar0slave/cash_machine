from django.urls import path
from .views import CashMachineView, MediaFileView, index

urlpatterns = [
    path('', index, name='index'),
    path('cash_machine/', CashMachineView.as_view(), name='cash_machine'),
    path('media/<str:file_name>', MediaFileView.as_view(), name='media_file'),
]
