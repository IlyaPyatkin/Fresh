from copy import deepcopy
from django.contrib import admin
from cartridge.shop.admin import CategoryAdmin, ProductAdmin
from cartridge.shop.models import Sale, DiscountCode
from mezzanine.pages.admin import PageAdmin
from mezzanine.generic.models import ThreadedComment
from mezzanine.conf.models import Setting


# Remove "content" field from cartridge's category edit page.
category_fieldsets = deepcopy(PageAdmin.fieldsets)
category_fieldsets[0][1]["fields"][3:3] = ["products"]
CategoryAdmin.fieldsets = category_fieldsets


# Edit displayable and editable fields of the product page
ProductAdmin.list_display = ["admin_thumb", "title", "status", "available", "sku", 
							 "unit_price", "num_in_stock", "admin_link"]
ProductAdmin.list_editable = ["status", "available", "unit_price", "num_in_stock"]


# Hide unused pages
admin.site.unregister(ThreadedComment)
admin.site.unregister(Setting)
admin.site.unregister(Sale)
admin.site.unregister(DiscountCode)
