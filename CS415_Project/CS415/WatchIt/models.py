from django.db import models

class Payment_detail(models.Model):
    id= models.AutoField
    payment_Name = models.CharField(null=True)
    payment_amount = models.DecimalField(null=True, decimal_places=2, max_digits=20)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)
