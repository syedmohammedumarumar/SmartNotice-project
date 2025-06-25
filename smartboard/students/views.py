# students/views.py
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from .models import Student
from .serializers import (
    StudentSerializer, StudentCreateSerializer, 
    FileUploadSerializer, BulkEmailSerializer
)
import logging
import time

logger = logging.getLogger(__name__)

class StudentListCreateView(generics.ListCreateAPIView):
    """List all students or create a new student"""
    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentCreateSerializer
        return StudentSerializer
    
    def get_queryset(self):
        queryset = Student.objects.all()
        roll_number = self.request.query_params.get('roll_number')
        branch = self.request.query_params.get('branch')
        hall_number = self.request.query_params.get('hall_number')
        gmail = self.request.query_params.get('gmail')
        
        if roll_number:
            queryset = queryset.filter(roll_number__icontains=roll_number)
        if branch:
            queryset = queryset.filter(branch=branch)
        if hall_number:
            queryset = queryset.filter(exam_hall_number=hall_number)
        if gmail:
            queryset = queryset.filter(gmail_address__icontains=gmail)
            
        return queryset

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a student"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_students_file(request):
    """Upload Excel/CSV file and create student records"""
    serializer = FileUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    file = serializer.validated_data['file']
    send_emails = serializer.validated_data['send_emails']
    
    try:
        # Process file
        students_data = serializer.process_file(file, send_emails)
        
        created_students = []
        updated_students = []
        email_results = []
        
        with transaction.atomic():
            for student_data in students_data:
                student, created = Student.objects.update_or_create(
                    roll_number=student_data['roll_number'],
                    defaults=student_data
                )
                
                if created:
                    created_students.append(student)
                else:
                    updated_students.append(student)
        
        # Send emails if requested
        if send_emails:
            all_students = created_students + updated_students
            email_results = send_bulk_emails(all_students)
        
        return Response({
            'message': 'File processed successfully',
            'created_count': len(created_students),
            'updated_count': len(updated_students),
            'total_processed': len(students_data),
            'emails_sent': len([r for r in email_results if r['success']]) if send_emails else 0,
            'email_failures': len([r for r in email_results if not r['success']]) if send_emails else 0,
            'email_results': email_results if send_emails else []
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        return Response({
            'error': 'Failed to process file',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_individual_email(request, student_id):
    """Send email to individual student's Gmail"""
    try:
        student = Student.objects.get(id=student_id)
        result = send_exam_room_email(student)
        
        if result['success']:
            student.email_sent = True
            student.save()
            
        return Response({
            'message': f'Email sending {"successful" if result["success"] else "failed"}',
            'student': StudentSerializer(student).data,
            'email_result': result
        }, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)
        
    except Student.DoesNotExist:
        return Response({
            'error': 'Student not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_bulk_emails_view(request):
    """Send emails to multiple students' Gmail addresses"""
    serializer = BulkEmailSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    student_ids = serializer.validated_data['student_ids']
    students = Student.objects.filter(id__in=student_ids)
    
    email_results = send_bulk_emails(students)
    
    return Response({
        'message': 'Bulk email sending completed',
        'total_students': len(students),
        'emails_sent': len([r for r in email_results if r['success']]),
        'email_failures': len([r for r in email_results if not r['success']]),
        'results': email_results
    }, status=status.HTTP_200_OK)

def send_exam_room_email(student):
    """Send exam room allocation email to student's Gmail"""
    try:
        subject = f'Exam Room Allocation - {student.roll_number} | MITS'
        
        # Enhanced email template
        message = f"""
Dear {student.name},

Your exam room has been allocated for the upcoming examination.

📚 STUDENT DETAILS:
━━━━━━━━━━━━━━━━━━━━━
👤 Name: {student.name}
🎓 Roll Number: {student.roll_number}
🏛️ Branch: {student.get_branch_display()}
🏢 Exam Hall Number: {student.exam_hall_number}
📧 Contact Email: {student.gmail_address}

⚠️ IMPORTANT INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━
• Please arrive at the exam hall at least 30 minutes before the scheduled exam time
• Bring your valid student ID card and hall ticket
• Mobile phones and electronic devices are strictly prohibited in the exam hall
• Reach the venue early to avoid any last-minute rush

📍 Exam Hall Location: Hall Number {student.exam_hall_number}

For any queries, please contact the examination cell.

Best regards,
MITS Examination Cell
Madanapalle Institute of Technology & Science

---
This is an automated message. Please do not reply to this email.
        """.strip()
        
        # Send email using Gmail SMTP
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.gmail_address],
            fail_silently=False,
        )
        
        logger.info(f"Email sent successfully to {student.roll_number} at {student.gmail_address}")
        
        return {
            'success': True,
            'student_id': student.id,
            'roll_number': student.roll_number,
            'email': student.gmail_address,
            'message': 'Email sent successfully to Gmail'
        }
        
    except Exception as e:
        logger.error(f"Failed to send email to {student.roll_number} at {student.gmail_address}: {str(e)}")
        return {
            'success': False,
            'student_id': student.id,
            'roll_number': student.roll_number,
            'email': student.gmail_address,
            'error': str(e)
        }

def send_bulk_emails(students):
    """Send emails to multiple students' Gmail addresses with rate limiting"""
    results = []
    successful_count = 0
    
    for i, student in enumerate(students):
        # Rate limiting: add delay every 10 emails to avoid Gmail rate limits
        if i > 0 and i % 10 == 0:
            time.sleep(2)  # 2 second delay every 10 emails
        
        result = send_exam_room_email(student)
        results.append(result)
        
        # Update email_sent status
        if result['success']:
            student.email_sent = True
            student.save(update_fields=['email_sent'])
            successful_count += 1
    
    logger.info(f"Bulk email completed: {successful_count}/{len(students)} emails sent successfully")
    return results

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_statistics(request):
    """Get system statistics"""
    total_students = Student.objects.count()
    emails_sent = Student.objects.filter(email_sent=True).count()
    students_with_gmail = Student.objects.exclude(gmail_address='').count()
    branches_stats = {}
    
    for branch_code, branch_name in Student.BRANCH_CHOICES:
        count = Student.objects.filter(branch=branch_code).count()
        if count > 0:
            branches_stats[branch_code] = {
                'name': branch_name,
                'count': count,
                'emails_sent': Student.objects.filter(branch=branch_code, email_sent=True).count()
            }
    
    return Response({
        'total_students': total_students,
        'students_with_gmail': students_with_gmail,
        'emails_sent': emails_sent,
        'emails_pending': total_students - emails_sent,
        'branches_statistics': branches_stats
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_email_configuration(request):
    """Test Gmail SMTP configuration"""
    try:
        # Send test email
        send_mail(
            subject='Test Email - MITS Exam System',
            message='This is a test email to verify Gmail SMTP configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': 'Test email sent successfully',
            'smtp_host': settings.EMAIL_HOST,
            'from_email': settings.DEFAULT_FROM_EMAIL
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Email configuration test failed: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Email configuration test failed'
        }, status=status.HTTP_400_BAD_REQUEST)
