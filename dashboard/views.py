from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from accounts.decorators import manager_required, superuser_required
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
@superuser_required
def audit_log(request):
    qs = DocumentLog.objects.select_related('user', 'document').order_by('-timestamp')

    # ── Filters ───────────────────────────────────────────────────────────
    f_action   = request.GET.get('action',   '').strip()
    f_user     = request.GET.get('user',     '').strip()
    f_keyword  = request.GET.get('keyword',  '').strip()
    f_date_from = request.GET.get('date_from', '').strip()
    f_date_to   = request.GET.get('date_to',   '').strip()

    if f_action:
        qs = qs.filter(action=f_action)
    if f_user:
        qs = qs.filter(user_id=f_user)
    if f_keyword:
        qs = qs.filter(
            Q(document_number__icontains=f_keyword) |
            Q(document_title__icontains=f_keyword)
        )
    if f_date_from:
        try:
            qs = qs.filter(timestamp__date__gte=f_date_from)
        except (ValueError, TypeError):
            f_date_from = ''
    if f_date_to:
        try:
            qs = qs.filter(timestamp__date__lte=f_date_to)
        except (ValueError, TypeError):
            f_date_to = ''

    is_filtered = any([f_action, f_user, f_keyword, f_date_from, f_date_to])
    total_count = qs.count()

    # ── Pagination (50 per page) ──────────────────────────────────────────
    paginator   = Paginator(qs, 50)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)

    # Preserve filter params in pagination links
    filter_params = request.GET.copy()
    filter_params.pop('page', None)

    context = {
        'page_obj':      page_obj,
        'total_count':   total_count,
        'is_filtered':   is_filtered,
        'filter_params': filter_params.urlencode(),
        # Filter state
        'f_action':    f_action,
        'f_user':      f_user,
        'f_keyword':   f_keyword,
        'f_date_from': f_date_from,
        'f_date_to':   f_date_to,
        # Drop-down data
        'action_choices': DocumentLog.ACTION_CHOICES,
        'log_users': (
            User.objects
            .filter(document_logs__isnull=False)
            .distinct()
            .order_by('username')
        ),
    }
    return render(request, 'dashboard/audit_log.html', context)


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
