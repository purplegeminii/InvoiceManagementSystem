from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

from .models import *
from .forms import *

# Create your views here.


def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date_created')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(customer__name__icontains=search)
        )
    
    if status:
        invoices = invoices.filter(status=status)
    
    context = {
        'invoices': invoices,
        'search': search,
        'status': status,
    }
    return render(request, 'invoices/invoice_list.html', context)

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {'invoice': invoice}
    return render(request, 'invoices/invoice_detail.html', context)

def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            messages.success(request, 'Invoice created successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Invoice',
    }
    return render(request, 'invoices/invoice_form.html', context)

def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Invoice updated successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    
    context = {
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'title': 'Update Invoice',
    }
    return render(request, 'invoices/invoice_form.html', context)

def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully!')
        return redirect('invoice_list')
    
    context = {'invoice': invoice}
    return render(request, 'invoices/invoice_confirm_delete.html', context)

def render_to_pdf(template_src, context_dict={}):
    """Helper function to render HTML to PDF"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def invoice_pdf(request, pk):
    """Generate PDF for a specific invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {'invoice': invoice}
    
    # Create PDF
    pdf = render_to_pdf('invoices/invoice_pdf.html', context)
    
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Invoice_{invoice.invoice_number}.pdf"
        content = f"inline; filename={filename}"
        download = request.GET.get("download")
        if download:
            content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    
    return HttpResponse("Error generating PDF", status=400)
