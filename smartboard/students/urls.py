# students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student CRUD operations
    path('', views.StudentListCreateView.as_view(), name='student-list-create'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # Hierarchical filtering endpoints
    path('branches/', views.get_branches, name='get-branches'),
    path('branches/<str:branch_code>/years/', views.get_years_by_branch, name='get-years-by-branch'),
    path('branches/<str:branch_code>/years/<str:year>/sections/', views.get_sections_by_branch_year, name='get-sections-by-branch-year'),
    path('branches/<str:branch_code>/years/<str:year>/sections/<str:section>/students/', views.get_students_by_branch_year_section, name='get-students-by-branch-year-section'),
    path('hierarchy/', views.get_hierarchy_overview, name='hierarchy-overview'),
    
    # File upload
    path('upload/', views.upload_students_file, name='upload-students'),
    
    # Email operations
    path('<int:student_id>/send-email/', views.send_individual_email, name='send-individual-email'),
    path('send-bulk-emails/', views.send_bulk_emails_view, name='send-bulk-emails'),
    path('test-email/', views.test_email_configuration, name='test-email'),
    
    # Statistics
    path('statistics/', views.get_statistics, name='statistics'),
]