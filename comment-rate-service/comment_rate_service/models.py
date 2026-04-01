from django.db import models

class Comment(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    product_type = models.CharField(max_length=50) # 'laptops' or 'clothes'
    content = models.TextField()
    rating = models.IntegerField() # 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product_type': self.product_type,
            'content': self.content,
            'rating': self.rating,
            'created_at': self.created_at.isoformat()
        }
