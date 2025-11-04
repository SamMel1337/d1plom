# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .search import DocumentSearch


# HTML Class-Based Views
class IndexView(View):
    """Главная страница с поиском"""
    template_name = 'index.html'

    def get(self, request):
        query = request.GET.get('q', '')
        documents = []

        if query:
            documents = DocumentSearch.search_documents(query)

        return render(request, self.template_name, {
            'query': query,
            'documents': documents
        })


class SearchResultsView(View):
    """Страница результатов поиска"""
    template_name = 'results.html'

    def get(self, request):
        query = request.GET.get('q', '')
        documents = []

        if query:
            documents = DocumentSearch.search_documents(query)

        return render(request, self.template_name, {
            'query': query,
            'documents': documents
        })


class CreateDocumentView(View):
    """Создание нового документа"""
    template_name = 'create_document.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        rubrics = [r.strip() for r in request.POST.get('rubrics', '').split(',') if r.strip()]
        text = request.POST.get('text', '')

        if rubrics and text:
            # Сохраняем рубрики как строку
            document = Document.objects.create(
                rubrics=', '.join(rubrics),  # Сохраняем как строку
                text=text
            )
            messages.success(request, 'Документ успешно создан!')
            return redirect('Search:admin-documents')
        else:
            messages.error(request, 'Заполните все обязательные поля')

        return render(request, self.template_name)


class AdminDocumentsView(View):
    """Админка для управления документами"""
    template_name = 'admin_documents.html'

    def get(self, request):
        documents = Document.objects.all().order_by('-created_date')
        return render(request, self.template_name, {
            'documents': documents
        })


class DocumentSearchView(View):
    """Расширенный поиск документов"""
    template_name = 'search.html'
    results_per_page = 10

    def get(self, request):
        return self._handle_search(request)

    def _handle_search(self, request):
        search_params = self._extract_search_params(request)
        search_results = self._execute_search(search_params)
        page_obj = self._paginate_results(search_results, search_params['page'])

        context = self._build_context(search_params, page_obj)
        return render(request, self.template_name, context)

    def _extract_search_params(self, request):
        return {
            'query': request.GET.get('q', '').strip(),
            'title_only': bool(request.GET.get('title_only')),
            'category': request.GET.get('category', ''),
            'sort': request.GET.get('sort', 'relevance'),
            'page': request.GET.get('page', 1),
        }

    def _execute_search(self, params):
        if not params['query']:
            return Document.objects.none()

        # Используем DocumentSearch для поиска
        return DocumentSearch.search_documents(params['query'])

    def _paginate_results(self, queryset, page_number):
        paginator = Paginator(queryset, self.results_per_page)
        try:
            return paginator.get_page(page_number)
        except:
            return paginator.get_page(1)

    def _build_context(self, params, page_obj):
        return {
            'query': params['query'],
            'results': page_obj,
            'title_only': params['title_only'],
            'category': params['category'],
            'sort': params['sort'],
            'sort_options': [
                ('relevance', 'По релевантности'),
                ('newest', 'Сначала новые'),
                ('oldest', 'Сначала старые'),
            ]
        }
