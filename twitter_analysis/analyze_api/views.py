#Stdlib imports

# Core Django imports
from django.db.models import Avg
from django.contrib.auth.models import User

# Third-party app imports
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404

# Imports from your apps
from analyze_tweets.models import Tweet, Keyword, Job
from analyze_tweets.views import get_top_10_words, JobStream,scheduler
from analyze_api.permissions import IsOwnerOrReadOnly
from analyze_api.serializers import TweetSerializer, KeywordSerializer, TweetAvgSerializer, JobSerializer, UserSerializer
from apscheduler.schedulers.background import BackgroundScheduler



# Create your views here.
class TweetFilter(filters.FilterSet):
    keyword = filters.CharFilter(field_name='keyword__keyword', lookup_expr='iexact')
    text = filters.CharFilter(field_name='text', lookup_expr='icontains')
    country = filters.CharFilter(field_name='country', lookup_expr='iexact')
    polarity_gte = filters.NumberFilter(field_name='polarity', lookup_expr='gte')
    polarity_lte = filters.NumberFilter(field_name='polarity', lookup_expr='lte')
    date_gte = filters.DateFilter(field_name='stored_at', lookup_expr='gte')
    date_lte = filters.DateFilter(field_name='stored_at', lookup_expr='lte')

    class Meta:
        model = Tweet
        fields = ['keyword', 'text', 'country', 'polarity_gte', 'polarity_lte', 'date_gte', 'date_lte']

class TweetViewSet(viewsets.ModelViewSet):
    "API endpoint that allows users to be viewed or edited"
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    filterset_class = TweetFilter


class TweetAvg(APIView):
    serializer_class = TweetAvgSerializer
    def get(self, request):
        queryset = Tweet.objects.all()
        keyword = self.request.query_params.get('keyword', None)
        keyword = keyword.upper()
        keyword_exist = Keyword.objects.filter(keyword = keyword).exists()
        if keyword is not None and keyword_exist:
            avg = queryset.filter(keyword__keyword=keyword).aggregate(Avg('polarity'))
            filtered_tweets = queryset.filter(keyword__keyword=keyword)
            top10 = get_top_10_words(filtered_tweets)
        elif not keyword_exist:
            return Response("There is no such keyword.",status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Please include keyword",status=status.HTTP_400_BAD_REQUEST)
        return Response({'Average Polarity': avg['polarity__avg'], 'Top 10 Words':top10})

    def post(self, request, keyword=None):
        serializer = TweetAvgSerializer(data=request.data)
        if serializer.is_valid():
            post_keyword = serializer.data['keyword']
            avg = Tweet.objects.filter(keyword__keyword=post_keyword).aggregate(Avg('polarity'))
            filtered_tweets = Tweet.objects.filter(keyword__keyword=post_keyword)
            top10 = get_top_10_words(filtered_tweets)
            return Response({'Average Polarity': avg['polarity__avg'], 'Top 10 Words':top10})
        else:
            return Response({'Error'})
        
        
class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    
class JobView(APIView):

    serializer_class = JobSerializer

    def get(self, request, format=None):
        queryset = Job.objects.all()
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = JobSerializer(data=request.data)
        if request.user.is_authenticated:
            if serializer.is_valid():
                post_keyword = serializer.data['keyword']
                post_keyword = post_keyword.upper()
                post_start_date = serializer.data['start_date']
                post_end_date = serializer.data['end_date']
            if Keyword.objects.filter(keyword=post_keyword).exists():
                pass

            else:
                new_keyword = Keyword(keyword=post_keyword)
                new_keyword.save()
            key = Keyword.objects.filter(keyword=post_keyword)[0]
            job_user = request.user
            # job_user = job_form.cleaned_data['user']
            new_job = Job(keyword=key, start_date=post_start_date, end_date=post_end_date, user=job_user)
            new_job.save()

            #note that the time format should be MM/DD/YYYY
            job = JobStream(key,new_job)
            scheduler.add_job(job.start, trigger='date', run_date = post_start_date,id = new_job.keyword.keyword + "_start")
            scheduler.add_job(job.terminate, trigger='date', run_date = post_end_date, id = new_job.keyword.keyword + "_end")
            scheduler.print_jobs()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response('You are not authenticated',status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)