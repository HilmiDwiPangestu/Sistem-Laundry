"""Helpers for fast, multi-item clothing entry on laundry notes."""

import json

from django.db import transaction

from app.nota.models import ItemPakaian


QUICK_ITEM_VALUES = [
    "Kaos L. Pendek",
    "Kemeja L. Pendek",
    "Celana Panjang",
    "Celana Pendek",
    "Kerudung",
    "Jaket",
    "Daster",
    "Gamis",
    "Handuk",
    "Sprei",
    "Selimut",
    "Kaos Kaki",
]


def _normalize(value):
    return " ".join(str(value or "").strip().split()).casefold()


def add_bulk_items_to_nota(nota, raw_payload):
    """Validate a cart payload and add all clothing rows in one transaction.

    Returns ``(total_pieces, distinct_types, error_message)``. No database rows
    are written if the payload is invalid.
    """
    try:
        payload = json.loads(raw_payload) if raw_payload else []
    except (json.JSONDecodeError, TypeError):
        return 0, 0, "Data keranjang tidak valid. Silakan pilih ulang pakaian."

    if not isinstance(payload, list) or not payload:
        return 0, 0, "Pilih minimal satu jenis pakaian terlebih dahulu."
    if len(payload) > 100:
        return 0, 0, "Keranjang terlalu banyak jenis pakaian. Maksimal 100 jenis sekali simpan."

    canonical_choices = {}
    for value, label in ItemPakaian.JENIS_PAKAIAN:
        canonical_choices[_normalize(value)] = value
        canonical_choices[_normalize(label)] = value

    selected = {}
    for row in payload:
        if not isinstance(row, dict):
            return 0, 0, "Ada data pakaian yang tidak valid. Silakan periksa keranjang."

        raw_jenis = row.get("jenis", "")
        jenis_input = " ".join(str(raw_jenis or "").strip().split())
        normalized_input = _normalize(jenis_input)
        jenis = canonical_choices.get(normalized_input, jenis_input)

        try:
            jumlah = int(row.get("jumlah", 0))
        except (TypeError, ValueError):
            return 0, 0, f"Jumlah untuk {jenis or 'pakaian'} tidak valid."
        catatan = " ".join(str(row.get("catatan", "") or "").strip().split())

        if not (2 <= len(jenis) <= 100):
            return 0, 0, "Nama pakaian harus berisi 2–100 karakter."
        if not (1 <= jumlah <= 99):
            return 0, 0, f"Jumlah {jenis} harus antara 1 sampai 99."
        if len(catatan) > 200:
            return 0, 0, f"Catatan untuk {jenis} maksimal 200 karakter."

        key = _normalize(jenis) + "\0" + _normalize(catatan)
        if key in selected:
            combined = selected[key][1] + jumlah
            if combined > 99:
                return 0, 0, f"Jumlah gabungan {jenis} tidak boleh lebih dari 99."
            selected[key] = (selected[key][0], combined, selected[key][2])
        else:
            selected[key] = (jenis, jumlah, catatan)

    if not selected:
        return 0, 0, "Pilih minimal satu jenis pakaian terlebih dahulu."

    total_pieces = sum(jumlah for _, jumlah, _ in selected.values())
    with transaction.atomic():
        for jenis, jumlah, catatan in selected.values():
            # Entries without notes merge into an existing matching no-note row.
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

    return total_pieces, len(selected), ""
