from django.db import models

class Interaction(models.Model):
    user_id = models.IntegerField()
    product_id = models.IntegerField()
    action = models.CharField(max_length=50) # VIEW, ADD_CART, PURCHASE
    weight = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Recommendation(models.Model):
    user_id = models.IntegerField(unique=True)
    product_ids = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)
