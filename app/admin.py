from django.contrib import admin
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import User, Patient, Report

admin.site.register(Report)
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
