# blogs/models.py

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class Blog(models.Model):
    title = models.CharField(max_length=200)
    meta = models.CharField(max_length=300, null=True, blank=True,)
    content = models.TextField()
    thumbnail_img = models.ImageField(null=True, blank=True, upload_to="images/")
    thumbnail_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=255, default="uncategorized")
    slug = models.CharField(max_length=100, unique=True, blank=True)
    time = models.DateField(auto_now_add=True,null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  
    is_approved = models.BooleanField(default=False)  
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) 
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
