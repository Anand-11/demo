from django.db import models
import datetime
#from django.contrib.admin.widgets import AdminDateWidget 
# Create your models here.
PROVIDER_NAME_CHOICES = (
    ('inneractive', 'inneractive'),
    ('InMobi', 'InMobi'),
    ('loopme', 'loopme'),
    ('yume', 'yume'),
    ('aerserv', 'aerserv'),
    ('Millennial media', 'Millennial media'),
    ('Q1media', 'Q1media'),
)

PROVIDER_TYPE_CHOICES = (
    ('banner', 'banner'),
    ('video', 'video'),
    ('interstitial', 'interstitial'),
)

COUNTRY_CHOICES = (
    ('IN', 'India'),
    ('US', 'US'),
    ('UK', 'UK'),
)

DEVICE_TYPE_CHOICES = (
    ('IOS','IOS'),
    ('ANDROID','ANDROID'),
)

class Entries(models.Model):
    country=models.CharField(max_length=30,null=False,blank=False,choices=COUNTRY_CHOICES)
    provider_name=models.CharField(max_length=100,null=False,blank=False,choices=PROVIDER_NAME_CHOICES)
    provider_type=models.CharField(max_length=100,null=False,blank=False,choices=PROVIDER_TYPE_CHOICES)
    impressions=models.IntegerField(default=0)
    revenue=models.IntegerField(default=0)
    ecpm=models.FloatField(default=0)
    entry_date = models.DateField(blank=False,null=False,default=datetime.date.today())

    class Meta:
        db_table='dashboard_entries'
        unique_together=('country','provider_name','provider_type','entry_date')


class GoogleAnalytics(models.Model):
    entry_date = models.DateField(blank=False,null=False,default=datetime.date.today())
    nos_of_devices = models.IntegerField(default=0)
    device =models.CharField(max_length=10,null=False,blank=False,choices=DEVICE_TYPE_CHOICES)

    class Meta:
        db_table="google_analytics"
        unique_together=('entry_date','nos_of_devices','device')


