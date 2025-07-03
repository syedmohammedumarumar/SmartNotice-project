# students/admin.py
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from .models import Student
import csv
from django.http import HttpResponse


class BranchFilter(SimpleListFilter):
    title = 'Branch'
    parameter_name = 'branch'
    
    def lookups(self, request, model_admin):
        return Student.BRANCH_CHOICES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(branch=self.value())
        return queryset


class YearFilter(SimpleListFilter):
    title = 'Year'
    parameter_name = 'year'
    
    def lookups(self, request, model_admin):
        return Student.YEAR_CHOICES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(year=self.value())
        return queryset


class EmailStatusFilter(SimpleListFilter):
    title = 'Email Status'
    parameter_name = 'email_status'
    
    def lookups(self, request, model_admin):
        return (
            ('sent', 'Email Sent'),
            ('pending', 'Email Pending'),
            ('no_email', 'No Gmail Address'),
            ('no_room', 'No Room Assigned'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'sent':
            return queryset.filter(email_sent=True)
        elif self.value() == 'pending':
            return queryset.filter(email_sent=False, gmail_address__isnull=False).exclude(gmail_address='')
        elif self.value() == 'no_email':
            return queryset.filter(Q(gmail_address__isnull=True) | Q(gmail_address=''))
        elif self.value() == 'no_room':
            return queryset.filter(Q(exam_hall_number__isnull=True) | Q(exam_hall_number=''))
        return queryset


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'roll_number', 'name', 'branch_display', 'year_display', 
        'exam_hall_number', 'gmail_status', 'email_status', 'created_at'
    ]
    
    list_filter = [
        BranchFilter, YearFilter, EmailStatusFilter, 
        'email_sent', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'roll_number', 'name', 'gmail_address', 'exam_hall_number', 'phone_number'
    ]
    
    list_per_page = 50
    
    ordering = ['branch', 'year', 'roll_number']
    
    readonly_fields = ['created_at', 'updated_at', 'institutional_email']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('name', 'roll_number', 'phone_number')
        }),
        ('Academic Details', {
            'fields': ('branch', 'year')
        }),
        ('Contact Information', {
            'fields': ('gmail_address', 'institutional_email')
        }),
        ('Exam Details', {
            'fields': ('exam_hall_number', 'email_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'export_to_csv', 'mark_email_sent', 'mark_email_pending', 
        'clear_exam_halls', 'send_bulk_emails'
    ]
    
    # Custom display methods
    def branch_display(self, obj):
        return obj.get_branch_display()
    branch_display.short_description = 'Branch'
    branch_display.admin_order_field = 'branch'
    
    def year_display(self, obj):
        return obj.get_year_display()
    year_display.short_description = 'Year'
    year_display.admin_order_field = 'year'
    
    def gmail_status(self, obj):
        if obj.gmail_address:
            return format_html('<span style="color: green;">✓ {}</span>', obj.gmail_address)
        return format_html('<span style="color: red;">✗ No Gmail</span>')
    gmail_status.short_description = 'Gmail Status'
    
    def email_status(self, obj):
        if obj.email_sent:
            return format_html('<span style="color: green;">✓ Sent</span>')
        elif not obj.gmail_address:
            return format_html('<span style="color: orange;">⚠ No Gmail</span>')
        elif not obj.exam_hall_number:
            return format_html('<span style="color: orange;">⚠ No Room</span>')
        else:
            return format_html('<span style="color: red;">✗ Pending</span>')
    email_status.short_description = 'Email Status'
    
    # Custom actions
    def export_to_csv(self, request, queryset):
        """Export selected students to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Roll Number', 'Name', 'Branch', 'Year', 'Gmail Address', 
            'Phone Number', 'Exam Hall Number', 'Email Sent', 'Created At'
        ])
        
        for student in queryset:
            writer.writerow([
                student.roll_number, student.name, student.get_branch_display(),
                student.get_year_display(), student.gmail_address or '',
                student.phone_number or '', student.exam_hall_number or '',
                'Yes' if student.email_sent else 'No', student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    export_to_csv.short_description = "Export selected students to CSV"
    
    def mark_email_sent(self, request, queryset):
        """Mark selected students as email sent"""
        count = queryset.update(email_sent=True)
        self.message_user(request, f'{count} students marked as email sent.')
    mark_email_sent.short_description = "Mark selected students as email sent"
    
    def mark_email_pending(self, request, queryset):
        """Mark selected students as email pending"""
        count = queryset.update(email_sent=False)
        self.message_user(request, f'{count} students marked as email pending.')
    mark_email_pending.short_description = "Mark selected students as email pending"
    
    def clear_exam_halls(self, request, queryset):
        """Clear exam hall numbers for selected students"""
        count = queryset.update(exam_hall_number=None)
        self.message_user(request, f'Exam hall numbers cleared for {count} students.')
    clear_exam_halls.short_description = "Clear exam hall numbers for selected students"
    
    def send_bulk_emails(self, request, queryset):
        """Send emails to selected students (requires valid Gmail and exam hall)"""
        # Filter students who have both Gmail and exam hall number
        valid_students = queryset.filter(
            gmail_address__isnull=False,
            exam_hall_number__isnull=False
        ).exclude(
            gmail_address='',
            exam_hall_number=''
        )
        
        if not valid_students.exists():
            self.message_user(request, 'No valid students found (must have Gmail address and exam hall number).', level='WARNING')
            return
        
        # Import the email function from views
        from .views import send_bulk_emails
        
        try:
            email_results = send_bulk_emails(valid_students)
            successful_emails = len([r for r in email_results if r['success']])
            failed_emails = len([r for r in email_results if not r['success']])
            
            self.message_user(
                request, 
                f'Bulk email completed: {successful_emails} sent successfully, {failed_emails} failed.'
            )
        except Exception as e:
            self.message_user(request, f'Error sending bulk emails: {str(e)}', level='ERROR')
    
    send_bulk_emails.short_description = "Send emails to selected students"
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view"""
        queryset = super().get_queryset(request)
        return queryset.select_related()
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to changelist view"""
        extra_context = extra_context or {}
        
        # Get statistics
        total_students = Student.objects.count()
        students_with_gmail = Student.objects.exclude(gmail_address='').count()
        students_with_rooms = Student.objects.exclude(exam_hall_number='').count()
        emails_sent = Student.objects.filter(email_sent=True).count()
        
        # Branch-wise statistics
        branch_stats = Student.objects.values('branch').annotate(
            count=Count('id')
        ).order_by('branch')
        
        extra_context['summary_stats'] = {
            'total_students': total_students,
            'students_with_gmail': students_with_gmail,
            'students_with_rooms': students_with_rooms,
            'emails_sent': emails_sent,
            'emails_pending': total_students - emails_sent,
            'branch_stats': branch_stats
        }
        
        return super().changelist_view(request, extra_context=extra_context)


# Custom admin site configuration (optional)
admin.site.site_header = 'MITS Student Management System'
admin.site.site_title = 'MITS Admin'
admin.site.index_title = 'Student Management Dashboard'