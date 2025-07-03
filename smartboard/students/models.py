# students/models.py
from django.db import models
from django.core.validators import RegexValidator, EmailValidator

class Student(models.Model):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science & Engineering (CSE)'),
        ('CSM', 'Computer Science & Engineering - AI & ML (CSM)'),
        ('CAI', 'Computer Science & Engineering - Artificial Intelligence (CAI)'),
        ('CSD', 'Computer Science & Engineering - Data Science (CSD)'),
        ('CSC', 'Computer Science & Engineering - Cyber Security (CSC)'),
        ('ECE', 'Electronics and Communication Engineering (ECE)'),
        ('EEE', 'Electrical and Electronics Engineering (EEE)'),
        ('ME', 'Mechanical Engineering (ME)'),
        ('CIV', 'Civil Engineering (CIV)'),
    ]
    
    YEAR_CHOICES = [
        ('1', '1st Year'),
        ('2', '2nd Year'),
        ('3', '3rd Year'),
        ('4', '4th Year'),
    ]
    
    name = models.CharField(max_length=100)
    
    roll_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Za-z0-9]+$',
            message='Roll number must be alphanumeric'
        )]
    )
    
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be 9-15 digits'
        )],
        null=True,
        blank=True
    )
    
    gmail_address = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        help_text="Student's Gmail address for exam notifications",
        null=True,
        blank=True
    )
    
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES, default='1')
    exam_hall_number = models.CharField(max_length=20, null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['branch', 'year', 'roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        unique_together = ['branch', 'year', 'roll_number']
    
    def __str__(self):
        return f"{self.roll_number} - {self.name} ({self.branch} {self.year})"
    
    @property
    def email_address(self):
        return self.gmail_address
    
    @property
    def institutional_email(self):
        return f"{self.roll_number.lower()}@mits.ac.in"
    
    @property
    def full_class_info(self):
        return f"{self.get_branch_display()} - {self.get_year_display()}"