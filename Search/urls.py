from django.urls import path
from . import views

urlpatterns = [
    # HTML URLs
    path('', views.index, name='index'),
    path('search/', views.search_results, name='search-results'),
    path('create/', views.create_document_page, name='create-document-page'),
    path('admin/documents/', views.admin_documents, name='admin-documents'),

]