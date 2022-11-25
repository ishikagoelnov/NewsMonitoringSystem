from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from .models import *
from django.views.decorators.csrf import csrf_exempt
import feedparser
from django.db import IntegrityError
from dateutil.parser import parse
from django.core.paginator import Paginator
from django.db.models import Q
from myNewsApp.utils import story_view,story_fetching,check_rss
from myNewsApp.serializers import Story_listing_Serializer, CompanySerializer
from rest_framework.decorators import api_view
from django.http import HttpResponse, JsonResponse

def index(request):
    return render(request, 'myNewsApp/index.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


@csrf_exempt
def login(request):
    """
    In this method we are trying to log in already created user
    using the username and password asked from user model of django
    """

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            try:
                auth.login(request, user)
                messages.info(request, "Logged in successfully!!")
                source=Source.objects.filter(
                    subscribed_user__user=user.id
                )
                if source:
                    return redirect('/stories_listing')
                else:
                    return render(request, 'myNewsApp/sourcing.html')  # redirect to story page
            except IndexError as e:
                messages.info(request, 'User not correctly signup!!')
                return redirect('/login')

        else:
            messages.info(request, 'Invalid Credentials')
            return render(request, 'myNewsApp/login.html')

    else:
        return render(request, 'myNewsApp/login.html')


def forget_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        newPassword = request.POST['newPassword']
        newPassword1 = request.POST['newPassword1']

        if newPassword == newPassword1:
            u = User.objects.get(username=username)
            u.set_password(newPassword)
            u.save()
            messages.info(request,"Password reset successfully")
            return render(request, 'myNewsApp/login.html')
        else:
            messages.info(request, "Password and Confirm password are not same")
            return render(request, 'myNewsApp/forget_password.html')
    else:
        return render(request, 'myNewsApp/forget_password.html')


def register(request):
    all_companies = Company.objects.all()
    if request.method == 'POST':
        # fetch all data from the form
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        company_data = request.POST.getlist('company')
        client_data = request.POST.getlist('client')

        if password1 == password2:

            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                messages.info(request, 'User already exists')
                return redirect('/register')
            else:
                client, company = client_data[0], company_data[0]  # get data from list of dropdown
                queryset =all_companies.filter(Q(company_name=company) | Q(company_name=client))  # get company and client in the form of list
                if(client==company):
                    registered_client=registered_company=queryset[0]
                else:
                    registered_company=queryset[0]
                    registered_client=queryset[1]

                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                password=password1, email=email)
                user.save()

                Subscriber.objects.create(user=user, company_data=registered_company, client=registered_client).save()
                messages.info(request,"Success!! registered successfully")
                return redirect('/login')
        else:
            print("Check your passwords !! Confirm password not matching to password")
            messages.info(request, 'Check your passwords !! Confirm password not matching to password')
            return redirect('/register')
    else:
        return render(request, 'myNewsApp/register.html', {'allcompanies': all_companies})



def sourcing(request):
    if request.method == 'POST':
        sourceName = request.POST['sourceName']
        sourceUrl = request.POST['sourceUrl']
        if check_rss(sourceUrl):
            try:
                subscriber_user = Subscriber.objects.select_related('client').filter(user=request.user.id)[0]
                requested_client = subscriber_user.client
                Source.objects.create(name=sourceName, url=sourceUrl, subscribed_user=subscriber_user,
                                      sourced_client=requested_client).save()
                messages.info(request,"Source added successfully")
                return redirect('/stories_listing')
            except IndexError:
                messages.info(request,'Something wrong with user account!! try with valid account')
                return redirect('/logout')
            except IntegrityError:
                messages.info(request, 'This source already exists try another one!!')
                return redirect('/sourcing')
        else:
            messages.info(request, 'Invalid rss feed !! Try to add correct rss ')
            return redirect('/sourcing')

    else:
        return render(request, 'myNewsApp/sourcing.html')


def source_listing(request):
    if request.user.is_staff:
        source = Source.objects.all()
    else:
        source=Source.objects.select_related('subscribed_user').filter(subscribed_user__user=request.user.id)

    if not source:
        return render(request, 'myNewsApp/sourcing.html')
    else:
        listing = {
            'source_lists': source,
            'source_count': len(source)
        }
        return render(request, 'myNewsApp/source_listing.html', listing)


def editing(request, pk):
    source_data = Source.objects.get(id=pk)
    if request.method == 'POST':
        updated_sourceName = request.POST['updsourceName']
        updated_sourceUrl = request.POST['updsourceUrl']

        if check_rss(updsourceUrl):
            source_data.name = updated_sourceName
            source_data.url = updated_sourceUrl
            source_data.save()
            messages.info(request,"Source edited successfully!!")
            return redirect('/source_listing')
        else:
            messages.info(request, 'Invalid rss feed !! Try to add correct rss ')
            return render(request, 'myNewsApp/editing.html', {'source_data': source_data})

    else:
        return render(request, 'myNewsApp/editing.html', {'source_data': source_data})


def sourceDelete(request, pk):
    if not request.user.is_staff:
        source=Source.objects.select_related('subscribed_user').filter(Q(subscribed_user__user=request.user.id),Q(id=pk))[0]
    else:
        source = Source.objects.select_related('subscribed_user').get(id=pk)

    if request.method == 'POST':
        source.delete()
        messages.info(request,"Source deleted successfully")
        if not source:
            return redirect('/sourcing')
        else:
            return redirect('/source_listing')
    else:
        messages.info(request,'Warning!! If source deleted then its stories will also be deleted ')
        return render(request, 'myNewsApp/sourceDelete.html', {'source_data': source})


