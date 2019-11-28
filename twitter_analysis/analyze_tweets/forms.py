from django import forms 
from analyze_tweets.models import Job
from django.contrib.auth import get_user_model
import datetime

class AddJobForm(forms.Form):
    User = get_user_model()
    keyword = forms.CharField(required=True, max_length=255, label="Enter your keyword here")
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    user = forms.ModelChoiceField(queryset=User.objects.all())

