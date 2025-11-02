from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Document
from .serializers import DocumentSerializer
from .search import DocumentSearch


# HTML Views
def index(request):
    query = request.GET.get('q', '')
    documents = []

    if query:
        documents = DocumentSearch.search_documents(query)

    return render(request, 'index.html', {
        'query': query,
        'documents': documents
    })


def search_results(request):
    query = request.GET.get('q', '')
    documents = []

    if query:
        documents = DocumentSearch.search_documents(query)

    return render(request, 'search_results.html', {
        'query': query,
        'documents': documents
    })


def create_document_page(request):
    if request.method == 'POST':
        rubrics = [r.strip() for r in request.POST.get('rubrics', '').split(',') if r.strip()]
        text = request.POST.get('text', '')

        if rubrics and text:
            document = Document.objects.create(
                rubrics=rubrics,
                text=text
            )
            messages.success(request, 'Документ успешно создан!')
            return redirect('admin-documents')
        else:
            messages.error(request, 'Заполните все обязательные поля')

    return render(request, 'create_document.html')


def admin_documents(request):
    documents = Document.objects.all().order_by('-created_date')
    return render(request, 'admin_documents.html', {
        'documents': documents
    })


# API Views
@api_view(['GET'])
def search_documents_api(request):
    query = request.GET.get('q', '')

    if not query:
        return Response(
            {'error': 'Query parameter "q" is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    documents = DocumentSearch.search_documents(query)
    serializer = DocumentSerializer(documents, many=True)

    return Response({
        'count': len(documents),
        'results': serializer.data
    })


@api_view(['DELETE'])
def delete_document_api(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    document.delete()

    return Response(
        {'message': f'Document {document_id} deleted successfully'},
        status=status.HTTP_204_NO_CONTENT
    )


@api_view(['POST'])
def create_document_api(request):
    serializer = DocumentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)