from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Document

class DocumentAPITestCase(APITestCase):
    def setUp(self):
        self.document = Document.objects.create(
            rubrics=['rubric1', 'rubric2'],
            text='Test document text for searching'
        )

    def test_search_documents(self):
        url = reverse('search-documents')
        response = self.client.get(url, {'q': 'searching'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_delete_document(self):
        url = reverse('delete-document', args=[self.document.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Document.objects.filter(id=self.document.id).exists())

    def test_create_document(self):
        url = reverse('create-document')
        data = {
            'rubrics': ['new_rubric'],
            'text': 'New document text'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 2)