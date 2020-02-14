#Standard Library imports
from collections import Counter
from datetime import datetime, date
import re

#Core Django imports
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect,HttpResponse
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

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
from analyze_tweets.forms import AddJobForm,UpdateJobForm
from .twitter_cred import consumer_key, consumer_secret, access_token, access_token_secret

#initialize scheduler 
scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': 24*60*60},)
scheduler.start()

#twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

@user_passes_test(lambda user: not user.username, login_url='index', redirect_field_name=None)
def register(request):
    if(request.method == 'POST'):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request,f'Account created for {username} !')
            return redirect('index')

    else:
        form = UserCreationForm()
    return render(request, 'analyze_tweets/register.html', {'form':form})
        
    
    
@login_required(login_url='login')
def index(request):
    # Generate counts of some of the main objects
    job_list = Job.objects.all().order_by('-last_modified')
    count_keywords = Keyword.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    
    context = {
        'job_list': job_list,
        'count_keywords': count_keywords,
        'num_visits': num_visits,
        'user':request.user
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class JobStream():
    def __init__(self, keyword, job):
        self.keyword = keyword
        self.job = job
        pk_id = Keyword.objects.get(keyword = self.keyword)
        keyword_id = pk_id.id
        self.myStreamListener = MyStreamListener(keyword_id)

    def start(self):
        self.myStream = tweepy.Stream(auth = api.auth, listener= self.myStreamListener)
        self.myStream.filter(track=[self.keyword], languages= ['en'], is_async=True)

    def terminate(self):
        self.myStream.disconnect()
        self.job.completion_status = True
        self.job.save()
        print("job ended!")

class MyStreamListener(tweepy.StreamListener):

    #overide Superclass __init__
    def __init__(self,keyword_id):
        super(MyStreamListener, self).__init__()
        self.keyword_id = keyword_id

    def on_status(self, status):
        #save tweets into Tweets database
        tweet_text = status.text
        tweet = Tweet(tweet_id = status.id, text = tweet_text.encode('ascii', 'ignore').decode('ascii'), keyword_id = self.keyword_id, country= status.user.location, stored_at= timezone.now())
        tweet.save()

    def on_error(self, status_code):
        if status_code == 420:
            return False



def tweet_analyzer():
    for tweet in Tweet.objects.filter(polarity__isnull=True):
        analyzed_tweet = TextBlob(tweet.text)
        tweet.polarity = analyzed_tweet.sentiment.polarity 
        tweet.save() 

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
    tweet_analyzer()
   
    if(word == None):
        num_comments = Tweet.objects.all().count()
        latest_comments = Tweet.objects.all().order_by('-stored_at')[:6]
        all_tweets = Tweet.objects.all()
        top_10_common = get_top_10_words(all_tweets)
        avg = Tweet.objects.filter(keyword__keyword=word).aggregate(Avg('polarity'))
        actual_avg = avg['polarity__avg']
        country_count = Tweet.objects.values('country').annotate(Count('id')).filter(id__count__gt=0)
        country_sentiment = Tweet.objects.values('country').annotate(Avg('polarity'))

    else:
        num_comments = Tweet.objects.filter(keyword__keyword=word).count()
        latest_comments = Tweet.objects.filter(keyword__keyword=word).order_by('-stored_at')[:6]
        all_tweets = Tweet.objects.filter(keyword__keyword=word)
        top_10_common = get_top_10_words(all_tweets)
        avg = Tweet.objects.filter(keyword__keyword=word).aggregate(Avg('polarity'))
        actual_avg = avg['polarity__avg']
        country_count = Tweet.objects.filter(keyword__keyword=word).values('country').annotate(Count('id')).filter(id__count__gt=0)
        country_sentiment = Tweet.objects.filter(keyword__keyword=word).values('country').annotate(Avg('polarity'))


    # Create array for number of tweets per country
    country_count = list(country_count.values_list('country', 'id__count'))
    country_count = [list(elem) for elem in country_count]
    country_count.insert(0, ['Country', 'Number of Tweets'])
    
    # Create array for sentiment by country
    country_sentiment = list(country_sentiment.values_list('country', 'polarity__avg'))
    country_sentiment = [list(elem) for elem in country_sentiment]
    country_sentiment = [[elem[0], float(elem[1])] for elem in country_sentiment]
    country_sentiment.insert(0, ['Country', 'Average Sentiment'])

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
    if len(the_sorted) > 0:
        list1, list2 = zip(*the_sorted)
        yearLabel = list(list1)
        yearData = list(list2)
    
    else:
        messages.error(request, "There are no tweets under the Keyword: {0}".format(word))
        return redirect('tweet_visualizer')
      
    context = {
        'num_comments' : num_comments,
        'latest_comments' : latest_comments,
        'sentiment_label' : sentiment_label,
        'yearLabel' : yearLabel,
        'yearData' : yearData,
        'keywords' : keywords,
        'top_10_common' : top_10_common,
        'actual_avg' : actual_avg,
        'country_count' : country_count,
        'country_sentiment' : country_sentiment,
    }
    return render(request, 'analyze_tweets/tweet_visualizer.html', context=context)

@login_required
def createJob(request):
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
            job_user = request.user
            # job_user = job_form.cleaned_data['user']
            new_job = Job(keyword=key, start_date=job_start_date, end_date=job_end_date, user=job_user)
            new_job.save()

            #note that the time format should be MM/DD/YYYY
            job = JobStream(job_keyword,new_job)
            scheduler.add_job(job.start, trigger='date', run_date = job_start_date,id = new_job.keyword.keyword + "_start")
            scheduler.add_job(job.terminate, trigger='date', run_date = job_end_date, id = new_job.keyword.keyword + "_end")
            scheduler.print_jobs()
            return HttpResponse("<h1>Job scheduled !</h1>")
            # Should not analyze tweets like this
            # return HttpResponseRedirect(reverse('tweet_analyzer'))
        else:
            print (job_form.errors)

    else:
        job_form = AddJobForm()
    return render(request, 'analyze_tweets/job_form.html', {'form': job_form})

def updateJob(request, pk= None):
    job = get_object_or_404(Job,id=pk)
    if request.user == job.user:
        if request.method == 'POST':
            job_form = UpdateJobForm(request.POST)
            if job_form.is_valid():

                # Can only reschedule start date if start date has not reached
                if timezone.now() < job.start_date :
                    # Have to check if updated date is valid, cannot be before time of request
                    job.start_date = job_form.cleaned_data['start_date']
                    job.save()
                    scheduler.reschedule_job(job.keyword.keyword+"_start",trigger='date',run_date=job.start_date)
                    # scheduler.print_jobs()
                else:
                    # Frontend have to check if date is valid
                    # cannot schedule start date of jobs that are already running
                    pass
                
                # Can only reschedule end date if end date has not reached
                if timezone.now() < job.end_date:
                    # Have to check if updated date is valid, cannot be before time of request
                    job.end_date = job_form.cleaned_data['end_date']
                    job.save()
                    scheduler.reschedule_job(job.keyword.keyword+"_end",trigger='date',run_date=job.end_date)
                    # scheduler.print_jobs()
                else:
                    # Frontend have to check if date is valid
                    # Cannot schedule end date of jobs that are already done
                    pass
                
                
                return HttpResponseRedirect(reverse('job_detail',kwargs={'pk':job.id}))
        else:
            data = {
                'start_date':job.start_date,
                'end_date':job.end_date,
            }
            job_form = UpdateJobForm(initial = data)
        return render(request, 'analyze_tweets/job_form.html', {'form': job_form,'job':job})

    else:
        return HttpResponse('Unauthorized', status=401)

def terminateJob(request, pk=None):
    job = get_object_or_404(Job,id=pk)
    if request.user == job.user:

        # Can only terminate an ongoing job, which means after start date and before end date
        if timezone.now() < job.end_date and timezone.now() > job.start_date:
            job.end_date = timezone.now()
            scheduler.reschedule_job(job.keyword.keyword+'_end',trigger='date')
            # scheduler.print_jobs(jobstore=None)
        else:
            #raise Error here
            pass
        
        return HttpResponseRedirect(reverse('job_detail',kwargs={'pk':job.id}))
    else:
        return HttpResponse('Unauthorized', status=401)




class JobListView(generic.ListView):
    model = Job
    # ordering = [-modified]

class JobDetailView(generic.DetailView):
    model = Job

