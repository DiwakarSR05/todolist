from django import forms
from .models import Task, Category,UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control form-control-lg'
            })

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Remove 'user' from kwargs before passing to super()
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter categories by user
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'reminder']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'reminder': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add details about your task...', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'placeholder': 'What needs to be done?', 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Category name'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
        
        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    remove_picture = forms.BooleanField(
        required=False, 
        widget=forms.HiddenInput(),
        initial=False
    )
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'phone_number', 'location']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control d-none'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+977 980000000'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your location'}),
        }