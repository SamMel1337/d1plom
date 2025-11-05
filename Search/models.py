from django_elasticsearch_dsl import  fields
from django.db import models
from django.urls import reverse


class Document(models.Model):
    rubrics = models.TextField(verbose_name="Рубрики")
    text = models.TextField(verbose_name="Текст документа")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-created_date']

    def __str__(self):
        return f"Документ {self.id}"

    @property
    def title(self):
        """Генерируем заголовок из первых слов текста"""
        return self.text[:50] + '...' if len(self.text) > 50 else self.text

    def get_absolute_url(self):
        return reverse('document_detail', kwargs={'pk': self.pk})

class DocumentIndex(Document):
    iD = fields.IntegerField(attr='id')
    text = fields.TextField()

    class Index:
        name = 'documents'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Document
        fields = ['created_date']
