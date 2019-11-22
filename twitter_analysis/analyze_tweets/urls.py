from django.urls import path
from . import views

urlpatterns = [
     path('tweet_analyzer/', views.tweet_analyzer, name = 'tweet_analyzer'),
     path('tweet_visualizer/', views.tweet_visualizer, name = 'tweet_visualizer'),
     path('tweet_visualizer/<word>', views.tweet_visualizer, name = 'tweet_visualizer'),
]