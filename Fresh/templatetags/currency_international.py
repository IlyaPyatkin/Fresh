from decimal import Decimal
import locale
from django import template

from cartridge.shop.utils import set_locale


register = template.Library()

@register.filter
def currency(value):
    """
    Replacement of cartridge's currency filter with international currency sign
    """
    set_locale()
    if not value:
        value = 0
    return locale.currency(Decimal(value), grouping=True, international=True)