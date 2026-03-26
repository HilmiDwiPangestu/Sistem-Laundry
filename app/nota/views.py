from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib import messages

from app.nota.models import Nota
from .forms import NotaForm

# Create your views here.
def index(request):
    notas = Nota.objects.all().order_by('-id')

    context = {
        'notas': notas
    }
    
    return render(request, 'nota/dashboard.html', context)

def nota_list(request):
    notas = Nota.objects.all().order_by('-id')

    print(notas)

    return render(request, 'nota/index.html', {
        'notas': notas
    })


def data_nota(request):
    notas = Nota.objects.select_related('pelanggan').all().order_by('-id')

    # tanggal hari ini
    today = now().date()

    # total nota hari ini
    total_nota = Nota.objects.filter(tgl=today).count()

    # pendapatan hari ini
    pendapatan_hari_ini = Nota.objects.filter(tgl=today).aggregate(
        total=Sum('harga')
    )['total'] or 0

    # total pendapatan semua
    total_pendapatan = Nota.objects.aggregate(
        total=Sum('harga')
    )['total'] or 0

    context = {
        'notas': notas,
        'total_nota': total_nota,
        'pendapatan_hari_ini': pendapatan_hari_ini,
        'total_pendapatan': total_pendapatan,
    }
    return render(request, 'nota/data_nota.html', context)


def nota_delete(request, id):

    nota = get_object_or_404(Nota, id=id)
    nota.delete()

    return redirect('nota:data_nota')


def nota_edit(request, id):
    nota = get_object_or_404(Nota, id=id)

    if request.method == "POST":
        nota.nama = request.POST.get('nama')
        nota.jenis = request.POST.get('jenis')
        nota.berat = request.POST.get('berat')
        nota.harga = request.POST.get('harga')
        nota.tgl = request.POST.get('tgl')
        nota.save()

        return redirect('nota:data_nota')

    context = {
        'nota': nota
    }

    return render(request, 'nota/data_notaEdit.html', context)