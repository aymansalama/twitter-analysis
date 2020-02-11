#Standard Library imports
from collections import Counter
from datetime import datetime, date
import re

#Core Django imports
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg

#Third-party app imports
import tweepy
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from chartjs.views.lines import BaseLineChartView
from apscheduler.schedulers.background import BackgroundScheduler

#Imports from local apps
from analyze_tweets.models import Tweet, Keyword, Job
from analyze_tweets.forms import AddJobForm
from .twitter_cred import consumer_key, consumer_secret, access_token, access_token_secret


#initialize scheduler 
scheduler = BackgroundScheduler()
scheduler.start()

#twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

class Job():
    def __init__(self, keyword_id, keyword):
        self.keyword = keyword
        self.myStreamListener = MyStreamListener(keyword_id)

    def test(self):
        self.myStream = tweepy.Stream(auth = api.auth, listener= self.myStreamListener)
        self.myStream.filter(track=[self.keyword], languages= ['en'], is_async=True)

    def terminate(self):
        self.myStream.disconnect()
        print("job ended!")

class MyStreamListener(tweepy.StreamListener):

    #overide Superclass __init__
    def __init__(self, keyword_id):
        super(MyStreamListener, self).__init__()
        self.keyword_id = keyword_id

    def on_status(self, status):
        #save tweets into Tweets database
        tweet = Tweet(tweet_id = status.id, text = status.text, keyword_id = self.keyword_id, stored_at= str(date.today()) )
        tweet.save()

    def on_error(self, status_code):
        if status_code == 420:
            return False

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

def get_top_10_words(all_tweets):
    this_list = []
    stop_words = set(stopwords.words('english'))
    stop_words.update(('https', 'rt', 'amp', "\'", "'s", '\"',)) 

    for e in all_tweets:
            this_list.append(e.text)

    all_comments = ' '.join(map(str, this_list)).lower()
    textb = TextBlob(all_comments)
    tokenized_text = textb.words
    filtered_sentence = [w for w in tokenized_text if not w in stop_words] 
    filtered_sentence = []

    for w in tokenized_text: 
        if w not in stop_words: 
            filtered_sentence.append(w)  

    fdist = FreqDist(filtered_sentence)
    top_10_common = fdist.most_common(10)
    return top_10_common


def tweet_visualizer(request, word = None):
    if(word == None):
        num_comments = Tweet.objects.all().count()
        latest_comments = Tweet.objects.all().order_by('-stored_at')[:6]
        all_tweets = Tweet.objects.all()
        top_10_common = get_top_10_words(all_tweets)
        avg = Tweet.objects.filter(keyword__keyword=word).aggregate(Avg('polarity'))
        actual_avg = avg['polarity__avg']

    else:
        num_comments = Tweet.objects.filter(keyword__keyword=word).count()
        latest_comments = Tweet.objects.filter(keyword__keyword=word).order_by('-stored_at')[:6]
        all_tweets = Tweet.objects.filter(keyword__keyword=word)
        top_10_common = get_top_10_words(all_tweets)
        avg = Tweet.objects.filter(keyword__keyword=word).aggregate(Avg('polarity'))
        actual_avg = avg['polarity__avg']

    keywords = Keyword.objects.all()
    pos = 0
    neg = 0 
    neu = 0

    #Plotting the graphs
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
        'top_10_common' : top_10_common,
        'actual_avg' : actual_avg,
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

def schedule_job(request, keyword):
    
    #the keyword_id needs to connect here to store inside Tweet table
    job = Job(1, keyword) 

    #start_date will need to pass here in the future
    scheduler.add_job(job.test)

    #currently using datetime for testing
    scheduler.add_job(job.terminate, run_date = datetime(2020, 2, 4, 15, 35, 00))
    scheduler.print_jobs(jobstore=None)

    return render(request, 'analyze_tweets/schedule_info.html')

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
