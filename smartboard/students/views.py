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
        
        if roll_number:
            queryset = queryset.filter(roll_number__icontains=roll_number)
        if branch:
            queryset = queryset.filter(branch=branch)
        if hall_number:
            queryset = queryset.filter(exam_hall_number=hall_number)
            
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
    parser_classes = [MultiPartParser, FormParser]
    
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
    """Send email to individual student"""
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
    """Send emails to multiple students"""
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
    """Send exam room allocation email to a student"""
    try:
        subject = f'Exam Room Allocation - {student.roll_number}'
        message = f"""
Dear {student.name},

Your exam room has been allocated for the upcoming examination.

Student Details:
- Name: {student.name}
- Roll Number: {student.roll_number}
- Branch: {student.get_branch_display()}
- Exam Hall Number: {student.exam_hall_number}

Please arrive at the exam hall at least 30 minutes before the scheduled exam time.

Best regards,
MITS Examination Cell
        """.strip()
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email_address],
            fail_silently=False,
        )
        
        return {
            'success': True,
            'student_id': student.id,
            'roll_number': student.roll_number,
            'email': student.email_address,
            'message': 'Email sent successfully'
        }
        
    except Exception as e:
        logger.error(f"Failed to send email to {student.roll_number}: {str(e)}")
        return {
            'success': False,
            'student_id': student.id,
            'roll_number': student.roll_number,
            'email': student.email_address,
            'error': str(e)
        }

def send_bulk_emails(students):
    """Send emails to multiple students"""
    results = []
    
    for student in students:
        result = send_exam_room_email(student)
        results.append(result)
        
        # Update email_sent status
        if result['success']:
            student.email_sent = True
            student.save(update_fields=['email_sent'])
    
    return results

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_statistics(request):
    """Get system statistics"""
    total_students = Student.objects.count()
    emails_sent = Student.objects.filter(email_sent=True).count()
    branches_stats = {}
    
    for branch_code, branch_name in Student.BRANCH_CHOICES:
        count = Student.objects.filter(branch=branch_code).count()
        if count > 0:
            branches_stats[branch_code] = {
                'name': branch_name,
                'count': count
            }
    
    return Response({
        'total_students': total_students,
        'emails_sent': emails_sent,
        'emails_pending': total_students - emails_sent,
        'branches_statistics': branches_stats
    })


