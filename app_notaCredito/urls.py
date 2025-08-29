
from django.urls import path
from app_notaCredito.views.notaCredito import *

app_name = 'app_notaCredito'

urlpatterns = [

    path('credit/note/admin/', CreditNoteListView.as_view(), name='credit_note_admin_list'),
    path('credit/note/admin/add/', CreditNoteCreateView.as_view(), name='credit_note_admin_create'),
    path('credit/note/admin/delete/<int:pk>/', CreditNoteDeleteView.as_view(), name='credit_note_admin_delete'),
    path('credit/note/client/', CreditNoteClientListView.as_view(), name='credit_note_client_list'),

]