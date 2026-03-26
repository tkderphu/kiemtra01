from django.db import models

class Cart(models.Model):
    customer_id = models.IntegerField(unique=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    qty = models.IntegerField(default=1)
    
    def to_dict(self):
        return {'id': self.id, 'product_id': self.product_id, 'qty': self.qty}
