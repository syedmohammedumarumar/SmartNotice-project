from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'name', 'branch', 'exam_hall_number', 'email_sent', 'created_at']
    list_filter = ['branch', 'exam_hall_number', 'email_sent', 'created_at']
    search_fields = ['roll_number', 'name', 'phone_number']
    list_editable = ['exam_hall_number']
    ordering = ['roll_number']
    
    actions = ['send_emails_to_selected']
    
    def send_emails_to_selected(self, request, queryset):
        from .views import send_bulk_emails
        results = send_bulk_emails(queryset)
        success_count = len([r for r in results if r['success']])
        self.message_user(
            request, 
            f"Emails sent to {success_count} out of {queryset.count()} students."
        )
    send_emails_to_selected.short_description = "Send exam room emails to selected students"