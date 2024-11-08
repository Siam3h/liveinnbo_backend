from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    #ModelMetadata = models.ForeignKey()
    
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',  
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions',  
        related_query_name='user',
    )

    def __str__(self):
        return self.username

    def set_password(self, new_password):
        self.password = make_password(new_password)
        self.save()

