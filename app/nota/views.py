from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localdate
from django.views.decorators.http import require_POST

from .forms import NotaForm
from .models import Nota, get_harga_layanan_map


@login_required
def index(request):
    return redirect("user:user_index")


@login_required
def nota_list(request):
    return redirect("nota:data_nota")


@login_required
def data_nota(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:notas")
    notas = Nota.objects.select_related("pelanggan").prefetch_related("items")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    tanggal = request.GET.get("tgl", "").strip()

    if query:
        notas = notas.filter(
            Q(pelanggan__nama__icontains=query)
            | Q(pelanggan__alamat__icontains=query)
        )
    if status in {"Belum", "Sudah"}:
        notas = notas.filter(status=status)
    if tanggal:
        notas = notas.filter(tgl=tanggal)

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
        "selesai_hari_ini": Nota.objects.filter(tgl=today, status="Sudah").count(),
        "belum_selesai": Nota.objects.filter(status="Belum").count(),
    }
    return render(request, "nota/data_nota.html", context)


@login_required
@require_POST
def nota_delete(request, id):
    nota = get_object_or_404(Nota, id=id)
    nota.delete()
    messages.success(request, "Nota berhasil dihapus.")
    return redirect("nota:data_nota")


@login_required
def nota_edit(request, id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:nota_edit", nota_id=id)
    nota = get_object_or_404(Nota.objects.select_related("pelanggan"), id=id)
    form = NotaForm(request.POST or None, instance=nota)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Nota berhasil diperbarui.")
        return redirect("user:nota_detail", nota_id=nota.id)

    return render(
        request,
        "nota/data_notaEdit.html",
        {"nota": nota, "form": form, "harga_layanan": get_harga_layanan_map()},
    )