def search_source(request):
    name = request.GET.get('search_name')
    if request.user.is_staff:
        source = Source.objects.filter(name__icontains=name)
    else:
        source = Source.objects.filter(name__icontains=name, subscribed_user__user=request.user.id)
    listing = {
        'source_lists': source,
        'source_count': len(source),
        'search_name':name
    }

    return render(request, 'myNewsApp/source_listing.html', listing)


def addstory(request):
    companies=Company.objects.all()
    sources=Source.objects.select_related('subscribed_user')
    if request.method == 'POST':

        title = request.POST['title']
        source1 = request.POST['source1']
        pub_date = request.POST['pub_date']
        body_text = request.POST['body_text']
        url1 = request.POST['url1']
        companies = request.POST.getlist('companies')

        preferred_source = sources.filter(name=source1)[0]
        preferred_client=Subscriber.objects.select_related('client').filter(user=request.user.id)[0].client
        if Story.objects.filter(url=url1).exists():
            messages.info(request,"This story already exists")
            return redirect('/addstory')
        else:
            newStory = Story.objects.create(title=title, source=preferred_source, pub_date=pub_date,
                                            body_text=body_text,
                                            url=url1,
                                            tagged_client=preferred_client)
            newStory.save()
            for company in companies:
                c1 = Company.objects.get(company_name=company)
                newStory.tagged_company.add(c1)
            messages.info(request,"Story added successfully")
            return redirect('/stories_listing')
    else:
        if not request.user.is_staff:
            sources = sources.filter(subscribed_user__user=request.user.id)

        context = {
            'allcompanies': companies,
            'sources': sources
        }
        return render(request, 'myNewsApp/addstory.html', context)


def storyDelete(request,pk):
    storyHere = Story.objects.get(id=pk)
    storyHere.delete()
    messages.info(request, "Story deleted successfully")
    return redirect('/stories_listing')


def editStories(request, pk):
    our_story = Story.objects.filter(id=pk)[0]
    if request.method == 'POST':
        updated_title = request.POST['title']
        updated_pub_date = request.POST['pub_date']
        updated_body_text = request.POST['body_text']
        updated_url = request.POST['url1']

        our_story.title = updated_title
        our_story.pub_date = parse(updated_pub_date)
        our_story.body_text = updated_body_text
        our_story.url = updated_url
        our_story.save()
        messages.info(request,"Story edited successfully")
        return redirect('/stories_listing')
    else:
        return render(request, 'myNewsApp/story_editing.html', {'story_data': our_story})


def search_story(request):
    name = request.GET.get('search_name')
    if request.user.is_staff:
        stories = Story.objects.select_related('source','tagged_client').prefetch_related('tagged_company').filter(title__icontains=name)
    else:
        client=Subscriber.objects.select_related('client').filter(user=request.user.id)[0].client
        stories = Story.objects.select_related('source','tagged_client').prefetch_related('tagged_company').filter(title__icontains=name, tagged_client=client)

    context = {
        'stories': stories,
        'storyCount': len(stories),
        'search_name': name
    }
    return render(request, 'myNewsApp/stories_listing.html', context)



def fetching(request, pk):
    source = Source.objects.select_related('sourced_client','subscribed_user').get(id=pk)
    subscriber = Subscriber.objects.select_related('client','company_data').get(user=request.user.id)
    if request.user.is_staff:
        stories = Story.objects.select_related('tagged_client','source').prefetch_related('tagged_company')
    else:
        stories = Story.objects.filter(tagged_client=subscriber.client).select_related('source','tagged_client').prefetch_related('tagged_company')

    story_fetching(source,subscriber,stories)
    messages.info(request,"Source fetched successfully")
    return redirect('/stories_listing')


@api_view(['GET'])
def stories_listing_api(request):
    is_staff = request.user.is_staff
    stories = Story.objects.select_related('tagged_client',
                                           'source').prefetch_related(
        'tagged_company')
    # if is_staff:
    #     stories = Story.objects.select_related('tagged_client','source').prefetch_related('tagged_company')
    # else:
    #     stories = Story.objects.filter(tagged_client=subcribed_client).select_related('source','tagged_client').prefetch_related('tagged_company')

    serialized_stories = Story_listing_Serializer(stories, many=True)
    return JsonResponse(serialized_stories.data, safe=False)


def stories_listing(request):
    is_staff = request.user.is_staff
    subscriber=Subscriber.objects.select_related('client','company_data').filter(user=request.user.id)[0]
    subcribed_client = subscriber.client
    if is_staff:
        stories = Story.objects.select_related('tagged_client','source').prefetch_related('tagged_company')

    else:
        stories = Story.objects.filter(tagged_client=subcribed_client).select_related('source','tagged_client').prefetch_related('tagged_company')

    if not stories:
        preferred_sources = Source.objects.filter(sourced_client=subcribed_client).select_related('sourced_client','subscribed_user')
        if not preferred_sources:
            return redirect('/sourcing')
        else:
            messages.info(request,"Fetch some source for stories")
            return redirect('/source_listing')

    context = {
        'stories': stories,
        'storyCount': len(stories)
    }
    # pagination
    p = Paginator(context['stories'], 5)
    page_number = request.GET.get('page')
    page_to_show = p.get_page(page_number)
    context['stories'] = page_to_show
    return render(request, 'myNewsApp/stories_listing.html', context)