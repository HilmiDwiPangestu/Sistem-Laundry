import csv
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localdate, localtime, now
from django.utils.dateparse import parse_date
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from app.nota.forms import (
    HargaLayananSettingsForm,
    NotaForm,
    PelangganForm,
    PengaturanLaundryForm,
    TransaksiBaruForm,
)
from app.nota.models import ItemPakaian, Nota, Pelanggan, PengaturanLaundry, get_harga_layanan_map
from .decorators import admin_required
from .forms import EmployeeCreateForm, EmployeeEditForm, LandingPageContentForm
from .models import LandingPageContent
from .item_utils import QUICK_ITEM_VALUES, add_bulk_items_to_nota
from .report_pdf import build_report_pdf


def _periode(request):
    today = localdate()
    periode = request.GET.get("periode", "").strip() or today.strftime("%Y-%m")
    try:
        parsed = datetime.strptime(periode, "%Y-%m")
        return periode, parsed.year, parsed.month
    except ValueError:
        return today.strftime("%Y-%m"), today.year, today.month


def _admin_nota_queryset(request):
    qs = Nota.objects.select_related("pelanggan").prefetch_related("items")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    tanggal = request.GET.get("tgl", "").strip()

    if query:
        lookup = Q(pelanggan__nama__icontains=query) | Q(pelanggan__alamat__icontains=query)
        if query.isdigit():
            lookup |= Q(id=int(query))
        qs = qs.filter(lookup)
    if status in {"Belum", "Sudah"}:
        qs = qs.filter(status=status)
    if tanggal:
        qs = qs.filter(tgl=tanggal)
    return qs, query, status, tanggal


@admin_required
def dashboard(request):
    today = localdate()
    User = get_user_model()
    context = {
        "today": today,
        "total_karyawan": User.objects.filter(is_staff=False, is_superuser=False).count(),
        "karyawan_aktif": User.objects.filter(is_staff=False, is_superuser=False, is_active=True).count(),
        "total_pelanggan": Pelanggan.objects.count(),
        "nota_hari_ini": Nota.objects.filter(tgl=today).count(),
        "belum_selesai": Nota.objects.filter(status="Belum").count(),
        "pendapatan_hari_ini": Nota.objects.filter(tgl=today).aggregate(total=Sum("harga"))["total"] or 0,
        "recent_notas": Nota.objects.select_related("pelanggan")[:6],
        "landing_content": LandingPageContent.get_solo(),
    }
    return render(request, "admin_panel/dashboard.html", context)


@admin_required
def note_monitor(request):
    """Read-only real-time note monitor for the Admin Center."""
    today = localdate()
    try:
        requested_date = parse_date(request.GET.get("tanggal", ""))
    except ValueError:
        requested_date = None
    selected_date = requested_date or today
    return render(
        request,
        "admin_panel/note_monitor.html",
        {
            "today": today,
            "selected_date": selected_date,
        },
    )


@never_cache
@require_GET
@admin_required
def note_monitor_data(request):
    """JSON snapshot polled by the admin-only monitoring screen."""
    today = localdate()
    try:
        requested_date = parse_date(request.GET.get("tanggal", ""))
    except ValueError:
        requested_date = None
    selected_date = requested_date or today

    base_queryset = Nota.objects.filter(tgl=selected_date)
    summary = base_queryset.aggregate(
        total_nota=Count("id"),
        total_pendapatan=Sum("harga"),
        belum_selesai=Count("id", filter=Q(status="Belum")),
        selesai=Count("id", filter=Q(status="Sudah")),
    )

    queryset = (
        base_queryset.select_related("pelanggan")
        .annotate(total_item_monitor=Sum("items__jumlah"))
        .order_by("-id")
    )
    notes = []
    for nota in queryset[:200]:
        notes.append({
            "id": nota.id,
            "nomor": nota.nomor_struk,
            "pelanggan": nota.pelanggan.nama,
            "jenis": nota.get_jenis_display(),
            "layanan": nota.get_layanan_display(),
            "berat": str(nota.berat).replace(".", ","),
            "harga": nota.harga,
            "status": nota.get_status_display(),
            "status_code": nota.status,
            "total_item": nota.total_item_monitor or 0,
        })

    return JsonResponse({
        "today": today.isoformat(),
        "selected_date": selected_date.isoformat(),
        "updated_at": localtime(now()).strftime("%H:%M:%S"),
        "summary": {
            "total_nota": summary["total_nota"] or 0,
            "total_pendapatan": summary["total_pendapatan"] or 0,
            "belum_selesai": summary["belum_selesai"] or 0,
            "selesai": summary["selesai"] or 0,
        },
        "notes": notes,
        "limit": 200,
    })


