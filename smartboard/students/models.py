# students/models.py
from django.db import models
from django.core.validators import RegexValidator, EmailValidator

class Student(models.Model):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('IT', 'Information Technology'),
        ('AIML', 'Artificial Intelligence and Machine Learning'),
        ('CSBS', 'Computer Science and Business Systems'),
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
        )]
    )
    
    gmail_address = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        help_text="Student's Gmail address for exam notifications",
        null=True,
        blank=True
    )
    
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    exam_hall_number = models.CharField(max_length=20)
    email_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        return f"{self.roll_number} - {self.name}"
    
    @property
    def email_address(self):
        return self.gmail_address
    
    @property
    def institutional_email(self):
        return f"{self.roll_number.lower()}@mits.ac.in"