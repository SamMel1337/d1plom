# serializers.py
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField(source='title')

    class Meta:
        model = Document
        fields = ['id', 'rubrics', 'text', 'created_date', 'title']
        read_only_fields = ['id', 'created_date']