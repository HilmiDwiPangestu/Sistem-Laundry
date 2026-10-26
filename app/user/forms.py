from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from app.nota.forms import ItemPakaianForm
from .models import LandingPageContent

# Nama lama dipertahankan untuk kompatibilitas dengan view yang sudah ada.
ItemLaundryForm = ItemPakaianForm

INPUT_CLASS = "form-control"


class LandingPageContentForm(forms.ModelForm):
    class Meta:
        model = LandingPageContent
        fields = [
            "aktif",
            "hero_badge",
            "hero_title",
            "hero_text",
            "hero_primary_label",
            "hero_secondary_label",
            "about_kicker",
            "about_title",
            "about_text",
            "benefit_1_title",
            "benefit_1_text",
            "benefit_2_title",
            "benefit_2_text",
            "benefit_3_title",
            "benefit_3_text",
            "services_title",
            "services_text",
            "service_express_text",
            "service_cuci_setrika_text",
            "service_cuci_lipat_text",
            "service_setrika_text",
            "process_title",
            "process_text",
            "process_step_1_title",
            "process_step_1_text",
            "process_step_2_title",
            "process_step_2_text",
            "process_step_3_title",
            "process_step_3_text",
            "cta_title",
            "cta_text",
            "footer_note",
            "tampilkan_harga",
        ]
        labels = {
            "aktif": "Tampilkan landing page",
            "hero_badge": "Label kecil hero",
            "hero_title": "Judul utama",
            "hero_text": "Deskripsi utama",
            "hero_primary_label": "Teks tombol layanan",
            "hero_secondary_label": "Teks tombol kontak",
            "about_kicker": "Label bagian tentang",
            "about_title": "Judul bagian tentang",
            "about_text": "Deskripsi tentang",
            "benefit_1_title": "Keunggulan 1 - judul",
            "benefit_1_text": "Keunggulan 1 - deskripsi",
            "benefit_2_title": "Keunggulan 2 - judul",
            "benefit_2_text": "Keunggulan 2 - deskripsi",
            "benefit_3_title": "Keunggulan 3 - judul",
            "benefit_3_text": "Keunggulan 3 - deskripsi",
            "services_title": "Judul bagian layanan",
            "services_text": "Deskripsi bagian layanan",
            "service_express_text": "Deskripsi Express",
            "service_cuci_setrika_text": "Deskripsi Cuci + Setrika",
            "service_cuci_lipat_text": "Deskripsi Cuci + Lipat",
            "service_setrika_text": "Deskripsi Setrika Saja",
            "process_title": "Judul bagian proses",
            "process_text": "Deskripsi proses",
            "process_step_1_title": "Proses 1 - judul",
            "process_step_1_text": "Proses 1 - deskripsi",
            "process_step_2_title": "Proses 2 - judul",
            "process_step_2_text": "Proses 2 - deskripsi",
            "process_step_3_title": "Proses 3 - judul",
            "process_step_3_text": "Proses 3 - deskripsi",
            "cta_title": "Judul ajakan",
            "cta_text": "Deskripsi ajakan",
            "footer_note": "Catatan footer",
            "tampilkan_harga": "Tampilkan harga layanan di landing page",
        }
        widgets = {
            "hero_badge": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "hero_title": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "hero_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
            "hero_primary_label": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "hero_secondary_label": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "about_kicker": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "about_title": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "about_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 4}),
            "benefit_1_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "benefit_1_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "benefit_2_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "benefit_2_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "benefit_3_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "benefit_3_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "services_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "services_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "service_express_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "service_cuci_setrika_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "service_cuci_lipat_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "service_setrika_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "process_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "process_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "process_step_1_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "process_step_1_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "process_step_2_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "process_step_2_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "process_step_3_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "process_step_3_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "cta_title": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "cta_text": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "footer_note": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "aktif": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "tampilkan_harga": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EmployeeCreateForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=150,
        label="Nama karyawan",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Nama lengkap"}),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "full_name")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Contoh: kasir1", "autocomplete": "off"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": INPUT_CLASS, "autocomplete": "new-password"})
        self.fields["password2"].widget.attrs.update({"class": INPUT_CLASS, "autocomplete": "new-password"})
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Ulangi password"

    def save(self, commit=True):
        user = super().save(commit=False)
        name = self.cleaned_data["full_name"].strip()
        first_name, _, last_name = name.partition(" ")
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        if commit:
            user.save()
        return user


class EmployeeEditForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        label="Nama karyawan",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )
    new_password = forms.CharField(
        required=False,
        label="Password baru",
        help_text="Kosongkan jika password tidak ingin diubah.",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASS, "autocomplete": "new-password"}),
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "is_active"]
        labels = {"username": "Username", "is_active": "Akun aktif"}
        widgets = {
            "username": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["full_name"].initial = self.instance.get_full_name() or self.instance.username

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as exc:
                raise forms.ValidationError(exc.messages)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        name = self.cleaned_data["full_name"].strip()
        first_name, _, last_name = name.partition(" ")
        user.first_name = first_name
        user.last_name = last_name
        password = self.cleaned_data.get("new_password")
        if password:
            user.set_password(password)
        # Akun yang dikelola di halaman ini selalu role karyawan.
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
