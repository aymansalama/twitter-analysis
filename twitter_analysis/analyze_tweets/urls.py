from django.urls import path, include
from . import views



urlpatterns = [
     path('', views.index, name='index'),
     path('keywords/', views.KeywordListView.as_view(), name='keywords'),
     path('keyword/<int:pk>', views.KeywordDetailView.as_view(), name='keyword_detail'),
     path('keyword/create/', views.KeywordCreate.as_view(), name='keyword_create'),
     path('keyword/<int:pk>/update/', views.KeywordUpdate.as_view(), name='keyword_update'),
     path('keyword/<int:pk>/delete/', views.KeywordDelete.as_view(), name='keyword_delete'),
     path('tweet_analyzer/', views.tweet_analyzer, name = 'tweet_analyzer'),
     path('tweet_visualizer/', views.tweet_visualizer, name = 'tweet_visualizer'),
     path('tweet_visualizer/<word>', views.tweet_visualizer, name = 'tweet_visualizer'),
     path('add_job/', views.addJob, name='add_job'),
     path('schedule_job/<keyword>', views.schedule_job, name='schedule_job'),
]