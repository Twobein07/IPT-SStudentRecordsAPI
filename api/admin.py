from django.contrib import admin
from .models import StudentRecord, PaymentRecord


class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'course', 'year_level', 'owner', 'created_at']
    list_filter = ['course', 'year_level']
    search_fields = ['full_name', 'course']


class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['card_holder', 'amount', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['card_holder']


admin.site.register(StudentRecord, StudentRecordAdmin)
admin.site.register(PaymentRecord, PaymentRecordAdmin)
