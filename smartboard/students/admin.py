# students/admin.py
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'name', 'branch', 'gmail_address', 'exam_hall_number', 'email_sent', 'created_at']
    list_filter = ['branch', 'exam_hall_number', 'email_sent', 'created_at']
    search_fields = ['roll_number', 'name', 'phone_number', 'gmail_address']
    list_editable = ['exam_hall_number']
    ordering = ['roll_number']
    
    actions = ['send_emails_to_selected', 'mark_emails_as_sent', 'mark_emails_as_not_sent']
    
    def send_emails_to_selected(self, request, queryset):
        from .views import send_bulk_emails
        results = send_bulk_emails(queryset)
        success_count = len([r for r in results if r['success']])
        self.message_user(
            request, 
            f"Emails sent to {success_count} out of {queryset.count()} students."
        )
    send_emails_to_selected.short_description = "Send exam room emails to selected students"
    
    def mark_emails_as_sent(self, request, queryset):
        updated = queryset.update(email_sent=True)
        self.message_user(request, f"{updated} students marked as email sent.")
    mark_emails_as_sent.short_description = "Mark selected students as email sent"
    
    def mark_emails_as_not_sent(self, request, queryset):
        updated = queryset.update(email_sent=False)
        self.message_user(request, f"{updated} students marked as email not sent.")
    mark_emails_as_not_sent.short_description = "Mark selected students as email not sent"
