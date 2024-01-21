from django import forms
from .models import  Contact, Comment


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact  # Replace 'Contact' with your actual model name
        fields = '__all__'  # Include all fields from the model

class SubscriberForm(forms.ModelForm):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    email = forms.EmailField()

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['body']
