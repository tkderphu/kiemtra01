from django.db import models

class Laptop(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, default='Unknown')
    image_url = models.CharField(max_length=500, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=10)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'brand': self.brand, 'image_url': self.image_url, 'price': float(self.price), 'quantity': self.quantity}
