from decimal import Decimal

from django import forms
from django.utils.timezone import localdate

from .models import (
    DEFAULT_HARGA_LAYANAN,
    HargaLayanan,
    ItemPakaian,
    Nota,
    Pelanggan,
    PengaturanLaundry,
    get_harga_layanan_map,
)

INPUT_CLASS = "form-control"
SELECT_CLASS = "form-select"


class BeratLaundryField(forms.DecimalField):
    """Input berat fleksibel untuk keyboard Indonesia/Android/iOS.

    Menerima pemisah desimal koma maupun titik dan maksimal 3 angka desimal,
    misalnya 3,81; 3.81; 3,815; atau 3.815.
    """

    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip().replace(" ", "").replace(",", ".")
        return super().to_python(value)


def berat_laundry_field():
    return BeratLaundryField(
        min_value=Decimal("0.001"),
        max_digits=8,
        decimal_places=3,
        label="Berat (kg)",
        error_messages={
            "invalid": "Masukkan berat yang valid, misalnya 3,81 atau 3,815.",
            "min_value": "Berat harus lebih dari 0 kg.",
            "max_decimal_places": "Berat maksimal 3 angka di belakang koma.",
        },
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Contoh: 3,81",
                "inputmode": "decimal",
                "autocomplete": "off",
                "enterkeyhint": "next",
                "data-price-weight": "",
                "data-weight-input": "",
                "aria-describedby": "weight-input-help",
            }
        ),
    )


