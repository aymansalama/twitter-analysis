from django.shortcuts import render, get_object_or_404
from analyze_tweets.models import Tweet, Keyword, Job
from analyze_tweets.forms import AddJobForm
from textblob import TextBlob
from collections import Counter
from django.views import generic
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from chartjs.views.lines import BaseLineChartView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .twitter_cred import consumer_key, consumer_secret, access_token, access_token_secret
import tweepy

#twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Create your views here.

def index(request):
    # Generate counts of some of the main objects
    num_keywords = Keyword.objects.all()
    count_keywords = Keyword.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'num_keywords': num_keywords,
        'count_keywords': count_keywords,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

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


def addJob(request):
    if request.method == 'POST':
        job_form = AddJobForm(request.POST)
        
        if job_form.is_valid():
            job_keyword = job_form.cleaned_data['keyword']
            
            
            if Keyword.objects.filter(keyword=job_keyword).exists():
                pass

            else:
                new_keyword = Keyword(keyword=job_keyword)
                new_keyword.save()

            key = Keyword.objects.filter(keyword=job_keyword)[0]
            job_start_date = job_form.cleaned_data['start_date']
            job_end_date = job_form.cleaned_data['end_date']
            job_user_id = job_form.cleaned_data['user']
            new_job = Job(keyword=key, start_date=job_start_date, end_date=job_end_date, user_id=job_user_id)
            new_job.save()
            return HttpResponseRedirect(reverse('tweet_visualizer'))
        else:
            print (job_form.errors)

    else:
        job_form = AddJobForm()
    return render(request, 'analyze_tweets/job_add.html', {'job_form': job_form})


# These class based views should be changed
class KeywordListView(generic.ListView):
    model = Keyword

class KeywordDetailView(generic.DetailView):
    model = Keyword
    paginate_by = 20

class KeywordCreate(CreateView):
    model = Keyword
    fields = '__all__'

class KeywordUpdate(UpdateView):
    model = Keyword
    fields = ['keyword','start_date', 'until_date']

class KeywordDelete(DeleteView):
    model = Keyword
    success_url = reverse_lazy('keywords')

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            url = self.get_success_url()
            return HttpResponseRedirect(url)
        else:
            return super(KeywordDelete, self).post(request, *args, **kwargs)
