from django.db import models
import uuid

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.IntegerField(default=1)
    status = models.CharField(max_length=50, default='PENDING') # PENDING, RESERVING, PAYMENT_PENDING, PROCESSING, FAILED, COMPLETED
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='VND')
    payment_status = models.CharField(max_length=50, default='PENDING') # PENDING, SUCCESS, FAILED
    shipping_status = models.CharField(max_length=50, default='PENDING') # PENDING, SHIPPED, DELIVERED
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'currency': self.currency,
            'payment_status': self.payment_status,
            'shipping_status': self.shipping_status,
            'created_at': self.created_at.isoformat(),
            'items': [i.to_dict() for i in self.items.all()]
        }

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=50)
    product_type = models.CharField(max_length=50) # 'laptops' | 'clothes'
    quantity = models.IntegerField(default=1)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'type': self.product_type,
            'quantity': self.quantity,
            'price': float(self.price_snapshot)
        }
