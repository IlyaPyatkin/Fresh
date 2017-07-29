from decimal import Decimal
from cartridge.shop.models import Product, OrderItem, Order, SelectedProduct, ProductVariation
from django.db import models
from django.db.models import Count, When
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User


# Show "Coming soon" on items that are not in stock
def in_stock(self):
    return self.num_in_stock is None or self.num_in_stock > 0 

Product.in_stock = in_stock


def setup(self, request):
    self.key = request.session.session_key
    self.user_id = request.user.id
    for field in self.session_fields:
        if field in request.session:
            setattr(self, field, request.session[field])
    self.total = self.item_total = request.cart.total_price()
    if self.shipping_total is not None:
        self.shipping_total = Decimal(str(self.shipping_total))
        self.total += self.shipping_total
    if self.discount_total is not None:
        self.total -= Decimal(self.discount_total)
    if self.tax_total is not None:
        self.total += Decimal(self.tax_total)
    self.save()
    item_by_owner = {}
    for item in request.cart:
        product_fields = [f.name for f in SelectedProduct._meta.fields]
        item = dict([(f, getattr(item, f)) for f in product_fields])
        orderitem = self.items.create(**item)
        # Group OrderItems by owner
        owner = ProductVariation.objects.get(sku=item['sku']).product.userproduct.owner
        if owner not in item_by_owner:
            item_by_owner[owner] = []
        item_by_owner[owner].append(orderitem)

    # Create UserOrder for each owner and UserOrderItem for each item of the owner 
    for owner, items in item_by_owner.items():
        userorder = UserOrder.objects.create(order=self, owner=owner)
        for item in items:
            UserOrderItem.objects.create(orderitem=item, userorder=userorder)

Order.setup = setup


class ExtendedProduct(Product):
    class Meta:
        proxy = True
        permissions = (
            ("view_all_products", "Can see all products"),
        )


# Bind Product to a certain User
class UserProduct(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        editable=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        editable=False
    )


@receiver(post_delete, sender=UserProduct)
def auto_delete_product(sender, instance, **kwargs):
    instance.product.delete()


# Bind Order to a certain User
class UserOrder(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        editable=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        editable=False
    )

    def is_shipped(self):
        items_shipped = self.items.values_list('shipped', flat=True)
        return all(shipped for shipped in items_shipped)

    def total(self):
        orderitems = self.items.all()
        return sum(map(lambda x: x.orderitem.total_price, orderitems))

    class Meta:
        verbose_name = _("User order")
        verbose_name_plural = _("User orders")
        permissions = (
            ("view_all_userorders", "Can see all user orders"),
        )


# OrderItem of the seller to check which items were shipped
class UserOrderItem(models.Model):
    orderitem = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        primary_key=True,
        editable=False
    )
    userorder = models.ForeignKey(
        UserOrder,
        on_delete=models.CASCADE,
        related_name="items",
        editable=False
    )
    shipped = models.BooleanField(_("Shipped"), default=False)

    class Meta:
        verbose_name = _("User order item")
        verbose_name_plural = _("User order items")

@receiver(post_delete, sender=UserOrderItem)
def auto_delete_orderitem(sender, instance, **kwargs):
    instance.orderitem.delete()
