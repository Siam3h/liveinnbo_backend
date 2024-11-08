from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    meta = models.CharField(max_length=300, null=True, blank=True,)
    location = models.CharField(max_length=300, default="N/A")
    content = models.TextField()
    thumbnail_img = models.ImageField(null=True, blank=True, upload_to="images/")
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=255, default="uncategorized")
    created_at = models.DateField(auto_now_add=True)
    price = models.PositiveIntegerField(default=0)
    receipt = models.FileField(upload_to='events/receipts/', null=True, blank=True,)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True) 
    
    @property
    def get_image_url(self):
        return self.receipt.url

    def __str__(self):
        return self.title 