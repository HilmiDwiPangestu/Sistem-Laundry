from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from app.nota.models import Nota
from app.user.decorators import admin_required


@login_required
def data_item(request):
    query = request.GET.get("q", "").strip()
    notas = Nota.objects.select_related("pelanggan").prefetch_related("items")
    if query:
        notas = notas.filter(Q(pelanggan__nama__icontains=query) | Q(items__jenis__icontains=query)).distinct()
    paginator = Paginator(notas, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "item/data_item.html", {"notas": page_obj, "page_obj": page_obj, "query": query})


@login_required
def detailItem(request, nota_id):
    nota = get_object_or_404(Nota.objects.select_related("pelanggan"), id=nota_id)
    items_qs = nota.items.all()
    total_item = items_qs.aggregate(total=Sum("jumlah"))["total"] or 0
    total_jenis = items_qs.count()
    paginator = Paginator(items_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "item/detail_item.html",
        {"nota": nota, "items": page_obj, "page_obj": page_obj, "total_item": total_item, "total_jenis": total_jenis},
    )


# Laporan dan keuangan hanya untuk Admin Center. URL lama dipertahankan
# sebagai redirect aman agar bookmark versi sebelumnya tidak membuka laporan
# di panel karyawan.
@admin_required
def laporan_bulanan(request):
    periode = request.GET.get("periode", "").strip()
    target = "adminpanel:reports"
    if periode:
        from django.urls import reverse
        return redirect(f"{reverse(target)}?periode={periode}")
    return redirect(target)


@admin_required
def laporan_detail_tanggal(request, tgl):
    return redirect("adminpanel:report_detail", tgl=tgl)
