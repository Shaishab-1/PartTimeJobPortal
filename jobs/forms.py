from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['age', 'qualifications', 'skills', 'professional_details']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'Enter your age'
            }),
            'qualifications': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'e.g. B.Sc in Computer Science',
                'rows': 3
            }),
            'skills': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'e.g. Python, Django, Tailwind CSS',
                'rows': 3
            }),
            'professional_details': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition',
                'placeholder': 'Tell us more about your experience',
                'rows': 4
            }),
        }
