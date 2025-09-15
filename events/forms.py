from django import forms
from .models import User

class ClubRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {
    'username': None,  # Remove help text
}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'club'
        user.is_staff = True
        user.is_superuser = False
        user.is_active = False  # Optional: require admin approval before login
        if commit:
            user.save()
        return user



from django import forms
from .models import Event
from django import forms
from .models import Event
from django.utils import timezone

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'venue', 'date', 'start_time', 'end_time', 'guest', 'image', 'total_seats']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
      

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Event date cannot be in the past.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data


# forms.py
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment', 'rating']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Leave your feedback here...'}),
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),  # Create choices for rating 1-5
        }


from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email ID', 'required': 'required'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your message', 'rows': 4, 'required': 'required'}),
        }
