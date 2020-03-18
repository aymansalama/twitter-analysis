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
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator

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
      
def landing_page(request):
    return render(request, 'analyze_tweets/landing_page.html')

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
        self.myStreamListener = MyStreamListener(keyword.id)

    def start(self):
        self.job.job_status = Job.Running
        self.job.save()
        self.myStream = tweepy.Stream(auth = api.auth, listener= self.myStreamListener)
        self.myStream.filter(track=[self.keyword.keyword], languages= ['en'], is_async=True)

    def terminate(self):
        self.myStream.disconnect()
        self.job.job_status = Job.Completed
        self.job.end_date = timezone.now()
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
        if (tweet_text.startswith('RT')):
            x= tweet_text.split()
            remove = x[0] + x[1]
            tweet_text = tweet_text[len(remove)+2:]
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

def get_top_10_words(all_tweets, word):
    this_list = []
    stop_words = set(stopwords.words('english'))
    stop_words.update(('https', 'rt', 'amp', "\'", "'s", '\"')) 

    if word != None:
        stop_words.update((word.lower(),word)) 


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

def keyword_list(request):
    all_keyword = Keyword.objects.all()
    keywords = []
    polarities = []
    for keyword in all_keyword:
        keyword_count = Tweet.objects.filter(keyword__keyword=keyword).count()
        avg = Tweet.objects.filter(keyword__keyword=keyword).aggregate(Avg('polarity')) 
        keyword.avg_polarity = avg['polarity__avg']
        keyword.tweet_count = keyword_count
        keywords.append(keyword.keyword)
        if avg['polarity__avg']:
            polarities.append(float(avg['polarity__avg']))
        else:
            polarities.append(0)
        keyword.save()

    context = {
        'all_keyword': all_keyword,
        'keywords': keywords,
        'polarities': polarities
    }
    return render(request, 'analyze_tweets/keyword_list.html', context=context)



def keyword_search(request):
    keywords = []
    polarities = []
    query = request.GET.get('q','')
    if query:
            queryset = (Q(keyword__icontains=query))
            results = Keyword.objects.filter(queryset).distinct()
    else:
       results = []

    for keyword in Keyword.objects.all():
        keywords.append(keyword.keyword)
        if keyword.avg_polarity:
            polarities.append(float(keyword.avg_polarity))
        else:
            polarities.append(0)
            
    context = {
        'results':results, 
        'query':query,
        'keywords': keywords,
        'polarities': polarities
        }
    return render(request, 'analyze_tweets/keyword_list.html', context=context)


def tweet_visualizer(request, word = None):
    tweet_analyzer()
 
    num_comments = Tweet.objects.filter(keyword__keyword=word).count()
    all_comments = Tweet.objects.filter(keyword__keyword=word).order_by('-stored_at')
    all_tweets = Tweet.objects.filter(keyword__keyword=word)
    top_10_common = get_top_10_words(all_tweets, word)
    country_count = Tweet.objects.filter(keyword__keyword=word).values('country').annotate(Count('id')).filter(id__count__gt=0)
    country_sentiment = Tweet.objects.filter(keyword__keyword=word).values('country').annotate(Avg('polarity'))

    pos = Tweet.objects.filter(keyword__keyword = word, polarity__gte=0.5).values('polarity').count()
    neg = Tweet.objects.filter(keyword__keyword = word, polarity__lte=-0.5).values('polarity').count()
    neu = Tweet.objects.filter(keyword__keyword = word, polarity__gt=-0.5, polarity__lt=0.5).values('polarity').count()

    yearDict = Tweet.objects.filter(keyword__keyword = word).values('stored_at__year').annotate(Count('id'))
    

    # Create array for number of tweets per country
    country_count = list(country_count.values_list('country', 'id__count'))
    country_count = [list(elem) for elem in country_count if elem[0] != None]
    country_count.insert(0, ['Country', 'Number of Tweets'])
    
    # Create array for sentiment by country
    country_sentiment = list(country_sentiment.values_list('country', 'polarity__avg'))
    country_sentiment = [list(elem) for elem in country_sentiment]
    country_sentiment = [[elem[0], float(elem[1])] for elem in country_sentiment if elem[0] != None]
    country_sentiment.insert(0, ['Country', 'Average Sentiment'])

    # Convert year QuerySet into dictionary
    yearDict = list(yearDict.values_list('stored_at__year', 'id__count'))
    yearDict = Counter(dict([list([str(elem[0]), elem[1]]) for elem in yearDict]))
    
    # Data to plot
    # labels = 'Positive', 'Negative', 'Neutral'
    sentiment_label = [pos, neg, neu]
    the_sorted = sorted(yearDict.items())
    if len(the_sorted) > 0:
        list1, list2 = zip(*the_sorted)
        yearLabel = list(list1)
        yearData = list(list2)

        # Create data array for Top 10 Words
        listA, listB = zip(*top_10_common)
        word_list = list(listA)
        word_count = list(listB)
    
    else:
        messages.error(request, "There are no tweets under the Keyword: {0}".format(word))
        return redirect('keyword_list')
    
    tweet_paginate = Paginator(all_comments, 15)
    tweet_number = request.GET.get('page')
    tweet_obj = tweet_paginate.get_page(tweet_number)
      
    context = {
        'num_comments' : num_comments,
        'all_comments' : all_comments,
        'sentiment_label' : sentiment_label,
        'yearLabel' : yearLabel,
        'yearData' : yearData,
        'country_count' : country_count,
        'country_sentiment' : country_sentiment,
        'word_list': word_list,
        'word_count': word_count,
        'word' : word,
        'tweet_obj' : tweet_obj
    }
    return render(request, 'analyze_tweets/tweet_visualizer.html', context=context)

