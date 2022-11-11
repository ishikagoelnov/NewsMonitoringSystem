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
    company_data = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, related_name='companyInfo')  # company delete subscriber delete
    client = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clientInfo')   # client delete subscriber delte


class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    subscribed_user = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='subUser')  # user delete - source delete
    sourced_client = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sourcingClient')  # remive null=true, but if we remove the clinet then source woukd be delete or not
    # referred_company = models.ManyToManyField(Company, related_name='refd_comp')

    class Meta:
        unique_together = ('url', 'sourced_client')

    def __str__(self):
        return self.name


class Story(models.Model):
    title = models.CharField(max_length=200)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='sourcedStory') # to be chnaged to set null
    pub_date = models.DateField()
    body_text = models.TextField()
    url = models.URLField(max_length=250)
    tagged_client = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tagClient') # to be reviewed (what happened if we remove the clieenet)
    tagged_company = models.ManyToManyField(Company, related_name='tagCompany')
    # login_user = models.ForeignKey(Subscriber, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('url', 'tagged_client')

    def __str__(self):
        return self.title
