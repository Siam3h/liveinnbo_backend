from django.db import models
from event.models import Event   

class Transaction(models.Model):
    name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, default = 0 , blank=True)
    ref = models.CharField(max_length=200, blank=True)  
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction for {self.event.title} by {self.email}"
