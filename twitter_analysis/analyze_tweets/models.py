from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Keyword(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    avg_polarity = models.DecimalField(decimal_places=5,max_digits=6,null=True)
    tweet_count = models.BigIntegerField(null=True)
    
    def __str__(self):
        return self.keyword

    def get_absolute_url(self):
        return reverse('keyword_detail', args=[str(self.id)])

class Job(models.Model):
    Pending = 'PENDING'
    Running = 'RUNNING'
    Completed = 'COMPLETED'

    JOB_CHOICES = (
        (Pending, 'PENDING'),
        (Running, 'RUNNING'),
        (Completed, 'COMPLETED'),
    )
    
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    job_status = models.CharField(max_length=255,choices=JOB_CHOICES,default=Pending)
    last_modified = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.keyword.keyword

    def get_absolute_url(self):
        return reverse('job_detail', args=[str(self.pk)])

class Tweet(models.Model):
    tweet_id = models.BigIntegerField()
    text = models.TextField()
    polarity = models.DecimalField(decimal_places=5,max_digits=6,null=True)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    country = models.CharField(max_length=255,null=True)
    stored_at = models.DateTimeField(editable= False)

    class Meta:
        indexes = [
            models.Index(fields=['keyword']),
        ]

    def save(self,*args, **kwargs):
        if not self.id:
            if not self.stored_at:
                self.stored_at = timezone.now()
        return super(Tweet,self).save()

    def __str__(self):
        return self.text

    def yearpublished(self):
        return self.stored_at.strftime('%Y')