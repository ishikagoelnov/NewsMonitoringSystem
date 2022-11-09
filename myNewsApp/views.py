from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from .models import *
from django.views.decorators.csrf import csrf_exempt
import feedparser
from django.db import IntegrityError
from dateutil.parser import parse


def index(request):
    return render(request, 'myNewsApp/index.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']

        # fetch the user with this credentials
        user = auth.authenticate(username=username, password=password1)
        if user is not None:
            auth.login(request, user)
            sb = Subscriber.objects.get(user=user.id)
            if Source.objects.filter(subscribed_user=sb).exists():
                return redirect('/stories_listing')
            else:
                return render(request, 'myNewsApp/sourcing.html')  # redirect to story page

        else:
            messages.info(request, 'Invalid Credentials')
            return render(request, 'myNewsApp/login.html')

    else:
        return render(request, 'myNewsApp/login.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        # company1 = request.POST['company1']
        # client1 = request.POST['client1']
        company1 = request.POST.getlist('company')
        client1 = request.POST.getlist('client')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken')
                return redirect('/register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Account with this email already exists')
                return redirect('/register')
            else:
                cl = client1[0]
                comp = company1[0]
                company_reg = Company.objects.get(company_name=comp)
                client_reg = Company.objects.get(company_name=cl)
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                password=password1, email=email)
                user.save()

                subscribedUser = Subscriber.objects.create(user=user, company_data=company_reg, client=client_reg)
                subscribedUser.save()
                return redirect('/login')
        else:
            print("Check your passwords !! Confirm password not matching to password")
            messages.info(request, 'Check your passwords !! Confirm password not matching to password')
            return redirect('/register')
    else:
        companyAll = Company.objects.all()
        return render(request, 'myNewsApp/register.html', {'allcompanies': companyAll})


def sourcing(request):
    if request.method == 'POST':
        sourceName = request.POST['sourceName']
        sourceUrl = request.POST['sourceUrl']
        user_here = request.user.id
        sb = Subscriber.objects.get(user=user_here)
        cl = sb.client
        sourcing_obj = Source.objects.create(name=sourceName, url=sourceUrl, subscribed_user=sb, sourced_client=cl)
        sourcing_obj.save()
        print(sourcing_obj)
        return redirect('/stories_listing')
    else:
        return render(request, 'myNewsApp/sourcing.html')


def source_listing(request):
    user = request.user.id
    if request.user.is_staff:
        source = Source.objects.all()
    else:
        sb = Subscriber.objects.get(user=user)
        source = Source.objects.filter(subscribed_user=sb)
    source_count = source.count()
    print(source_count)
    print(source)
    listing = {
        'source_lists': source,
        'source_count': source_count
    }
    return render(request, 'myNewsApp/source_listing.html', listing)


def stories_listing(request):
    user = request.user.id
    sb = Subscriber.objects.get(user=user)
    clientHere = sb.client
    preferred_sources = Source.objects.filter(sourced_client=clientHere)
    print(preferred_sources)

    count = preferred_sources.count()
    allEntries = []
    storyCount = 0
    for i in range(count):
        source_url = preferred_sources[i].url
        NewsFeed = feedparser.parse(source_url)
        allEntries1 = NewsFeed.entries
        for entry in allEntries1:
            storyCount += 1
            title = entry.title
            desc = entry.summary
            updesc = ""  # here updated description
            if '<' in desc:
                ed = desc.rfind('>')
                updesc += desc[ed + 1:]
            else:
                updesc += desc
            sourceHere = Source.objects.get(url=source_url)
            pub_date1 = entry.published
            pub_date = parse(pub_date1)
            url = entry.link
            clientHere = sourceHere.sourced_client
            userHere = sourceHere.subscribed_user
            companyHere = userHere.company_data
            if Story.objects.filter(title=title).exists():
                pass
            else:
                try:
                    story_obj = Story.objects.create(title=title, source=sourceHere, pub_date=pub_date,
                                                     body_text=updesc,
                                                     url=url, tagged_client=clientHere)
                    story_obj.save()
                    story_obj.tagged_company.add(companyHere)

                except IntegrityError as e:
                    continue

    if request.user.is_staff:
        stories = Story.objects.all()
        c = stories.count()
    else:
        user = request.user.id
        sb = Subscriber.objects.get(user=user)
        preferred_client = sb.client
        stories = Story.objects.filter(tagged_client=preferred_client)
        print("kaisa hai")

    context = {
        'stories': stories,
        'storyCount': storyCount
    }
    return render(request, 'myNewsApp/stories_listing.html', context)


