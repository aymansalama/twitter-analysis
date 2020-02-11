from django.urls import path, include
from django.conf.urls import url

from rest_framework import routers

from analyze_api.views import KeywordViewSet, TweetViewSet, TweetAvg



keyword_list = KeywordViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

keyword_detail = KeywordViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

tweet_list = TweetViewSet.as_view({
    'get': 'list'
})

tweet_detail = TweetViewSet.as_view({
    'get': 'retrieve'
})


urlpatterns = [
    path('keyword/', keyword_list, name='keyword-list'),
    path('keyword/<int:pk>', keyword_detail, name='keyword-detail'),
    path('tweet/', tweet_list, name='tweet-list'),
    path('tweet/<int:pk>/', tweet_detail, name='tweet-detail'),
    path('tweet/avg/', TweetAvg.as_view(), name='tweet-avg'),
]
