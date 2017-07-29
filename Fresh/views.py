from django.http import Http404, HttpResponse
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.template.response import TemplateResponse
from mezzanine.conf import settings
from cartridge.shop.models import Order

try:
    from xhtml2pdf import pisa
except (ImportError, SyntaxError):
    pisa = None
HAS_PDF = pisa is not None

def invoice(request, order_id, template="shop/order_invoice.html",
            template_pdf="shop/order_invoice_pdf.html", extra_context=None):
    """
    Display a plain text invoice for the given order. The order must
    belong to the user which is checked via session or ID if
    authenticated, or if the current user is staff.
    """
    try:
        order = Order.objects.get_for_user(order_id, request)
    except Order.DoesNotExist:
        raise Http404
    context = {"order": order}
    context.update(order.details_as_dict())
    context.update(extra_context or {})
    if HAS_PDF and request.GET.get("format") == "pdf":
        response = HttpResponse(content_type="application/pdf")
        name = slugify("%s-invoice-%s" % (settings.SITE_TITLE, order.id))
        response["Content-Disposition"] = "attachment; filename=%s.pdf" % name
        html = get_template(template_pdf).render(context)
        pisa.CreatePDF(html, response)
        return response
    return TemplateResponse(request, template, context)