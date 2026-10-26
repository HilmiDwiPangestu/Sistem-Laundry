from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.urls import reverse
from django.utils.timezone import localdate
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from app.nota.forms import (
    HargaLayananSettingsForm,
    PengaturanLaundryForm,
    ItemPakaianForm,
    NotaForm,
    PelangganForm,
    TransaksiBaruForm,
)
from app.nota.models import DEFAULT_HARGA_LAYANAN, ItemPakaian, Nota, Pelanggan, PengaturanLaundry, get_harga_layanan_map
from .decorators import admin_required
from .models import LandingPageContent
from .item_utils import QUICK_ITEM_VALUES, add_bulk_items_to_nota


def landing_page(request):
    """Landing page publik. Kontennya dikelola admin dari Admin Center."""
    content = LandingPageContent.get_solo()
    laundry = PengaturanLaundry.get_solo()
    if not content.aktif:
        return render(request, "public/landing_offline.html", {"landing": content, "laundry": laundry})
    price_map = get_harga_layanan_map()
    service_labels = {
        "express": ("Express", content.service_express_text),
        "reguler_cuci_setrika": ("Cuci + Setrika", content.service_cuci_setrika_text),
        "reguler_cuci_lipat": ("Cuci + Lipat", content.service_cuci_lipat_text),
        "reguler_setrika": ("Setrika Saja", content.service_setrika_text),
    }
    services = []
    for code, default in DEFAULT_HARGA_LAYANAN.items():
        title, desc = service_labels[code]
        services.append({
            "code": code,
            "title": title,
            "description": desc,
            "price": price_map.get(code, default["harga_per_kg"]),
        })

    phone_digits = "".join(ch for ch in (laundry.telepon or "") if ch.isdigit())
    if phone_digits.startswith("0"):
        phone_digits = "62" + phone_digits[1:]
    whatsapp_url = f"https://wa.me/{phone_digits}" if phone_digits else ""

    return render(
        request,
        "public/landing.html",
        {
            "landing": content,
            "laundry": laundry,
            "services": services,
            "starting_price": min((service["price"] for service in services), default=0),
            "whatsapp_url": whatsapp_url,
        },
    )


