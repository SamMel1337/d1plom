from elasticsearch_dsl import Search
from django_elasticsearch_dsl.registries import registry
from .models import DocumentIndex


class DocumentSearch:
    @staticmethod
    def search_documents(query_text):
        search = DocumentIndex.search()

        if query_text:
            search = search.query(
                'match',
                text=query_text
            )

        # Выполняем поиск и получаем ID документов
        response = search.execute()
        document_ids = [hit.iD for hit in response]

        # Получаем документы из БД в правильном порядке
        from .models import Document
        documents = Document.objects.filter(id__in=document_ids)

        # Сохраняем порядок из Elasticsearch
        document_dict = {doc.id: doc for doc in documents}
        ordered_documents = [document_dict[doc_id] for doc_id in document_ids if doc_id in document_dict]

        return ordered_documents[:20]  # Возвращаем первые 20