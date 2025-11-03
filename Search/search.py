# search.py
from django.db.models import Q
from .models import Document


class DocumentSearch:
    @staticmethod
    def search_documents(query):
        """Поиск документов по текстовому запросу"""
        if not query:
            return Document.objects.none()

        return Document.objects.filter(
            Q(text__icontains=query) |
            Q(rubrics__icontains=query)
        ).distinct().order_by('-created_date')

    @staticmethod
    def search_by_rubrics(rubrics):
        """Поиск документов по рубрикам"""
        if not rubrics:
            return Document.objects.none()

        return Document.objects.filter(
            rubrics__icontains=rubrics
        ).order_by('-created_date')