@login_required
def role_redirect(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:dashboard")
    return redirect("user:user_index")


@login_required
def index(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:operations")
    today = localdate()
    notas_hari_ini = Nota.objects.filter(tgl=today)
    pending_notas = (
        Nota.objects.filter(status="Belum")
        .select_related("pelanggan")
        .prefetch_related("items")[:8]
    )
    recent_notas = Nota.objects.select_related("pelanggan").prefetch_related("items")[:6]

    context = {
        "today": today,
        "total_nota_hari_ini": notas_hari_ini.count(),
        "selesai_hari_ini": notas_hari_ini.filter(status="Sudah").count(),
        "belum_selesai": Nota.objects.filter(status="Belum").count(),
        "pending_notas": pending_notas,
        "recent_notas": recent_notas,
    }
    return render(request, "user/dashboard.html", context)


@login_required
def transaksi_baru(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:nota_create")
    preselected = None
    pelanggan_id = request.GET.get("pelanggan")
    if pelanggan_id:
        preselected = Pelanggan.objects.filter(id=pelanggan_id).first()

    form = TransaksiBaruForm(
        request.POST or None,
        preselected_pelanggan=preselected,
    )

    if request.method == "POST" and form.is_valid():
        nota = form.save()
        messages.success(
            request,
            f"Nota #{nota.id} berhasil dibuat. Tambahkan daftar pakaian bila diperlukan.",
        )
        return redirect("user:nota_detail", nota_id=nota.id)

    return render(
        request,
        "user/transaksi_baru.html",
        {"form": form, "harga_layanan": get_harga_layanan_map()},
    )


@login_required
def nota_detail(request, nota_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:nota_detail", nota_id=nota_id)
    nota = get_object_or_404(
        Nota.objects.select_related("pelanggan").prefetch_related("items"),
        id=nota_id,
    )
    form = ItemPakaianForm()

    if request.method == "POST":
        action = request.POST.get("action", "manual_item")

        if action == "simple_item":
            raw_jenis = request.POST.get("jenis_sederhana", "")
            jenis_input = " ".join(str(raw_jenis).strip().split())
            raw_catatan = request.POST.get("catatan_sederhana", "")
            catatan = " ".join(str(raw_catatan).strip().split())

            try:
                jumlah = int(request.POST.get("jumlah_sederhana", 1))
            except (TypeError, ValueError):
                jumlah = 0

            # Pegawai boleh mengetik label bawaan maupun jenis pakaian baru.
            # Jika cocok dengan daftar bawaan, simpan value kanoniknya agar konsisten.
            canonical = {}
            for value, label in ItemPakaian.JENIS_PAKAIAN:
                canonical[str(value).casefold()] = value
                canonical[str(label).casefold()] = value
            jenis = canonical.get(jenis_input.casefold(), jenis_input) if jenis_input else ""

            if not (2 <= len(jenis) <= 100):
                messages.error(request, "Isi jenis pakaian terlebih dahulu (maksimal 100 karakter).")
            elif not (1 <= jumlah <= 99):
                messages.error(request, "Jumlah pakaian harus antara 1 sampai 99.")
            elif len(catatan) > 200:
                messages.error(request, "Catatan maksimal 200 karakter.")
            else:
                # Tanpa catatan, jenis yang sama langsung digabung supaya Isi Nota tetap ringkas.
                existing = None
                if not catatan:
                    existing = nota.items.filter(jenis__iexact=jenis, catatan__isnull=True).first()
                    if existing is None:
                        existing = nota.items.filter(jenis__iexact=jenis, catatan="").first()

                if existing:
                    existing.jumlah += jumlah
                    existing.save(update_fields=["jumlah"])
                else:
                    ItemPakaian.objects.create(
                        nota=nota,
                        jenis=jenis,
                        jumlah=jumlah,
                        catatan=catatan or None,
                    )
                messages.success(request, f"{jumlah} {jenis_input or jenis} ditambahkan ke nota.")
                return redirect("user:nota_detail", nota_id=nota.id)

        elif action == "bulk_items":
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
            return redirect("user:nota_detail", nota_id=nota.id)

        else:
            form = ItemPakaianForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.nota = nota
                item.save()
                messages.success(request, "Item pakaian ditambahkan.")
                return redirect("user:nota_detail", nota_id=nota.id)

    # Semua daftar data menggunakan 10 baris/kartu per halaman.
    # Rincian pakaian pada detail nota juga dipaginasi agar tetap ringkas di HP.
    items_qs = nota.items.all()
    total_item = items_qs.aggregate(total=Sum("jumlah"))["total"] or 0
    total_jenis = items_qs.count()
    paginator = Paginator(items_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    all_choices = list(ItemPakaian.JENIS_PAKAIAN)
    quick_values = set(QUICK_ITEM_VALUES)
    quick_items = [(value, label) for value, label in all_choices if value in quick_values]
    other_items = [(value, label) for value, label in all_choices if value not in quick_values]

    return render(
        request,
        "user/nota_detail.html",
        {
            "nota": nota,
            "form": form,
            "total_item": total_item,
            "total_jenis": total_jenis,
            "items": page_obj,
            "page_obj": page_obj,
            # Cetak tetap menampilkan seluruh item, bukan hanya halaman aktif.
            "print_items": items_qs,
            "quick_items": quick_items,
            "other_items": other_items,
            "all_items": all_choices,
        },
    )


@admin_required
def harga_layanan(request):
    form = HargaLayananSettingsForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Harga layanan berhasil diperbarui dan berlaku untuk nota baru.")
        return redirect("user:harga_layanan")

    return render(
        request,
        "user/harga_layanan.html",
        {"form": form, "harga_layanan": get_harga_layanan_map()},
    )


@admin_required
def control_center(request):
    settings_obj = PengaturanLaundry.get_solo()
    settings_form = PengaturanLaundryForm(instance=settings_obj)
    price_form = HargaLayananSettingsForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "receipt_settings":
            settings_form = PengaturanLaundryForm(request.POST, instance=settings_obj)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, "Pengaturan struk dan printer berhasil disimpan.")
                return redirect("adminpanel:control_center")
        elif action == "service_prices":
            price_form = HargaLayananSettingsForm(request.POST)
            if price_form.is_valid():
                price_form.save()
                messages.success(request, "Harga layanan berhasil diperbarui.")
                return redirect("adminpanel:control_center")

    latest_nota = Nota.objects.select_related("pelanggan").first()
    return render(
        request,
        "user/control_center.html",
        {
            "settings_form": settings_form,
            "price_form": price_form,
            "laundry_settings": settings_obj,
            "harga_layanan": get_harga_layanan_map(),
            "latest_nota": latest_nota,
            "control_center_url_name": "adminpanel:control_center",
            "receipt_test_url_name": "adminpanel:receipt_test",
        },
    )


@login_required
def nota_receipt(request, nota_id):
    nota = get_object_or_404(
        Nota.objects.select_related("pelanggan").prefetch_related("items"),
        id=nota_id,
    )
    settings_obj = PengaturanLaundry.get_solo()
    items = list(nota.items.all())
    total_item = sum(item.jumlah for item in items)
    total_jenis = len(items)
    has_items = total_jenis > 0

    selected_copy = request.GET.get("copy", "all").strip().lower()
    if selected_copy not in {"all", "customer", "laundry", "items"}:
        selected_copy = "all"

    # Sebelum rincian pakaian diisi hanya ada 2 struk. Begitu item sudah
    # dimasukkan, lembar item/produksi otomatis menjadi struk ketiga.
    receipt_count = 3 if has_items else 2

    return render(
        request,
        "user/nota_receipt.html",
        {
            "nota": nota,
            "items": items,
            "total_item": total_item,
            "total_jenis": total_jenis,
            "has_items": has_items,
            "receipt_count": receipt_count,
            "selected_copy": selected_copy,
            "laundry_settings": settings_obj,
            "autoprint": request.GET.get("autoprint") == "1",
        },
    )


@admin_required
def receipt_test(request):
    settings_obj = PengaturanLaundry.get_solo()
    return render(
        request,
        "user/receipt_test.html",
        {
            "laundry_settings": settings_obj,
            "autoprint": request.GET.get("autoprint") == "1",
            "control_center_url_name": "adminpanel:control_center",
        },
    )


@login_required
def pelanggan_list(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:customers")
    query = request.GET.get("q", "").strip()
    pelanggan_qs = Pelanggan.objects.all().order_by("nama")
    if query:
        pelanggan_qs = pelanggan_qs.filter(
            Q(nama__icontains=query) | Q(alamat__icontains=query)
        )

    paginator = Paginator(pelanggan_qs, 10)
    pelanggan = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "user/pelanggan_list.html",
        {"pelanggan": pelanggan, "page_obj": pelanggan, "query": query},
    )


@login_required
def buatNota(request, pelanggan_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:nota_create")
    # URL lama dipertahankan, tetapi diarahkan ke alur transaksi baru yang lebih ringkas.
    pelanggan = get_object_or_404(Pelanggan, id=pelanggan_id)
    url = reverse("user:transaksi_baru")
    return redirect(f"{url}?pelanggan={pelanggan.id}")


@login_required
def tambahNota(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:nota_create")
    return redirect("user:transaksi_baru")


@login_required
def pelangganBaru(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:customer_create")
    form = PelangganForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pelanggan = form.save()
        messages.success(request, "Pelanggan berhasil ditambahkan.")
        if request.POST.get("lanjut_nota") == "1":
            url = reverse("user:transaksi_baru")
            return redirect(f"{url}?pelanggan={pelanggan.id}")
        return redirect("user:pelanggan_list")

    return render(request, "user/pelangganBaru.html", {"form": form, "mode": "baru"})


@login_required
def pelanggan_edit(request, pelanggan_id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("adminpanel:customer_edit", pelanggan_id=pelanggan_id)
    pelanggan = get_object_or_404(Pelanggan, id=pelanggan_id)
    form = PelangganForm(request.POST or None, instance=pelanggan)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Data pelanggan berhasil diperbarui.")
        return redirect("user:pelanggan_list")

    return render(
        request,
        "user/pelangganBaru.html",
        {"form": form, "mode": "edit", "pelanggan_obj": pelanggan},
    )


@login_required
def tambah_item(request, nota_id):
    # Kompatibilitas URL lama.
    if request.method == "POST":
        return nota_detail(request, nota_id)
    return redirect("user:nota_detail", nota_id=nota_id)


@login_required
@require_POST
def ubah_jumlah_item(request, nota_id, item_id):
    nota = get_object_or_404(Nota, id=nota_id)
    item = get_object_or_404(nota.items, id=item_id)
    try:
        delta = int(request.POST.get("delta", 0))
    except (TypeError, ValueError):
        delta = 0

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if delta not in {-1, 1}:
        if is_ajax:
            return JsonResponse({"ok": False, "message": "Perubahan jumlah item tidak valid."}, status=400)
        messages.error(request, "Perubahan jumlah item tidak valid.")
        return redirect("user:nota_detail", nota_id=nota.id)

    new_total = item.jumlah + delta
    deleted = new_total <= 0
    if deleted:
        item.delete()
        messages.success(request, "Item pakaian dihapus.")
        current_quantity = 0
    else:
        item.jumlah = new_total
        item.save(update_fields=["jumlah"])
        current_quantity = item.jumlah

    if is_ajax:
        total_item = nota.items.aggregate(total=Sum("jumlah"))["total"] or 0
        jenis_count = nota.items.count()
        return JsonResponse(
            {
                "ok": True,
                "deleted": deleted,
                "quantity": current_quantity,
                "total_item": total_item,
                "jenis_count": jenis_count,
            }
        )

    return redirect("user:nota_detail", nota_id=nota.id)


@login_required
@require_POST
def hapus_item(request, nota_id, item_id):
    nota = get_object_or_404(Nota, id=nota_id)
    item = get_object_or_404(nota.items, id=item_id)
    item.delete()
    messages.success(request, "Item pakaian dihapus.")
    return redirect("user:nota_detail", nota_id=nota.id)


@login_required
@require_POST
def hapusNota(request, nota_id):
    nota = get_object_or_404(Nota.objects.select_related("pelanggan"), id=nota_id)
    nomor_struk = nota.nomor_struk
    pelanggan_nama = nota.pelanggan.nama
    nota.delete()
    messages.success(request, f"Nota {nomor_struk} atas nama {pelanggan_nama} berhasil dihapus.")

    next_url = request.POST.get("next", "").strip()
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("nota:data_nota")


@login_required
@require_POST
def selesaiItem(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    nota.status = "Sudah" if nota.status == "Belum" else "Belum"
    nota.save(update_fields=["status"])
    label = "selesai" if nota.status == "Sudah" else "belum selesai"
    messages.success(request, f"Status nota diubah menjadi {label}.")
    return redirect(request.POST.get("next") or reverse("user:nota_detail", args=[nota.id]))
