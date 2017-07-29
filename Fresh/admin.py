from copy import deepcopy
from django.db import models
from django.db.models import Count, Case, When, Value, Sum, IntegerField, F, BooleanField
from django.db.models.functions import Cast
from django.contrib import admin
from django.utils.translation import (ugettext, ugettext_lazy as _,
                                      pgettext_lazy as __)
from cartridge.shop.admin import CategoryAdmin, ProductAdmin, OrderAdmin
from cartridge.shop.models import Sale, DiscountCode, Order
from cartridge.shop.fields import MoneyField
from cartridge.shop.forms import MoneyWidget
from mezzanine.pages.admin import PageAdmin
from mezzanine.generic.models import ThreadedComment
from mezzanine.conf.models import Setting
from Fresh.models import UserProduct, UserOrder, UserOrderItem


# Remove "content" field from cartridge's category edit page.
category_fieldsets = deepcopy(PageAdmin.fieldsets)
category_fieldsets[0][1]["fields"][3:3] = ["products"]
CategoryAdmin.fieldsets = category_fieldsets


# Edit displayable and editable fields of the product page
ProductAdmin.list_display = ["admin_thumb", "title", "status", "available", "sku", 
                             "unit_price", "num_in_stock", "owneruser", "admin_link"]
def owneruser(self, obj):
    return obj.userproduct.owner
owneruser.admin_order_field = "userproduct__owner"
owneruser.short_description = _("User")
ProductAdmin.owneruser = owneruser
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
    if request.user.has_perm("shop.view_all_products"):
        return qs
    return qs.filter(userproduct__owner=request.user)

ProductAdmin.get_queryset = product_get_queryset


class UserOrderItemInline(admin.TabularInline):
    readonly_fields = [
        "itemsku",
        "itemdescription",
        "itemquantity",
        "itemunit_price",
        "itemtotal_price"
    ]
    fields = readonly_fields + ["shipped"]
    def itemsku(self, obj):
        return obj.orderitem.sku
    def itemdescription(self, obj):
        return obj.orderitem.description
    def itemquantity(self, obj):
        return obj.orderitem.quantity
    def itemunit_price(self, obj):
        return obj.orderitem.unit_price
    def itemtotal_price(self, obj):
        return obj.orderitem.total_price

    itemdescription.short_description = _("Description")
    itemquantity.short_description = _("Quantity")
    itemunit_price.short_description = _("Unit price")
    itemtotal_price.short_description = _("Total price")
    itemsku.short_description = _("SKU")



    verbose_name_plural = _("Items")
    model = UserOrderItem
    extra = 0
    formfield_overrides = {MoneyField: {"widget": MoneyWidget}}


class UserOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "orderid", "ordertime", "is_shipped", "total", "owner")
    list_filter = ("owner__groups", )
    search_fields = ("id", "owner__username", "order__id")
    inlines = (UserOrderItemInline,)

    def get_queryset(self, request):
        qs = super(UserOrderAdmin, self).get_queryset(request)
        qs = qs.annotate(items_shipped = Cast(Sum('items__shipped'), IntegerField()))
        qs = qs.annotate(items_num = Cast(Count('items__shipped'), IntegerField()))
        qs = qs.annotate(items_left = F('items_num') - F('items_shipped'))
        qs = qs.annotate(shipped=Cast(Case(When(items_left=0, then=Value(True)), default=Value(False)), BooleanField()))
        qs = qs.annotate(total_price=Sum('items__orderitem__total_price'))
        if request.user.has_perm("Fresh.view_all_userorders"):
            return qs
        return qs.filter(owner=request.user)

    def first_name(self, obj):
        return obj.order.shipping_detail_first_name
    def street(self, obj):
        return obj.order.shipping_detail_street
    def state(self, obj):
        return obj.order.shipping_detail_state
    def country(self, obj):
        return obj.order.shipping_detail_country
    def last_name(self, obj):
        return obj.order.shipping_detail_last_name
    def city(self, obj):
        return obj.order.shipping_detail_city
    def postcode(self, obj):
        return obj.order.shipping_detail_postcode
    def phone(self, obj):
        return obj.order.shipping_detail_phone


    first_name.short_description = _("First name")
    street.short_description = _("Street")
    state.short_description = _("State/Region")
    country.short_description = _("Country")
    last_name.short_description = _("Last name")
    city.short_description = _("City/Suburb")
    postcode.short_description = _("Zip/Postcode")
    phone.short_description = _("Phone")
    fieldsets = (
        (_("Shipping details"), {"fields": [
            ('first_name', 'last_name'),
            ('street', 'city'),
            ('state', 'postcode'),
            ('country', 'phone')
        ]}),
    )

    readonly_fields = (
        'first_name', 'last_name',
        'street', 'city',
        'state', 'postcode',
        'country', 'phone'
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("order", "owner")
        return self.readonly_fields


    def is_shipped(self, obj):
        if obj.is_shipped():
            return _("Shipped")
        return _("Not shipped")
    def total(self, obj):
        return obj.total()
    def orderid(self, obj):
        return obj.order.id
    def ordertime(self, obj):
        return obj.order.time


    is_shipped.short_description = _('Shipped')
    total.short_description = _('Total')
    orderid.short_description = _("Order ID")
    ordertime.short_description = _("Time")

    is_shipped.admin_order_field = 'shipped'
    total.admin_order_field = 'total_price'
    orderid.admin_order_field = 'order__id'
    ordertime.admin_order_field = 'order__time'

    def lookup_allowed(self, key, value):
        return True


# Hide unused pages
admin.site.unregister(ThreadedComment)
admin.site.unregister(Setting)
admin.site.unregister(Sale)
admin.site.unregister(DiscountCode)
admin.site.register(UserOrder, UserOrderAdmin)