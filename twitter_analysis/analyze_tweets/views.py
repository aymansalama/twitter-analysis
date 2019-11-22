from django.shortcuts import render
from analyze_tweets.models import Tweet, Keyword
from textblob import TextBlob
from collections import Counter
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .twitter_cred import consumer_key, consumer_secret, access_token, access_token_secret
import tweepy

#twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Create your views here.

def tweet_analyzer(request):
    for tweet in Tweet.objects.filter(polarity__isnull=True):
        analyzed_tweet = TextBlob(tweet.text)
        tweet.polarity = analyzed_tweet.sentiment.polarity 
        tweet.save() 


    return render(request, 'analyze_tweets/tweet_analyzed.html')

def tweet_visualizer(request, word = None):
    if(word == None):
        num_comments = Tweet.objects.all().count()
        latest_comments = Tweet.objects.all().order_by('-stored_at')[:6]
        all_tweets = Tweet.objects.all()
    else:
        num_comments = Tweet.objects.filter(keyword__keyword=word).count()
        latest_comments = Tweet.objects.filter(keyword__keyword=word).order_by('-stored_at')[:6]
        all_tweets = Tweet.objects.filter(keyword__keyword=word)

    keywords = Keyword.objects.all()
    pos = 0
    neg = 0 
    neu = 0

    yearDict = Counter()
    for tweet in all_tweets:
        year = tweet.yearpublished()
        yearDict[year] += 1

        if tweet.polarity >= 0.5:
            pos += 1

        elif tweet.polarity <= -0.5:
            neg += 1

        else:
            neu += 1
    
    # Data to plot
    # labels = 'Positive', 'Negative', 'Neutral'
    sentiment_label = [pos, neg, neu]
    
    the_sorted = sorted(yearDict.items())
    list1, list2 = zip(*the_sorted)
    yearLabel = list(list1)
    yearData = list(list2)
      

    context = {
        'num_comments' : num_comments,
        'latest_comments' : latest_comments,
        'sentiment_label' : sentiment_label,
        'yearLabel' : yearLabel,
        'yearData' : yearData,
        'keywords' : keywords,
    }
    return render(request, 'analyze_tweets/tweet_visualizer.html', context=context)