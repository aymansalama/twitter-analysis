from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Job(models.Model):
    keyword = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.keyword


class Tweet(models.Model):
    tweet_id = models.BigIntegerField()
    text = models.TextField()
    polarity = models.DecimalField(decimal_places=5,max_digits=6,null=True)
    keyword = models.CharField(max_length=255)
    country = models.CharField(max_length=255,null=True)
    stored_at = models.DateTimeField(editable= False)

    class Meta:
        indexes = [
            models.Index(fields=['keyword']),
        ]

    def save(self,*args, **kwargs):
        if not self.id:
            self.stored_at = timezone.now()
        return super(Tweet,self).save()

    def __str__(self):
        return self.text