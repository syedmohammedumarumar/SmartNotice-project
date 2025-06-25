from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student CRUD operations
    path('', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # File upload
    path('upload/', views.upload_students_file, name='upload-students'),
    
    # Email operations
    path('<int:student_id>/send-email/', views.send_individual_email, name='send-individual-email'),
    path('send-bulk-emails/', views.send_bulk_emails_view, name='send-bulk-emails'),
    path('test-email/', views.test_email_configuration, name='test-email'),
    
    # Statistics
    path('statistics/', views.get_statistics, name='statistics'),
]
