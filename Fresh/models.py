from cartridge.shop.models import Product


# Show "Coming soon" on items that are not in stock
def in_stock(self):
	return self.num_in_stock is None or self.num_in_stock > 0 

Product.in_stock = in_stock
