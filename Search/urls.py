from django.urls import path
from .views import (
    IndexView,
    SearchResultsView,
    CreateDocumentView,
    AdminDocumentsView,
    DocumentSearchView, DocumentDeleteView, DocumentDetailView,
)
from . import views

app_name = 'Search'

urlpatterns = [
    # HTML Views
    path('', IndexView.as_view(), name='index'),
    path('search/', DocumentSearchView.as_view(), name='search'),
    path('results/', SearchResultsView.as_view(), name='results'),
    path('create/', CreateDocumentView.as_view(), name='create-document'),
    path('admin/', AdminDocumentsView.as_view(), name='admin-documents'),
    path('search/<int:id>/', DocumentDeleteView.as_view(), name='delete'),
    path('document/<int:id>/', views.DocumentDetailView.as_view(), name='document-detail'),

]