# def checkScheduler(request):
#     jobs = scheduler.get_jobs()
#     scheduler.print_jobs()
#     return HttpResponse(jobs)

def initScheduler(): 
    #check job status of all jobs and reschedule
    for unfinished_job in Job.objects.filter(job_status = Job.Running):
        #case 1: the job end_date already passed
        #solution: update the job as completed
        if unfinished_job.end_date <= timezone.now():
            unfinished_job.job_status = Job.Completed
            unfinished_job.save()
            print("Time passed")
        
        #case 2: the job suppose to be still running
        #solution: run the job immediately
        else:
            keyword = Keyword.objects.get(id = unfinished_job.keyword_id)
            job = JobStream(keyword,unfinished_job)
            scheduler.add_job(job.start, trigger='date', run_date = timezone.now(), id = unfinished_job.keyword.keyword + "_start")
            scheduler.add_job(job.terminate, trigger='date', run_date = unfinished_job.end_date, id = unfinished_job.keyword.keyword + "_end")
   
    for unfinished_job in Job.objects.filter(job_status = Job.Pending):
        #there are 3 scenarios of pending job

        #case 1: the job start_date has already passed, but the end_date is not
        #solution: run job immediately
        if unfinished_job.start_date <= timezone.now():
            
            #case 2: the job start_date and end_date both passed
            #solution: update the job as completed
            if unfinished_job.end_date <= timezone.now():
                unfinished_job.job_status = Job.Completed
                unfinished_job.save()
                print("Time passed")
                continue

            unfinished_job.job_status = Job.Running
            unfinished_job.save()
            keyword = Keyword.objects.get(id = unfinished_job.keyword_id)
            job = JobStream(keyword,unfinished_job)
            scheduler.add_job(job.start, trigger='date', run_date = timezone.now(), id = unfinished_job.keyword.keyword + "_start")
            scheduler.add_job(job.terminate, trigger='date', run_date = unfinished_job.end_date, id = unfinished_job.keyword.keyword + "_end")
            
        #case 3: the job has not started (starting in the future)
        #solution: schedule the job as usual
        else:
            keyword = Keyword.objects.get(id = unfinished_job.keyword_id)
            job = JobStream(keyword,unfinished_job)
            scheduler.add_job(job.start, trigger='date', run_date = unfinished_job.start_date, id = unfinished_job.keyword.keyword + "_start")
            scheduler.add_job(job.terminate, trigger='date', run_date = unfinished_job.end_date, id = unfinished_job.keyword.keyword + "_end")
    
    scheduler.add_job(tweet_analyzer,'interval', minutes=15)
    scheduler.print_jobs()

initScheduler()

@login_required
def createJob(request):
    if request.method == 'POST':
        job_form = AddJobForm(request.POST)
        
        if job_form.is_valid():
            job_keyword = job_form.cleaned_data['keyword']
            job_keyword = job_keyword.upper()
            
            if Keyword.objects.filter(keyword=job_keyword).exists():
                #check previous job_status for that keyword
                prev_keyword_id = Keyword.objects.get(keyword= job_keyword)

                for prev_job in Job.objects.filter(keyword_id = prev_keyword_id):
                    if (prev_job.job_status == Job.Pending or prev_job.job_status == Job.Running):
                        #if there is an existing job pending or running
                         return render(request, 'analyze_tweets/job_form.html', {'form': job_form,'message' : 'Job already exist. Please update job instead.'})
                
                new_keyword = prev_keyword_id

            else:
                new_keyword = Keyword(keyword=job_keyword)
                new_keyword.save()

            key = Keyword.objects.filter(keyword=job_keyword)[0]
            job_start_date = job_form.cleaned_data['start_date']
            job_end_date = job_form.cleaned_data['end_date']
            job_user = request.user
            # job_user = job_form.cleaned_data['user']
            
            #time validation
            if job_end_date <= job_start_date:
                return render(request, 'analyze_tweets/job_form.html', {'form': job_form,'message' : 'Invalid Time.'})

            new_job = Job(keyword=key, start_date=job_start_date, end_date=job_end_date, user=job_user)
            new_job.save()

            job = JobStream(key,new_job)
            scheduler.add_job(job.start, trigger='date', run_date = job_start_date,id = new_job.keyword.keyword + "_start")
            scheduler.add_job(job.terminate, trigger='date', run_date = job_end_date, id = new_job.keyword.keyword + "_end")
            scheduler.print_jobs()
            return render(request, 'analyze_tweets/job_form.html', {'form': job_form, 'message' : 'Your job has been scheduled.'})

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
            scheduler.reschedule_job(job.keyword.keyword+'_end',trigger='date')
            # scheduler.print_jobs(jobstore=None)

        elif timezone.now() < job.start_date:
            scheduler.remove_job(job.keyword.keyword+'_start')
            scheduler.remove_job(job.keyword.keyword+'_end')
            job.start_date = timezone.now()
            job.end_date = timezone.now()
            job.job_status = Job.Completed
            job.save()
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



