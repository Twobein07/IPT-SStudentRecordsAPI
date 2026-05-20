from django.db import models
from django.contrib.auth.models import User


class StudentRecord(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_records')
    full_name = models.CharField(max_length=100)
    course = models.CharField(max_length=50)
    year_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.course} (Yr {self.year_level})"


class PaymentRecord(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_records')
    card_holder = models.CharField(max_length=100)
    encrypted_card_number = models.TextField()
    encrypted_cvv = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} by {self.card_holder}"
