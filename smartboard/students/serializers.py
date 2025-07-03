# students/serializers.py
from rest_framework import serializers
from .models import Student
import pandas as pd

class StudentSerializer(serializers.ModelSerializer):
    email_address = serializers.ReadOnlyField()
    institutional_email = serializers.ReadOnlyField()
    full_class_info = serializers.ReadOnlyField()
    branch_display = serializers.CharField(source='get_branch_display', read_only=True)
    year_display = serializers.CharField(source='get_year_display', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'name', 'roll_number', 'phone_number', 
            'gmail_address', 'branch', 'branch_display', 'year', 'year_display',
            'exam_hall_number', 'email_sent', 'email_address', 'institutional_email', 
            'full_class_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email_sent', 'created_at', 'updated_at']

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'name', 'roll_number', 'phone_number', 
            'gmail_address', 'branch', 'year', 'exam_hall_number'
        ]
    
    def validate_gmail_address(self, value):
        """Validate that the email is a Gmail address"""
        if value and not value.lower().endswith('@gmail.com'):
            raise serializers.ValidationError(
                "Please provide a valid Gmail address ending with @gmail.com"
            )
        return value.lower() if value else value
    
    def validate(self, data):
        """Validate branch and year combinations"""
        branch = data.get('branch')
        year = data.get('year')
        
        # Check if branch is valid
        valid_branches = [choice[0] for choice in Student.BRANCH_CHOICES]
        if branch not in valid_branches:
            raise serializers.ValidationError(f"Invalid branch. Choose from: {', '.join(valid_branches)}")
        
        # Check if year is valid
        valid_years = [choice[0] for choice in Student.YEAR_CHOICES]
        if year not in valid_years:
            raise serializers.ValidationError(f"Invalid year. Choose from: {', '.join(valid_years)}")
        
        return data

class ExamRoomUploadSerializer(serializers.Serializer):
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
        """Process uploaded file and update student exam room numbers"""
        try:
            # Read file based on extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Expected columns: S.No, Roll No, Room No
            expected_columns = ['S.No', 'Roll No', 'Room No']
            
            # Check if all required columns are present (case insensitive)
            df_columns = [col.strip() for col in df.columns]
            missing_columns = []
            column_mapping = {}
            
            for expected_col in expected_columns:
                found = False
                for df_col in df_columns:
                    if df_col.lower() == expected_col.lower():
                        column_mapping[expected_col] = df_col
                        found = True
                        break
                if not found:
                    missing_columns.append(expected_col)
            
            if missing_columns:
                raise serializers.ValidationError(
                    f"Missing required columns: {', '.join(missing_columns)}. "
                    f"Expected columns: {', '.join(expected_columns)}"
                )
            
            # Rename columns to standard format
            df = df.rename(columns={
                column_mapping['S.No']: 'sno',
                column_mapping['Roll No']: 'roll_number',
                column_mapping['Room No']: 'room_number'
            })
            
            # Clean and validate data
            df = df.dropna(subset=['roll_number', 'room_number'])
            
            processed_data = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    roll_number = str(row['roll_number']).strip().upper()
                    room_number = str(row['room_number']).strip()
                    
                    if not roll_number or not room_number:
                        errors.append(f"Row {index + 2}: Roll number and room number cannot be empty")
                        continue
                    
                    processed_data.append({
                        'roll_number': roll_number,
                        'room_number': room_number
                    })
                    
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            if errors:
                raise serializers.ValidationError({
                    'file_errors': errors,
                    'valid_records': len(processed_data)
                })
            
            return processed_data
            
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