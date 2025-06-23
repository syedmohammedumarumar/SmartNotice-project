from rest_framework import serializers
from .models import Student
import pandas as pd
import openpyxl

class StudentSerializer(serializers.ModelSerializer):
    email_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'roll_number', 'phone_number', 
            'branch', 'exam_hall_number', 'email_sent', 
            'email_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email_sent', 'created_at', 'updated_at']

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'name', 'roll_number', 'phone_number', 
            'branch', 'exam_hall_number'
        ]

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    send_emails = serializers.BooleanField(default=True)
    
    def validate_file(self, value):
        """Validate uploaded file format"""
        if not value.name.endswith(('.xlsx', '.xls', '.csv')):
            raise serializers.ValidationError(
                "Only Excel (.xlsx, .xls) and CSV files are allowed."
            )
        return value
    
    def process_file(self, file, send_emails=True):
        """Process uploaded file and create student records"""
        try:
            # Read file based on extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['name', 'roll_number', 'phone_number', 'branch', 'exam_hall_number']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise serializers.ValidationError(
                    f"Missing required columns: {', '.join(missing_columns)}"
                )
            
            # Clean and validate data
            df = df.dropna(subset=required_columns)
            students_data = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    student_data = {
                        'name': str(row['name']).strip(),
                        'roll_number': str(row['roll_number']).strip().upper(),
                        'phone_number': str(row['phone_number']).strip(),
                        'branch': str(row['branch']).strip().upper(),
                        'exam_hall_number': str(row['exam_hall_number']).strip(),
                    }
                    
                    # Validate individual student data
                    serializer = StudentCreateSerializer(data=student_data)
                    if serializer.is_valid():
                        students_data.append(student_data)
                    else:
                        errors.append(f"Row {index + 2}: {serializer.errors}")
                        
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            if errors:
                raise serializers.ValidationError({
                    'file_errors': errors,
                    'valid_records': len(students_data)
                })
            
            return students_data
            
        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise e
            raise serializers.ValidationError(f"Error processing file: {str(e)}")

class BulkEmailSerializer(serializers.Serializer):
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    
    def validate_student_ids(self, value):
        """Validate that all student IDs exist"""
        existing_ids = Student.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Students with IDs {list(missing_ids)} do not exist."
            )
        return value