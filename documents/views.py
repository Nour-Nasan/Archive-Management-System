import os
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from .forms import DocumentForm, DocumentFileForm, VersionUploadForm
from .models import Document, DocumentFile, Department, DocumentType, DocumentLog
from .utils import log_action, diff_document


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _can_upload(user):
    """Managers and System Administrators may upload new versions."""
    return user.is_superuser or user.is_manager()


def _next_version(doc):
    """Return the next safe version number for a document (max existing + 1)."""
    max_v = doc.files.order_by('-version').values_list('version', flat=True).first()
    return (max_v or 0) + 1


# ─── Document CRUD ────────────────────────────────────────────────────────────

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

            # ── Audit: document created ──────────────────────────────────
            details_parts = [
                f'Title: {doc.title}',
                f'Document Number: {doc.document_number}',
                f'Type: {doc.document_type or "—"}',
                f'Department: {doc.department or "—"}',
                f'Status: {doc.get_status_display()}',
            ]
            log_action(doc, request.user, DocumentLog.ACTION_CREATED,
                       '\n'.join(details_parts))

            uploaded = request.FILES.get('file')
            if uploaded:
                version = _next_version(doc)
                DocumentFile.objects.create(
                    document=doc,
                    file=uploaded,
                    original_name=uploaded.name,
                    file_type=os.path.splitext(uploaded.name)[1].lstrip('.').lower(),
                    file_size=uploaded.size,
                    uploaded_by=request.user,
                    version=version,
                    notes='Initial version uploaded with document.',
                )
                log_action(doc, request.user, DocumentLog.ACTION_FILE_UPLOADED,
                           f'File: {uploaded.name} (v{version}, {uploaded.size:,} bytes)\n'
                           f'Notes: Initial version uploaded with document.')

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
    # Versions ordered newest first (by version DESC — set in model Meta)
    versions = doc.files.select_related('uploaded_by').order_by('-version')

    logs = doc.logs.select_related('user').order_by('-timestamp')

    return render(request, 'documents/document_detail.html', {
        'document': doc,
        'versions': versions,
        'logs': logs,
        'can_upload': _can_upload(request.user),
    })


@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        # ── Snapshot BEFORE save ─────────────────────────────────────────
        old = {
            'title': doc.title,
            'document_number': doc.document_number,
            'description': doc.description or '',
            'document_date': str(doc.document_date),
            'status': doc.status,
            'document_type_id': doc.document_type_id,
            'department_id': doc.department_id,
            '__document_type_name': str(doc.document_type) if doc.document_type else '—',
            '__department_name': str(doc.department) if doc.department else '—',
        }
        old_status = doc.status

        form = DocumentForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            doc.refresh_from_db()

            # ── Compute field-level diff ─────────────────────────────────
            new_data = {
                'title': doc.title,
                'document_number': doc.document_number,
                'description': doc.description or '',
                'document_date': str(doc.document_date),
                'status': doc.status,
                'document_type_id': doc.document_type_id,
                'department_id': doc.department_id,
                'document_type': doc.document_type,
                'department': doc.department,
            }
            changes, status_changed = diff_document(old, new_data, doc)

            if changes:
                log_action(doc, request.user, DocumentLog.ACTION_EDITED,
                           '\n'.join(changes))

            if status_changed:
                old_label = dict(Document.STATUS_CHOICES).get(old_status, old_status)
                new_label = doc.get_status_display()
                log_action(doc, request.user, DocumentLog.ACTION_STATUS_CHANGED,
                           f'Status changed from "{old_label}" to "{new_label}"')

            messages.success(request, 'Document updated successfully.')
            return redirect('documents:document_detail', pk=doc.pk)
    else:
        form = DocumentForm(instance=doc)

    return render(request, 'documents/document_form.html', {
        'form': form,
        'action': 'Edit',
        'document': doc,
    })


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        log_action(doc, request.user, DocumentLog.ACTION_DELETED,
                   f'Document "{doc.title}" ({doc.document_number}) permanently deleted '
                   f'({doc.files.count()} file version(s) removed).')
        doc.delete()
        messages.success(request, 'Document deleted.')
        return redirect('documents:document_list')
    return render(request, 'documents/document_confirm_delete.html', {'document': doc})


# ─── Version Upload ────────────────────────────────────────────────────────────

@login_required
def document_upload_version(request, pk):
    doc = get_object_or_404(
        Document.objects.select_related('document_type', 'department'),
        pk=pk,
    )

    # Server-side permission: managers and superusers only
    if not _can_upload(request.user):
        messages.error(request, 'You do not have permission to upload file versions.')
        return redirect('documents:document_detail', pk=doc.pk)

    if request.method == 'POST':
        form = VersionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['file']
            notes = form.cleaned_data.get('notes', '').strip()
            version = _next_version(doc)

            DocumentFile.objects.create(
                document=doc,
                file=uploaded,
                original_name=uploaded.name,
                file_type=os.path.splitext(uploaded.name)[1].lstrip('.').lower(),
                file_size=uploaded.size,
                uploaded_by=request.user,
                version=version,
                notes=notes,
            )

            # ── Audit log ─────────────────────────────────────────────────
            log_detail_parts = [
                f'File: {uploaded.name}',
                f'Version: v{version}',
                f'Size: {uploaded.size:,} bytes',
            ]
            if notes:
                log_detail_parts.append(f'Notes: {notes}')
            log_action(doc, request.user, DocumentLog.ACTION_FILE_UPLOADED,
                       '\n'.join(log_detail_parts))

            messages.success(request,
                             f'Version v{version} uploaded successfully: {uploaded.name}')
            return redirect('documents:document_detail', pk=doc.pk)
    else:
        form = VersionUploadForm()

    next_ver = _next_version(doc)
    return render(request, 'documents/document_upload_version.html', {
        'document': doc,
        'form': form,
        'next_version': next_ver,
    })
