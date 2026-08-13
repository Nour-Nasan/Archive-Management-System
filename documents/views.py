import os
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import DocumentForm, DocumentFileForm
from .models import Document, DocumentFile, Department, DocumentType


@login_required
def document_list(request):
    qs = Document.objects.select_related('document_type', 'department', 'created_by')

    q = request.GET.get('q', '').strip()
    dept_id = request.GET.get('department', '')
    dtype_id = request.GET.get('document_type', '')

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(document_number__icontains=q))
    if dept_id:
        qs = qs.filter(department_id=dept_id)
    if dtype_id:
        qs = qs.filter(document_type_id=dtype_id)

    context = {
        'documents': qs,
        'departments': Department.objects.all(),
        'document_types': DocumentType.objects.all(),
        'q': q,
        'selected_dept': dept_id,
        'selected_dtype': dtype_id,
    }
    return render(request, 'documents/document_list.html', context)


@login_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        file_form = DocumentFileForm(request.POST, request.FILES)
        if form.is_valid() and file_form.is_valid():
            doc = form.save(commit=False)
            doc.created_by = request.user
            doc.save()

            uploaded = request.FILES.get('file')
            if uploaded:
                DocumentFile.objects.create(
                    document=doc,
                    file=uploaded,
                    original_name=uploaded.name,
                    file_type=os.path.splitext(uploaded.name)[1].lstrip('.').lower(),
                    file_size=uploaded.size,
                    uploaded_by=request.user,
                    version=1,
                )

            messages.success(request, 'Document created successfully.')
            return redirect('documents:document_detail', pk=doc.pk)
    else:
        form = DocumentForm()
        file_form = DocumentFileForm()

    return render(request, 'documents/document_form.html', {
        'form': form,
        'file_form': file_form,
        'action': 'Add',
    })


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(
        Document.objects.select_related('document_type', 'department', 'created_by'),
        pk=pk,
    )
    files = doc.files.select_related('uploaded_by').all()
    return render(request, 'documents/document_detail.html', {'document': doc, 'files': files})


@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=doc)
        file_form = DocumentFileForm(request.POST, request.FILES)
        if form.is_valid() and file_form.is_valid():
            form.save()

            uploaded = request.FILES.get('file')
            if uploaded:
                next_version = (doc.files.order_by('-version').values_list('version', flat=True).first() or 0) + 1
                DocumentFile.objects.create(
                    document=doc,
                    file=uploaded,
                    original_name=uploaded.name,
                    file_type=os.path.splitext(uploaded.name)[1].lstrip('.').lower(),
                    file_size=uploaded.size,
                    uploaded_by=request.user,
                    version=next_version,
                )

            messages.success(request, 'Document updated successfully.')
            return redirect('documents:document_detail', pk=doc.pk)
    else:
        form = DocumentForm(instance=doc)
        file_form = DocumentFileForm()

    return render(request, 'documents/document_form.html', {
        'form': form,
        'file_form': file_form,
        'action': 'Edit',
        'document': doc,
    })


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        doc.delete()
        messages.success(request, 'Document deleted.')
        return redirect('documents:document_list')
    return render(request, 'documents/document_confirm_delete.html', {'document': doc})
