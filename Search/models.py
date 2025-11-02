from django.db import models
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Document(models.Model):
    rubrics = models.JSONField(help_text="Массив рубрик")
    text = models.TextField(help_text="Текст документа")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"Document {self.id}"

@registry.register_document
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

# Сигналы для автоматического обновления индекса
@receiver(post_save, sender=Document)
def update_document_index(sender, instance, **kwargs):
    DocumentIndex().update(instance)

@receiver(post_delete, sender=Document)
def delete_document_index(sender, instance, **kwargs):
    DocumentIndex().delete(instance)