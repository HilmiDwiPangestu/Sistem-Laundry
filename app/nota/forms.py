from django import forms
from .models import Nota, ItemPakaian, Pelanggan


class NotaForm(forms.ModelForm):

    class Meta:
        model = Nota
        fields = [ 
            'berat',
            'jenis',
            'layanan',
            'harga',
            'tgl'
        ]

        widgets = {
             'berat': forms.NumberInput(attrs={
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary',
                'placeholder': 'Berat pakaian (kg)',
                'step': '0.1'
            }),

             'jenis': forms.Select(attrs={
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
            }),

            'layanan': forms.Select(attrs={
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
            }),

            'harga': forms.NumberInput(attrs={
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary',
                'placeholder': 'Total harga'
            }),

            'tgl': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary'
            }),
        }

class pelangganBaruForm(forms.ModelForm):
    class Meta:
        model = Pelanggan
        fields = [
            'nama',
            'jenis_plggn',
            'alamat'
        ]

        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition',
                'placeholder': 'Masukkan nama pelanggan'
                }),

            'jenis_plggn': forms.Select(attrs={
                'class': 'w-full h-11 px-3 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition'
                }),

            'alamat': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition',
                'rows': 3,
                'placeholder': 'Masukkan alamat pelanggan (opsional)'
            }),
        }

class ItemPakaianForm(forms.ModelForm):

    class Meta:
        model = ItemPakaian
        fields = [
            'jenis',
            'jumlah',
            'catatan'
        ]

        widgets = {
            'jenis': forms.Select(attrs={
                'class': 'select2 w-full rounded-lg border-slate-300'
            }),

            'jumlah': forms.NumberInput(attrs={
                'class': 'w-full rounded-lg border-slate-300'
            }),
            
            'catatan': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-slate-300'
            }),
        }