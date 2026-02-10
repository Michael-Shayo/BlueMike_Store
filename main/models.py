from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    )

    role = models.CharField(
        max_length=10,choices=ROLE_CHOICES,default='buyer'
    )

    phone = models.CharField(
        max_length=20,unique=True,null=True,blank=True
    )

    status = models.CharField(
        max_length=10,choices=STATUS_CHOICES,default='active'
    )

    def is_buyer(self):
        return self.role == 'buyer'

    def is_seller(self):
        return self.role == 'seller'

    def is_admin(self):
        return self.role == 'admin'

    def __str__(self):
        return self.username
    

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    address = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class SellerProfile(models.Model):
    TANZANIA_REGIONS = (
        ('arusha', 'Arusha'),
        ('dar_es_salaam', 'Dar es Salaam'),
        ('dodoma', 'Dodoma'),
        ('geita', 'Geita'),
        ('iringa', 'Iringa'),
        ('kagera', 'Kagera'),
        ('katavi', 'Katavi'),
        ('kigoma', 'Kigoma'),
        ('kilimanjaro', 'Kilimanjaro'),
        ('lindi', 'Lindi'),
        ('manyara', 'Manyara'),
        ('mara', 'Mara'),
        ('mbeya', 'Mbeya'),
        ('morogoro', 'Morogoro'),
        ('mtwara', 'Mtwara'),
        ('mwanza', 'Mwanza'),
        ('njombe', 'Njombe'),
        ('pemba_north', 'Pemba North'),
        ('pemba_south', 'Pemba South'),
        ('pwani', 'Pwani'),
        ('rukwa', 'Rukwa'),
        ('ruvuma', 'Ruvuma'),
        ('shinyanga', 'Shinyanga'),
        ('simiyu', 'Simiyu'),
        ('singida', 'Singida'),
        ('songwe', 'Songwe'),
        ('tabora', 'Tabora'),
        ('tanga', 'Tanga'),
        ('unguja_north', 'Unguja North'),
        ('unguja_south', 'Unguja South'),
        ('zanzibar_west', 'Zanzibar West'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField()
    region = models.CharField(
        max_length=50,
        choices=TANZANIA_REGIONS
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name
    
 
# class ShopLocation(models.Model):
#     seller = models.OneToOneField(
#         "SellerProfile",
#         on_delete=models.CASCADE,
#         related_name="location"
#     )

#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.seller.business_name} Location"