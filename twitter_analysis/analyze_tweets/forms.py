from django import forms 
from analyze_tweets.models import Job,User
from django.contrib.auth import get_user_model
from django.shortcuts import  get_object_or_404
from django.utils import timezone

class AddJobForm(forms.Form):
   
    
    
    keyword = forms.CharField(required=True, max_length=255, label="Enter your keyword here")
    start_date = forms.DateTimeField(initial = timezone.now())
    end_date = forms.DateTimeField()

    # this should be temporary, should be removed after authentication is working
    # user = forms.ModelChoiceField(queryset=User.objects.all())


class UpdateJobForm(forms.Form):

    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()

    # this should be temporary, should be removed after authentication is working
    # user = forms.ModelChoiceField(queryset=User.objects.all())

