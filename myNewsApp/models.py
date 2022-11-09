from django.db import models
from django.contrib.auth import get_user_model
from django.forms import forms

User = get_user_model()


class Company(models.Model):
    company_name = models.CharField(max_length=200, blank=True)
    website = models.URLField(max_length=200, blank=True)
    company_address = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.company_name


class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_data = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='companyInfo')
    client = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clientInfo')


class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    subscribed_user = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    sourced_client = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    # referred_company = models.ManyToManyField(Company, related_name='refd_comp')

    class Meta:
        unique_together = ('url', 'sourced_client')

    def __str__(self):
        return self.name


class Story(models.Model):
    title = models.CharField(max_length=200)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    pub_date = models.DateField()
    body_text = models.TextField()
    url = models.URLField(max_length=250)
    tagged_client = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    tagged_company = models.ManyToManyField(Company, related_name='tag_comp')
    # login_user = models.ForeignKey(Subscriber, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('url', 'tagged_client')

    def __str__(self):
        return self.title
