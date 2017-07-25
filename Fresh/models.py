from cartridge.shop.models import Product
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.models import User


# Show "Coming soon" on items that are not in stock
def in_stock(self):
	return self.num_in_stock is None or self.num_in_stock > 0 

Product.in_stock = in_stock

# Bind Product to a certain User
class UserProduct(models.Model):
	product = models.OneToOneField(
		Product,
		on_delete=models.CASCADE,
		primary_key=True,
	)
	owner = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		verbose_name=_("Owner")
	)

	def __str__(self):
		return str(self.owner)

@receiver(post_delete, sender=UserProduct)
def auto_delete_product(sender, instance, **kwargs):
	instance.product.delete()
