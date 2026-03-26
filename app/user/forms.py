from django import forms
from django_select2.forms import Select2Widget
from app.nota.models import ItemPakaian


base_input_class = (
    "w-full h-11 px-3 rounded-lg border border-slate-300 "
    "dark:border-slate-700 bg-white dark:bg-slate-900 "
    "text-sm focus:outline-none focus:ring-2 focus:ring-primary"
)

class ItemLaundryForm(forms.ModelForm):


    class Meta:
        model = ItemPakaian
        fields = ['jenis', 'jumlah', 'catatan']

        widgets = {
            'jenis': Select2Widget(attrs={
                'class': 'w-full',
                'data-placeholder': 'Pilih jenis pakaian',
                'data-allow-clear': 'true'
            }),

            'jumlah': forms.NumberInput(attrs={
                'class': base_input_class,
                'min': 1,
                'placeholder': 'Masukkan jumlah pakaian'
            }),

            'catatan': forms.TextInput(attrs={
                'class': base_input_class,
                'placeholder': 'Contoh: ada noda tinta'
            }),
        }