class NotaForm(forms.ModelForm):
    berat = berat_laundry_field()

    class Meta:
        model = Nota
        fields = ["berat", "jenis", "layanan", "tgl"]
        labels = {
            "berat": "Berat (kg)",
            "jenis": "Jenis laundry",
            "layanan": "Kecepatan layanan",
            "tgl": "Tanggal masuk",
        }
        widgets = {
            "jenis": forms.Select(
                attrs={"class": SELECT_CLASS, "data-price-kind": ""}
            ),
            "layanan": forms.Select(
                attrs={"class": SELECT_CLASS, "data-price-speed": ""}
            ),
            "tgl": forms.DateInput(attrs={"type": "date", "class": INPUT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and not self.initial.get("tgl"):
            self.initial["tgl"] = localdate()

    def clean_berat(self):
        berat = self.cleaned_data["berat"]
        if berat <= 0:
            raise forms.ValidationError("Berat harus lebih dari 0 kg.")
        return berat

    def save(self, commit=True):
        nota = super().save(commit=False)
        nota.terapkan_harga_otomatis()
        if commit:
            nota.save()
        return nota


class TransaksiBaruForm(forms.ModelForm):
    berat = berat_laundry_field()

    MODE_PELANGGAN = (
        ("lama", "Pelanggan tersimpan"),
        ("baru", "Pelanggan baru"),
    )

    mode_pelanggan = forms.ChoiceField(
        choices=MODE_PELANGGAN,
        widget=forms.RadioSelect,
        initial="lama",
        label="Pilih cara input pelanggan",
    )
    pelanggan = forms.ModelChoiceField(
        queryset=Pelanggan.objects.none(),
        required=False,
        empty_label="Pilih pelanggan...",
        label="Pelanggan",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    nama_baru = forms.CharField(
        required=False,
        max_length=100,
        label="Nama pelanggan",
        widget=forms.TextInput(
            attrs={"class": INPUT_CLASS, "placeholder": "Nama pelanggan baru"}
        ),
    )
    jenis_plggn_baru = forms.ChoiceField(
        required=False,
        choices=Pelanggan.JNS_PLGGN,
        label="Jenis pelanggan",
        widget=forms.Select(attrs={"class": SELECT_CLASS}),
    )
    alamat_baru = forms.CharField(
        required=False,
        max_length=200,
        label="Alamat / keterangan",
        widget=forms.Textarea(
            attrs={"class": INPUT_CLASS, "rows": 2, "placeholder": "Opsional"}
        ),
    )

    class Meta:
        model = Nota
        fields = ["berat", "jenis", "layanan", "tgl"]
        labels = NotaForm.Meta.labels
        widgets = NotaForm.Meta.widgets

    def __init__(self, *args, preselected_pelanggan=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pelanggan"].queryset = Pelanggan.objects.all().order_by("nama")

        if not self.is_bound:
            self.initial.setdefault("tgl", localdate())
            if preselected_pelanggan:
                self.initial["pelanggan"] = preselected_pelanggan
                self.initial["mode_pelanggan"] = "lama"
            elif not self.fields["pelanggan"].queryset.exists():
                self.initial["mode_pelanggan"] = "baru"

    def clean(self):
        cleaned = super().clean()
        mode = cleaned.get("mode_pelanggan")

        if mode == "lama":
            if not cleaned.get("pelanggan"):
                self.add_error("pelanggan", "Pilih pelanggan yang sudah tersimpan.")
        elif mode == "baru":
            nama = (cleaned.get("nama_baru") or "").strip()
            if not nama:
                self.add_error("nama_baru", "Nama pelanggan wajib diisi.")
            else:
                cleaned["nama_baru"] = nama
        return cleaned

    def clean_berat(self):
        berat = self.cleaned_data["berat"]
        if berat <= 0:
            raise forms.ValidationError("Berat harus lebih dari 0 kg.")
        return berat

    def save(self, commit=True):
        nota = super().save(commit=False)
        if self.cleaned_data["mode_pelanggan"] == "baru":
            pelanggan = Pelanggan.objects.create(
                nama=self.cleaned_data["nama_baru"],
                jenis_plggn=self.cleaned_data.get("jenis_plggn_baru") or "umum",
                alamat=(self.cleaned_data.get("alamat_baru") or "").strip() or None,
            )
        else:
            pelanggan = self.cleaned_data["pelanggan"]

        nota.pelanggan = pelanggan
        nota.status = "Belum"
        nota.terapkan_harga_otomatis()
        if commit:
            nota.save()
        return nota


class HargaLayananSettingsForm(forms.Form):
    express = forms.IntegerField(
        min_value=1,
        label="Express",
        help_text="Berlaku untuk semua jenis laundry Express.",
        widget=forms.NumberInput(
            attrs={"class": INPUT_CLASS, "min": 1, "step": 500, "inputmode": "numeric"}
        ),
    )
    reguler_cuci_setrika = forms.IntegerField(
        min_value=1,
        label="Reguler - Cuci Setrika",
        widget=forms.NumberInput(
            attrs={"class": INPUT_CLASS, "min": 1, "step": 500, "inputmode": "numeric"}
        ),
    )
    reguler_cuci_lipat = forms.IntegerField(
        min_value=1,
        label="Reguler - Cuci Lipat",
        widget=forms.NumberInput(
            attrs={"class": INPUT_CLASS, "min": 1, "step": 500, "inputmode": "numeric"}
        ),
    )
    reguler_setrika = forms.IntegerField(
        min_value=1,
        label="Reguler - Setrika Saja",
        widget=forms.NumberInput(
            attrs={"class": INPUT_CLASS, "min": 1, "step": 500, "inputmode": "numeric"}
        ),
    )

    def __init__(self, *args, **kwargs):
        bound_data = args[0] if args else kwargs.get("data")
        if bound_data is None:
            kwargs.setdefault("initial", get_harga_layanan_map())
        super().__init__(*args, **kwargs)

    def save(self):
        for kode, default in DEFAULT_HARGA_LAYANAN.items():
            HargaLayanan.objects.update_or_create(
                kode=kode,
                defaults={
                    "nama": default["nama"],
                    "harga_per_kg": self.cleaned_data[kode],
                    "urutan": default["urutan"],
                },
            )


class PengaturanLaundryForm(forms.ModelForm):
    class Meta:
        model = PengaturanLaundry
        fields = [
            "nama_usaha",
            "slogan",
            "alamat",
            "telepon",
            "lebar_kertas",
            "tampilkan_logo",
            "tampilkan_item",
            "footer_struk",
        ]
        labels = {
            "nama_usaha": "Nama usaha",
            "slogan": "Slogan",
            "alamat": "Alamat",
            "telepon": "No. telepon / WhatsApp",
            "lebar_kertas": "Lebar kertas thermal",
            "tampilkan_logo": "Tampilkan logo pada struk",
            "tampilkan_item": "Tampilkan jumlah pakaian pada struk utama",
            "footer_struk": "Pesan penutup struk",
        }
        widgets = {
            "nama_usaha": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "slogan": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Opsional"}),
            "alamat": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2, "placeholder": "Opsional"}),
            "telepon": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Opsional"}),
            "lebar_kertas": forms.Select(attrs={"class": SELECT_CLASS}),
            "footer_struk": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "tampilkan_logo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "tampilkan_item": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PelangganForm(forms.ModelForm):
    class Meta:
        model = Pelanggan
        fields = ["nama", "jenis_plggn", "alamat"]
        labels = {
            "nama": "Nama pelanggan",
            "jenis_plggn": "Jenis pelanggan",
            "alamat": "Alamat / keterangan",
        }
        widgets = {
            "nama": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Nama pelanggan", "autofocus": True}
            ),
            "jenis_plggn": forms.Select(attrs={"class": SELECT_CLASS}),
            "alamat": forms.Textarea(
                attrs={
                    "class": INPUT_CLASS,
                    "rows": 3,
                    "placeholder": "Opsional",
                }
            ),
        }

    def clean_nama(self):
        return self.cleaned_data["nama"].strip()


# Alias agar pemanggilan lama tetap kompatibel.
pelangganBaruForm = PelangganForm


class ItemPakaianForm(forms.ModelForm):
    class Meta:
        model = ItemPakaian
        fields = ["jenis", "jumlah", "catatan"]
        labels = {
            "jenis": "Jenis pakaian",
            "jumlah": "Jumlah",
            "catatan": "Catatan",
        }
        widgets = {
            "jenis": forms.Select(attrs={"class": SELECT_CLASS}),
            "jumlah": forms.NumberInput(
                attrs={"class": INPUT_CLASS, "min": 1, "inputmode": "numeric"}
            ),
            "catatan": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Opsional, mis. noda tinta"}
            ),
        }
