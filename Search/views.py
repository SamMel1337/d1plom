from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DeleteView, DetailView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer
from .search import DocumentSearch


# HTML Class-Based Views
class IndexView(View):
    """Главная страница с поиском - доступна всем"""
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


class SearchResultsView(View):
    """Страница результатов поиска - доступна всем"""
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


class CreateDocumentView( View):
    """Создание нового документа - требует авторизации"""
    template_name = 'create_document.html'  # Укажите ваш URL для входа

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
    """Админка для управления документами - требует авторизации"""
    template_name = 'admin_documents.html'

    def get(self, request):
        documents = Document.objects.all().order_by('-created_date')
        return render(request, self.template_name, {
            'documents': documents
        })


class DocumentSearchView(View):
    """Расширенный поиск документов - доступен всем"""
    template_name = 'results.html'
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
            'page': int(request.GET.get('page', 1)),
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


class DocumentDeleteView( DeleteView):
    """Удаление документа - требует авторизации"""
    model = Document
    template_name = 'Search/delete.html'
    uccess_message = 'Запись успешно удалена!'
    success_url = reverse_lazy('Search:admin_documents.html')

    def get_success_url(self):
        messages.success(self.request, f'Документ "{self.object.title}" был успешно удален.')
        return super().get_success_url()
        #return reverse_lazy('Search:admin_documents.html')

    def get_queryset(self):
        return Document.objects.all()


class DocumentDetailView(DetailView):
    """Просмотр деталей документа - доступен всем"""
    model = Document
    template_name = 'document_detail.html'
    context_object_name = 'document'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get('pk')
        slug = self.kwargs.get('slug')

        if pk:
            return get_object_or_404(queryset, pk=pk)
        elif slug:
            return get_object_or_404(queryset, slug=slug)
        else:
            raise Http404("No document found")


# API Views - можно также настроить права доступа
class DocumentListAPIView(APIView):
    """API для списка документов - настройте права по необходимости"""

    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)