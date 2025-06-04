from django.db import models

# Create your models here.
class QRCode(models.Model):
    data=models.CharField()
    mobile_number=models.CharField()

    def __str__(self):
        return f"{self.data} - {self.mobile_number}"  