@admin_required
def operations(request):
    today = localdate()
    context = {
        "nota_hari_ini": Nota.objects.filter(tgl=today).count(),
        "belum_selesai": Nota.objects.filter(status="Belum").count(),
        "selesai_hari_ini": Nota.objects.filter(tgl=today, status="Sudah").count(),
        "total_pelanggan": Pelanggan.objects.count(),
        "recent_notas": Nota.objects.select_related("pelanggan")[:8],
    }
    return render(request, "admin_panel/operations.html", context)


@admin_required
def admin_notas(request):
    notas, query, status, tanggal = _admin_nota_queryset(request)
    today = localdate()
    paginator = Paginator(notas, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "notas": page_obj,
        "page_obj": page_obj,
        "query": query,
        "status_filter": status,
        "tanggal_filter": tanggal,
        "total_nota_hari_ini": Nota.objects.filter(tgl=today).count(),
        "belum_selesai": Nota.objects.filter(status="Belum").count(),
        "pendapatan_hari_ini": Nota.objects.filter(tgl=today).aggregate(total=Sum("harga"))["total"] or 0,
    }
    return render(request, "admin_panel/notas.html", context)


@admin_required
def admin_nota_create(request):
    form = TransaksiBaruForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        nota = form.save()
        messages.success(request, f"Nota {nota.nomor_struk} berhasil dibuat oleh admin.")
        return redirect("adminpanel:nota_detail", nota_id=nota.id)
    return render(request, "admin_panel/nota_form.html", {"form": form, "mode": "create", "harga_layanan": get_harga_layanan_map()})


