from django.shortcuts import render, redirect, get_object_or_404
from .models import ItemLaundry
from app.nota.models import Nota, Pelanggan, ItemPakaian
from app.nota.forms import NotaForm, pelangganBaruForm
from .forms import ItemLaundryForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.db.models import Sum

# Create your views here.
def index(request):
    query = request.GET.get('q', '')
    filter_tgl = request.GET.get('tgl', '')

    # =========================
    # DATA PELANGGAN
    # =========================
    pelanggan_list = Pelanggan.objects.all().order_by('-id')

    if query:
        pelanggan_list = pelanggan_list.filter(nama__icontains=query)

    pelanggan_page_number = request.GET.get('pelanggan_page')
    pelanggan_paginator = Paginator(pelanggan_list, 5)  # 5 data per halaman
    pelanggan = pelanggan_paginator.get_page(pelanggan_page_number)

    # =========================
    # DATA NOTA
    # =========================
    notas_list = Nota.objects.select_related('pelanggan').order_by('-id')

    if filter_tgl:
        notas_list = notas_list.filter(tgl=filter_tgl)

    nota_page_number = request.GET.get('nota_page')
    nota_paginator = Paginator(notas_list, 5)  # 5 data per halaman
    notas = nota_paginator.get_page(nota_page_number)

    # =========================
    # SELECTED CUSTOMER
    # =========================
    selected_customer = None
    if query:
        selected_customer = Pelanggan.objects.filter(nama__icontains=query).first()

    context = {
        'notas': notas,
        'selected_customer': selected_customer,
        'query': query,
        'pelanggan': pelanggan,
        'filter_tgl': filter_tgl,
    }

    return render(request, 'user/detail_nota.html', context)

def buatNota(request, pelanggan_id):

    pelanggan = get_object_or_404(Pelanggan, id=pelanggan_id)
    if request.method == 'POST':
        form = NotaForm(request.POST)

        if form.is_valid():
            nota = form.save(commit=False)
            nota.pelanggan = pelanggan
            nota.save()

            messages.success(request, "Data nota berhasil disimpan!")
            return redirect('user:user_index')

    else:
        form = NotaForm()

    context = {
        'pelanggan': pelanggan,
        'form': form
    }

    return render(request, 'user/buatNota.html', context)

def tambahNota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)

        if form.is_valid():
            nota = form.save(commit=False)
            nota.save()

            messages.success(request, "Data nota berhasil disimpan!")
            return redirect('nota:data_nota')

    else:
        form = NotaForm()
    return render(request, 'user/tambahNota.html', {
        'form': form
    })

def pelangganBaru(request):
    form = pelangganBaruForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Data pelanggan berhasil disimpan!")
        return redirect('user:user_index')
    
    context = {
        'form': form
    }
    return render(request, 'user/pelangganBaru.html', context)


def tambah_item(request, nota_id):

    nota = get_object_or_404(Nota, id=nota_id)

    if request.method == 'POST':
        form = ItemLaundryForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.nota = nota
            item.save()

            messages.success(request, "Data item berhasil disimpan!")
            return redirect('user:tambah_item', nota_id=nota.id)

    else:
        form = ItemLaundryForm()

    # hitung total jumlah pakaian
    total_item = nota.items.aggregate(total=Sum('jumlah'))['total'] or 0

    context = {
        'nota': nota,
        'form': form,
        'total_item': total_item
    }
    return render(request, 'user/detail_item.html', context)

def hapusNota(request, nota_id):
   
   nota = get_object_or_404(Nota, id=nota_id)
   
   if request.method == "POST":
        nota.delete()
        messages.success(request, "Nota berhasil dihapus.")
        return redirect('user:user_index')
   
   return redirect('user:user_index')

def selesaiItem(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)

    if nota.status == "Belum":
        nota.status = "Sudah"
    else:
        nota.status = "Belum"

    nota.save()

    return redirect('user:user_index')

