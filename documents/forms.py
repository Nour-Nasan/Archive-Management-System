import os
from django import forms
from .models import Document, DocumentFile, Department, DocumentType


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'title', 'document_number', 'document_type', 'department',
            'description', 'document_date', 'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class DocumentFileForm(forms.Form):
    """Lightweight form used only during document creation for the optional first file."""
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Attach file (optional)',
    )


class VersionUploadForm(forms.Form):
    """Dedicated form for uploading a new document version."""
    file = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label='Select file',
        error_messages={'required': 'Please select a file to upload.'},
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional: describe what changed in this version…',
        }),
        label='Version notes (optional)',
        max_length=1000,
    )
