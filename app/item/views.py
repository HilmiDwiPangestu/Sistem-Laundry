from django.shortcuts import render, get_object_or_404
from app.nota.models import Nota
from django.db.models import Sum, Count

# Create your views here.

def data_item(request):
    notas = Nota.objects.select_related('pelanggan').all().order_by('-id')
    
    return render(request, 'item/data_item.html', {'notas': notas})

def detailItem(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    items = nota.items.all()

    return render(request, 'item/detail_item.html', {
        'nota': nota,
        'items': items
    })

def laporan_bulanan(request):
    bulan = request.GET.get('bulan')
    tahun = request.GET.get('tahun')

    notas = Nota.objects.all()

    if bulan and tahun:
        notas = notas.filter(tgl__month=bulan, tgl__year=tahun)

    # GROUP BY TANGGAL
    laporan = (
        notas.values('tgl')
        .annotate(
            total_nota=Count('id'),
            total_pendapatan=Sum('harga')
        )
        .order_by('-tgl')
    )

    context = {
        'laporan': laporan,
        'bulan': bulan,
        'tahun': tahun,
    }

    return render(request, 'item/laporan.html', context)

def laporan_detail_tanggal(request, tgl):
    notas = Nota.objects.filter(tgl=tgl).order_by('-id')

    return render(request, 'item/detail_laporan.html', {
        'notas': notas,
        'tgl': tgl
    })