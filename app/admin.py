from django.contrib import admin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import User, Patient, Report
from .models import DocumentFolderPath

admin.site.register(DocumentFolderPath)

from django.contrib import admin

class ReportAdmin(admin.ModelAdmin):
    list_display = ("patient_firstname", "patient_lastname", "user_username", "date")

    def patient_firstname(self, obj):
        return obj.patient.firstname if obj.patient else 'No Patient'

    def patient_lastname(self, obj):
        return obj.patient.lastname if obj.patient else 'No Patient'

    def user_username(self, obj):
        return obj.user.username if obj.user else 'No User'

    patient_firstname.short_description = 'Patient Firstname'
    patient_lastname.short_description = 'Patient Lastname'
    user_username.short_description = 'User Username'

admin.site.register(Report, ReportAdmin)
admin.site.register(Patient)

class CustomUserCreationForm(UserCreationForm):
    role = forms.CharField(label='Role')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'role')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    role = forms.CharField(label='Role')
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  
    form = CustomUserChangeForm
    fieldsets = UserAdmin.fieldsets + ( 
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)
