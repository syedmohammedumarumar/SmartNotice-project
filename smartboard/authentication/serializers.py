# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import UserProfile, OTPVerification
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=15, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_phone_number(self, value):
        # Remove any spaces, dashes, or parentheses
        phone = re.sub(r'[\s\-\(\)]', '', value)
        
        # Check if phone number contains only digits and optional + at the beginning
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise serializers.ValidationError("Enter a valid phone number.")
        
        # Check if phone number already exists
        if UserProfile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        
        return value
    
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(**validated_data)
        
        # Create or update user profile with phone number
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.phone_number = phone_number
        user_profile.save()
        
        return user


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'date_joined')
        read_only_fields = ('id', 'date_joined')
    
    def get_phone_number(self, obj):
        try:
            return obj.userprofile.phone_number
        except UserProfile.DoesNotExist:
            return None
    
    def update(self, instance, validated_data):
        # Handle phone_number separately
        phone_number = validated_data.pop('phone_number', None)
        
        # Update user fields
        instance = super().update(instance, validated_data)
        
        # Update phone number in profile
        if phone_number is not None:
            user_profile, created = UserProfile.objects.get_or_create(user=instance)
            user_profile.phone_number = phone_number
            user_profile.save()
        
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password')

            if not user.check_password(password):
                raise serializers.ValidationError('Invalid email or password')

            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')

            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        return value
    
    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        
        # Delete any existing OTPs for this user for password reset
        OTPVerification.objects.filter(
            user=user, 
            purpose='password_reset',
            is_used=False
        ).delete()
        
        # Create new OTP
        otp_obj = OTPVerification.objects.create(
            user=user,
            purpose='password_reset'
        )
        
        # Send OTP email
        subject = 'Password Reset OTP'
        message = f"""
        Hello {user.username},
        
        You have requested to reset your password. Please use the following OTP to verify your identity:
        
        OTP: {otp_obj.otp_code}
        
        This OTP is valid for 10 minutes only.
        
        If you did not request this password reset, please ignore this email.
        
        Best regards,
        Your App Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            raise serializers.ValidationError(f"Failed to send email: {str(e)}")


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6, min_length=6)
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp_code = attrs.get('otp_code')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address.")
        
        # Find the OTP
        try:
            otp_obj = OTPVerification.objects.get(
                user=user,
                otp_code=otp_code,
                purpose='password_reset',
                is_used=False
            )
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")
        
        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6, min_length=6)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        
        email = attrs.get('email')
        otp_code = attrs.get('otp_code')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address.")
        
        # Find the OTP
        try:
            otp_obj = OTPVerification.objects.get(
                user=user,
                otp_code=otp_code,
                purpose='password_reset',
                is_used=False
            )
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")
        
        attrs['user'] = user
        attrs['otp_obj'] = otp_obj
        return attrs
    
    def save(self):
        user = self.validated_data['user']
        otp_obj = self.validated_data['otp_obj']
        new_password = self.validated_data['new_password']
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Delete all other unused OTPs for this user
        OTPVerification.objects.filter(
            user=user,
            purpose='password_reset',
            is_used=False
        ).delete()
        
        return user