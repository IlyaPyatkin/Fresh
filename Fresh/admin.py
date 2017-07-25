from copy import deepcopy
from django.contrib import admin
from cartridge.shop.admin import CategoryAdmin, ProductAdmin
from cartridge.shop.models import Sale, DiscountCode
from mezzanine.pages.admin import PageAdmin
from mezzanine.generic.models import ThreadedComment
from mezzanine.conf.models import Setting
from Fresh.models import UserProduct


# Remove "content" field from cartridge's category edit page.
category_fieldsets = deepcopy(PageAdmin.fieldsets)
category_fieldsets[0][1]["fields"][3:3] = ["products"]
CategoryAdmin.fieldsets = category_fieldsets


# Edit displayable and editable fields of the product page
ProductAdmin.list_display = ["admin_thumb", "title", "status", "available", "sku", 
							 "unit_price", "num_in_stock", "userproduct", "admin_link"]
ProductAdmin.list_editable = ["status", "available", "unit_price", "num_in_stock"]


# Add filter based on groups to product page
ProductAdmin.list_filter = ("status", "available", "categories", "userproduct__owner__groups")

def lookup_allowed(self, key, value):
	return True

ProductAdmin.lookup_allowed = lookup_allowed


# Create a UserProduct object when a new Product is saved
def new_save_model(self, request, obj, form, change):
    super(ProductAdmin, self).save_model(request, obj, form, change)
    if not change:
    	UserProduct.objects.create(product=obj, owner=request.user)
    self._product_id = obj.id

ProductAdmin.save_model = new_save_model


# Hide items that are not owned by the current user
# if the user doesn't have super user privileges
def product_get_queryset(self, request):
	qs = super(ProductAdmin, self).get_queryset(request)
	if request.user.is_superuser:
		return qs
	return qs.filter(userproduct__owner=request.user)

ProductAdmin.get_queryset = product_get_queryset


# Hide unused pages
admin.site.unregister(ThreadedComment)
admin.site.unregister(Setting)
admin.site.unregister(Sale)
admin.site.unregister(DiscountCode)
