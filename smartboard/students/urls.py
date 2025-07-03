# students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student CRUD operations
    path('', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # Hierarchical filtering endpoints (without sections)
    path('branches/', views.get_branches, name='get-branches'),
    path('branches/<str:branch_code>/years/', views.get_years_by_branch, name='get-years-by-branch'),
    path('branches/<str:branch_code>/years/<str:year>/students/', views.get_students_by_branch_year, name='get-students-by-branch-year'),
    path('hierarchy/', views.get_hierarchy_overview, name='hierarchy-overview'),
    
    # Exam room file upload (new endpoint)
    path('upload-rooms/', views.upload_exam_room_file, name='upload-exam-rooms'),
    
    # Email operations
    path('<int:student_id>/send-email/', views.send_individual_email, name='send-individual-email'),
    path('send-bulk-emails/', views.send_bulk_emails_view, name='send-bulk-emails'),
    path('test-email/', views.test_email_configuration, name='test-email'),
    
    # Statistics
    path('statistics/', views.get_statistics, name='statistics'),
]