@admin_required
def admin_nota_detail(request, nota_id):
    nota = get_object_or_404(Nota.objects.select_related("pelanggan"), id=nota_id)
    if request.method == "POST" and request.POST.get("action") == "bulk_items":
        total_added, kinds_added, error = add_bulk_items_to_nota(
            nota, request.POST.get("items_payload", "")
        )
        if error:
            messages.error(request, error)
        else:
            messages.success(
                request,
                f"{total_added} pakaian dari {kinds_added} jenis berhasil ditambahkan ke nota.",
            )
        return redirect("adminpanel:nota_detail", nota_id=nota.id)

    items_qs = nota.items.all()
    paginator = Paginator(items_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    all_items = list(ItemPakaian.JENIS_PAKAIAN)
    quick_values = set(QUICK_ITEM_VALUES)
    quick_items = [(value, label) for value, label in all_items if value in quick_values]
    return render(
        request,
        "admin_panel/nota_detail.html",
        {
            "nota": nota,
            "items": page_obj,
            "page_obj": page_obj,
            "total_item": items_qs.aggregate(total=Sum("jumlah"))["total"] or 0,
            "total_jenis": items_qs.count(),
            "all_items": all_items,
            "quick_items": quick_items,
        },
    )


@admin_required
def admin_nota_edit(request, nota_id):
    nota = get_object_or_404(Nota.objects.select_related("pelanggan"), id=nota_id)
    form = NotaForm(request.POST or None, instance=nota)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Nota {nota.nomor_struk} berhasil diperbarui.")
        return redirect("adminpanel:nota_detail", nota_id=nota.id)
    return render(request, "admin_panel/nota_form.html", {"form": form, "mode": "edit", "nota": nota, "harga_layanan": get_harga_layanan_map()})


@admin_required
@require_POST
def admin_nota_status(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    nota.status = "Sudah" if nota.status == "Belum" else "Belum"
    nota.save(update_fields=["status"])
    label = "selesai" if nota.status == "Sudah" else "belum selesai"
    messages.success(request, f"Status {nota.nomor_struk} diubah menjadi {label}.")
    return redirect("adminpanel:nota_detail", nota_id=nota.id)


@admin_required
@require_POST
def admin_nota_delete(request, nota_id):
    nota = get_object_or_404(Nota.objects.select_related("pelanggan"), id=nota_id)
    nomor = nota.nomor_struk
    nota.delete()
    messages.success(request, f"Nota {nomor} berhasil dihapus.")
    return redirect("adminpanel:notas")


@admin_required
def admin_customers(request):
    query = request.GET.get("q", "").strip()
    qs = Pelanggan.objects.all().order_by("nama")
    if query:
        qs = qs.filter(Q(nama__icontains=query) | Q(alamat__icontains=query))
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "admin_panel/customers.html", {"pelanggan": page_obj, "page_obj": page_obj, "query": query})


@admin_required
def admin_customer_create(request):
    form = PelangganForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pelanggan = form.save()
        messages.success(request, f"Pelanggan {pelanggan.nama} berhasil ditambahkan.")
        return redirect("adminpanel:customers")
    return render(request, "admin_panel/customer_form.html", {"form": form, "mode": "create"})


@admin_required
def admin_customer_edit(request, pelanggan_id):
    pelanggan = get_object_or_404(Pelanggan, id=pelanggan_id)
    form = PelangganForm(request.POST or None, instance=pelanggan)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Data pelanggan {pelanggan.nama} berhasil diperbarui.")
        return redirect("adminpanel:customers")
    return render(request, "admin_panel/customer_form.html", {"form": form, "mode": "edit", "pelanggan_obj": pelanggan})


@admin_required
def reports(request):
    periode, tahun, bulan = _periode(request)
    notas = Nota.objects.filter(tgl__year=tahun, tgl__month=bulan)
    laporan = (
        notas.values("tgl")
        .annotate(total_nota=Count("id"), total_pendapatan=Sum("harga"))
        .order_by("-tgl")
    )
    paginator = Paginator(laporan, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "laporan": page_obj,
        "page_obj": page_obj,
        "periode": periode,
        "total_nota": notas.count(),
        "total_pendapatan": notas.aggregate(total=Sum("harga"))["total"] or 0,
        "total_selesai": notas.filter(status="Sudah").count(),
        "total_belum": notas.filter(status="Belum").count(),
    }
    return render(request, "admin_panel/reports.html", context)


@admin_required
def report_detail(request, tgl):
    notas_qs = Nota.objects.select_related("pelanggan").filter(tgl=tgl).order_by("-id")
    paginator = Paginator(notas_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "admin_panel/report_detail.html",
        {
            "notas": page_obj,
            "page_obj": page_obj,
            "tgl": tgl,
            "total_nota": notas_qs.count(),
            "total_pendapatan": notas_qs.aggregate(total=Sum("harga"))["total"] or 0,
        },
    )


@admin_required
def report_download(request):
    periode, tahun, bulan = _periode(request)
    notas = Nota.objects.select_related("pelanggan").prefetch_related("items").filter(tgl__year=tahun, tgl__month=bulan).order_by("tgl", "id")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="laporan-sani-laundry-{periode}.csv"'
    response.write("\ufeff")  # BOM agar Excel membaca UTF-8 dengan benar.
    writer = csv.writer(response, delimiter=";")
    writer.writerow([
        "No. Nota", "Tanggal", "Pelanggan", "Jenis Pelanggan", "Layanan", "Kecepatan",
        "Berat (kg)", "Harga/kg", "Total", "Status", "Total Item"
    ])
    for nota in notas:
        writer.writerow([
            nota.nomor_struk,
            nota.tgl.strftime("%d/%m/%Y"),
            nota.pelanggan.nama,
            nota.pelanggan.get_jenis_plggn_display(),
            nota.get_jenis_display(),
            nota.get_layanan_display(),
            str(nota.berat).replace(".", ","),
            nota.harga_per_kg or "",
            nota.harga,
            nota.get_status_display(),
            nota.total_item,
        ])
    return response


@admin_required
def report_pdf_download(request):
    periode, tahun, bulan = _periode(request)
    notas = list(
        Nota.objects.select_related("pelanggan")
        .prefetch_related("items")
        .filter(tgl__year=tahun, tgl__month=bulan)
        .order_by("tgl", "id")
    )
    rows = [
        {
            "nomor": nota.nomor_struk,
            "tanggal": nota.tgl.strftime("%d/%m/%Y"),
            "pelanggan": nota.pelanggan.nama,
            "layanan": f"{nota.get_jenis_display()} - {nota.get_layanan_display()}",
            "berat": nota.berat,
            "harga_per_kg": nota.harga_per_kg or 0,
            "total": nota.harga,
            "status": nota.get_status_display(),
        }
        for nota in notas
    ]
    total_pendapatan = sum(nota.harga for nota in notas)
    total_selesai = sum(1 for nota in notas if nota.status == "Sudah")
    total_belum = len(notas) - total_selesai
    pdf = build_report_pdf(
        title="LAPORAN TRANSAKSI & KEUANGAN",
        subtitle=f"Periode {periode}",
        laundry_settings=PengaturanLaundry.get_solo(),
        summary=[
            ("Total nota", len(notas)),
            ("Total pendapatan", f"Rp{total_pendapatan:,.0f}".replace(",", ".")),
            ("Selesai", total_selesai),
            ("Belum selesai", total_belum),
        ],
        rows=rows,
        show_date=True,
    )
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="laporan-sani-laundry-{periode}.pdf"'
    return response


@admin_required
def report_daily_pdf_download(request, tgl):
    try:
        parsed = datetime.strptime(tgl, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Tanggal laporan tidak valid.")
        return redirect("adminpanel:reports")

    notas = list(
        Nota.objects.select_related("pelanggan")
        .prefetch_related("items")
        .filter(tgl=parsed)
        .order_by("id")
    )
    rows = [
        {
            "nomor": nota.nomor_struk,
            "tanggal": nota.tgl.strftime("%d/%m/%Y"),
            "pelanggan": nota.pelanggan.nama,
            "layanan": f"{nota.get_jenis_display()} - {nota.get_layanan_display()}",
            "berat": nota.berat,
            "harga_per_kg": nota.harga_per_kg or 0,
            "total": nota.harga,
            "status": nota.get_status_display(),
        }
        for nota in notas
    ]
    total_pendapatan = sum(nota.harga for nota in notas)
    pdf = build_report_pdf(
        title="LAPORAN TRANSAKSI HARIAN",
        subtitle=parsed.strftime("%d/%m/%Y"),
        laundry_settings=PengaturanLaundry.get_solo(),
        summary=[
            ("Total nota", len(notas)),
            ("Total pendapatan", f"Rp{total_pendapatan:,.0f}".replace(",", ".")),
        ],
        rows=rows,
        show_date=False,
    )
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="laporan-sani-laundry-{tgl}.pdf"'
    return response


@admin_required
def report_daily_download(request, tgl):
    try:
        parsed = datetime.strptime(tgl, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Tanggal laporan tidak valid.")
        return redirect("adminpanel:reports")
    notas = Nota.objects.select_related("pelanggan").prefetch_related("items").filter(tgl=parsed).order_by("id")
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="laporan-sani-laundry-{tgl}.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["No. Nota", "Pelanggan", "Layanan", "Kecepatan", "Berat (kg)", "Harga/kg", "Total", "Status", "Total Item"])
    for nota in notas:
        writer.writerow([
            nota.nomor_struk,
            nota.pelanggan.nama,
            nota.get_jenis_display(),
            nota.get_layanan_display(),
            str(nota.berat).replace(".", ","),
            nota.harga_per_kg or "",
            nota.harga,
            nota.get_status_display(),
            nota.total_item,
        ])
    return response


@admin_required
def landing_editor(request):
    content = LandingPageContent.get_solo()
    form = LandingPageContentForm(request.POST or None, instance=content)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Konten landing page berhasil diperbarui.")
        return redirect("adminpanel:landing")
    return render(request, "admin_panel/landing_editor.html", {"form": form, "landing_content": content})


@admin_required
def employees(request):
    User = get_user_model()
    query = request.GET.get("q", "").strip()
    qs = User.objects.filter(is_staff=False, is_superuser=False).order_by("-is_active", "username")
    if query:
        qs = qs.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "admin_panel/employees.html", {"page_obj": page_obj, "employees": page_obj, "query": query})


@admin_required
def employee_create(request):
    form = EmployeeCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Akun karyawan {user.username} berhasil dibuat.")
        return redirect("adminpanel:employees")
    return render(request, "admin_panel/employee_form.html", {"form": form, "mode": "create"})


@admin_required
def employee_edit(request, user_id):
    User = get_user_model()
    employee = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    form = EmployeeEditForm(request.POST or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Akun karyawan {user.username} berhasil diperbarui.")
        return redirect("adminpanel:employees")
    return render(request, "admin_panel/employee_form.html", {"form": form, "mode": "edit", "employee": employee})


@admin_required
@require_POST
def employee_toggle(request, user_id):
    User = get_user_model()
    employee = get_object_or_404(User, pk=user_id, is_staff=False, is_superuser=False)
    employee.is_active = not employee.is_active
    employee.save(update_fields=["is_active"])
    label = "diaktifkan" if employee.is_active else "dinonaktifkan"
    messages.success(request, f"Akun {employee.username} berhasil {label}.")
    return redirect("adminpanel:employees")


@admin_required
def settings_center(request):
    settings_obj = PengaturanLaundry.get_solo()
    settings_form = PengaturanLaundryForm(instance=settings_obj)
    price_form = HargaLayananSettingsForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "business_settings":
            settings_form = PengaturanLaundryForm(request.POST, instance=settings_obj)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, "Identitas usaha dan pengaturan struk berhasil disimpan.")
                return redirect("adminpanel:settings")
        elif action == "service_prices":
            price_form = HargaLayananSettingsForm(request.POST)
            if price_form.is_valid():
                price_form.save()
                messages.success(request, "Harga layanan berhasil diperbarui.")
                return redirect("adminpanel:settings")

    return render(
        request,
        "admin_panel/settings.html",
        {
            "settings_form": settings_form,
            "price_form": price_form,
            "laundry_settings": settings_obj,
            "harga_layanan": get_harga_layanan_map(),
        },
    )