def editing(request, pk):
    if request.method == 'POST':
        updsourceName = request.POST['updsourceName']
        updsourceUrl = request.POST['updsourceUrl']
        ourSource = Source.objects.get(id=pk)
        ourSource.name = updsourceName
        ourSource.url = updsourceUrl
        ourSource.save()
        return redirect('/source_listing')

    else:
        source_data = Source.objects.get(id=pk)
        return render(request, 'myNewsApp/editing.html', {'source_data': source_data})


def sourceDelete(request, pk):
    if request.method == 'POST':
        password1 = request.POST['password1']
        username1 = request.user.username
        user = auth.authenticate(username=username1, password=password1)
        if user is not None:
            source_data = Source.objects.get(id=pk)
            source_data.delete()
            return redirect('/source_listing')
        else:
            # print("wrong password")
            source_data = Source.objects.get(id=pk)
            messages.info(request, 'Check your passwords !! Enter correct password for delete')
            return render(request, 'myNewsApp/sourceDelete.html', {'source_data': source_data})
            # return redirect('/NewsApp/sourceDelete')
    else:
        source_data = Source.objects.get(id=pk)
        return render(request, 'myNewsApp/sourceDelete.html', {'source_data': source_data})


def search_source(request):
    name1 = request.GET.get('search_name')
    user = request.user.id
    if request.user.is_staff:
        s1 = Source.objects.filter(name__icontains=name1)
    else:
        sb = Subscriber.objects.get(user=user)
        s1 = Source.objects.filter(name__icontains=name1, subscribed_user=sb)
    source_count = s1.count()
    listing = {
        'source_lists': s1,
        'source_count': source_count
    }
    return render(request, 'myNewsApp/source_listing.html', listing)


def addstory(request):
    if request.method == 'POST':
        title = request.POST['title']
        source1 = request.POST['source1']
        pub_date = request.POST['pub_date']
        body_text = request.POST['body_text']
        url1 = request.POST['url1']
        companies = request.POST.getlist('companies')

        user = request.user.id
        sb = Subscriber.objects.get(user=user)
        preferred_source = Source.objects.get(name=source1)
        preferred_client = sb.client
        newStory = Story.objects.create(title=title, source=preferred_source, pub_date=pub_date, body_text=body_text,
                                        url=url1,
                                        tagged_client=preferred_client)
        newStory.save()
        for company in companies:
            print(company)
            c1 = Company.objects.get(company_name=company)
            newStory.tagged_company.add(c1)
        return redirect('/stories_listing')
    else:
        company1 = Company.objects.all()
        user = request.user.id
        sb = Subscriber.objects.get(user=user)
        sources = Source.objects.filter(subscribed_user=sb)
        context = {
            'allcompanies': company1,
            'sources': sources
        }
        return render(request, 'myNewsApp/addstory.html', context)


def storyDelete(request, pk):
    storyHere = Story.objects.get(id=pk)
    storyHere.delete()
    return redirect('/stories_listing')


def editStories(request, pk):
    if request.method == 'POST':
        uptitle = request.POST['title']
        uppub_date = request.POST['pub_date']
        upbody_text = request.POST['body_text']
        upurl1 = request.POST['url1']

        ourStory = Story.objects.get(id=pk)
        ourStory.title = uptitle
        uppub_date1 = parse(uppub_date)
        ourStory.pub_date = uppub_date1
        ourStory.body_text = upbody_text
        ourStory.url = upurl1
        ourStory.save()
        return redirect('/stories_listing')
    else:
        story_data = Story.objects.get(id=pk)
        return render(request, 'myNewsApp/story_editing.html', {'story_data': story_data})


def search_story(request):
    name1 = request.GET.get('search_name')
    user = request.user.id
    if request.user.is_staff:
        s1 = Story.objects.filter(title__icontains=name1)
    else:
        sb = Subscriber.objects.get(user=user)
        client = sb.client
        s1 = Story.objects.filter(title__icontains=name1, tagged_client=client)
    story_count = s1.count()
    listing = {
        'stories': s1,
        'storyCount': story_count
    }
    return render(request, 'myNewsApp/stories_listing.html', listing)
