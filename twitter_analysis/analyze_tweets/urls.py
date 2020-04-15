from django.urls import path, include
from . import views



urlpatterns = [
     path('', views.index, name='index'),
     path('tweet_analyzer/', views.tweet_analyzer, name = 'tweet_analyzer'),
     path('tweet_visualizer/', views.tweet_visualizer, name = 'tweet_visualizer'),
     path('tweet_visualizer/<word>', views.tweet_visualizer, name = 'tweet_visualizer'),
     path('tweet_list/', views.tweet_list, name = 'tweet_list'),
     path('tweet_list/<word>', views.tweet_list, name = 'tweet_list'),
     path('tweet_list/search', views.tweet_search, name="tweet_search"),
     path('keyword/', views.keyword_list, name="keyword_list"),
     path('keyword/search', views.keyword_search, name="keyword_search"),
     path('jobs/', views.JobListView.as_view(), name='jobs'),
     path('jobs/create/', views.createJob, name='create_job'),
     path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
     path('jobs/<int:pk>/update', views.updateJob , name='update_job'),
     path('jobs/<int:pk>/stop', views.terminateJob , name='terminate_job'),

]