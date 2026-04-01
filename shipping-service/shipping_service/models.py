from django.db import models
import uuid
import random
import string

def generate_tracking():
    return 'VN' + ''.join(random.choices(string.digits, k=10))

class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=50)
    address = models.TextField()
    status = models.CharField(max_length=50, default='PENDING') # PENDING, SHIPPED, DELIVERED
    tracking_number = models.CharField(max_length=50, default=generate_tracking)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'order_id': self.order_id,
            'address': self.address,
            'status': self.status,
            'tracking_number': self.tracking_number
        }
