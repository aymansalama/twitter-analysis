#Stdlib imports

# Core Django imports
from django.db.models import Avg

# Third-party app imports
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import rest_framework as filters

# Imports from your apps
from analyze_tweets.models import Tweet, Keyword, Job
from analyze_tweets.views import get_top_10_words
from analyze_api.serializers import TweetSerializer, KeywordSerializer, TweetAvgSerializer

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
        if keyword is not None:
            avg = queryset.filter(keyword__keyword=keyword).aggregate(Avg('polarity'))
            filtered_tweets = queryset.filter(keyword__keyword=keyword)
            top10 = get_top_10_words(filtered_tweets)
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
    




