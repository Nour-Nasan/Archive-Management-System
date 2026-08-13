from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from accounts.decorators import manager_required
from accounts.models import User
from documents.models import Document, DocumentFile, Department, DocumentType, DocumentLog


@login_required
@manager_required
def manager_dashboard(request):
    return render(request, 'dashboard/manager_dashboard.html')


@login_required
def employee_dashboard(request):
    return render(request, 'dashboard/employee_dashboard.html')


@login_required
@manager_required
def reports(request):
    # ── Date filter params ────────────────────────────────────────────────
    date_from = request.GET.get('date_from', '').strip()
    date_to   = request.GET.get('date_to',   '').strip()

    # Base document queryset, optionally narrowed by document_date
    doc_qs = Document.objects.all()
    if date_from:
        try:
            doc_qs = doc_qs.filter(document_date__gte=date_from)
        except (ValueError, TypeError):
            date_from = ''
    if date_to:
        try:
            doc_qs = doc_qs.filter(document_date__lte=date_to)
        except (ValueError, TypeError):
            date_to = ''

    # ── Summary statistics ────────────────────────────────────────────────
    total_docs    = doc_qs.count()
    active_docs   = doc_qs.filter(status='active').count()
    archived_docs = doc_qs.filter(status='archived').count()
    total_depts   = Department.objects.count()
    total_types   = DocumentType.objects.count()
    total_users   = User.objects.filter(is_active=True).count()
    total_files   = DocumentFile.objects.count()

    # ── Documents by department ───────────────────────────────────────────
    # Annotate every department with the count of docs within the date window
    by_dept = (
        Department.objects
        .annotate(doc_count=Count(
            'document',
            filter=Q(document__in=doc_qs),
        ))
        .order_by('-doc_count', 'name')
    )

    # ── Documents by document type ────────────────────────────────────────
    by_type = (
        DocumentType.objects
        .annotate(doc_count=Count(
            'document',
            filter=Q(document__in=doc_qs),
        ))
        .order_by('-doc_count', 'name')
    )

    # ── Documents by status ───────────────────────────────────────────────
    status_labels = dict(Document.STATUS_CHOICES)
    by_status = []
    for val, label in Document.STATUS_CHOICES:
        by_status.append({
            'status': val,
            'label':  label,
            'count':  doc_qs.filter(status=val).count(),
        })

    # ── Recent activity (always all-time — not date filtered) ─────────────
    recent_logs = (
        DocumentLog.objects
        .select_related('user')
        .order_by('-timestamp')[:10]
    )

    # ── User activity: documents created per user ─────────────────────────
    user_activity = (
        User.objects
        .annotate(doc_count=Count(
            'created_documents',
            filter=Q(created_documents__in=doc_qs),
        ))
        .filter(doc_count__gt=0)
        .order_by('-doc_count', 'username')
    )

    context = {
        # Summary
        'total_docs':    total_docs,
        'active_docs':   active_docs,
        'archived_docs': archived_docs,
        'total_depts':   total_depts,
        'total_types':   total_types,
        'total_users':   total_users,
        'total_files':   total_files,
        # Breakdowns
        'by_dept':       by_dept,
        'by_type':       by_type,
        'by_status':     by_status,
        # Activity
        'recent_logs':   recent_logs,
        'user_activity': user_activity,
        # Date filter state
        'date_from':        date_from,
        'date_to':          date_to,
        'is_date_filtered': bool(date_from or date_to),
    }
    return render(request, 'dashboard/reports.html', context)
