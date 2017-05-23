from django import forms
from django.forms.widgets import *
from yoolotto.lottery.models import LotteryGame
from yoolotto.lottery.models import LotteryGameComponent


CHOICES = (
	('------','------'),
	('Powerball','Powerball'),
	('MEGA Millions','MEGA Millions'),
	('Pick Three','Pick Three'),
	('All or Nothing','All or Nothing'),
	('Cash Five','Cash Five'),
	('Daily Four','Daily Four'),
	('Two Step','Two Step'),
	('Lotto Texas','Lotto Texas'),
	)

class AnalyticForm(forms.Form):
	game = forms.CharField(label="Game",
							max_length=80,
							widget =Select(choices=CHOICES),
							required=True,
							)
	date_from = forms.CharField(label="Date From",
		 					widget=TextInput(attrs={'placeholder': '2016-1-30'}))

	date_to = forms.CharField(label="Date To",
		 					widget=TextInput(attrs={'placeholder': '2016-1-31'}))

class UpdateCoinsForm(forms.Form):
	email = forms.CharField(label="Email",max_length=100,required=True,)
	coins = forms.FloatField(label="Coins",required=True,)

VIDEO_PROVIDER_CHOICES = (('inneractive','inneractive'),
	('aerserv','aerserv'),
	('yume','yume'),
	('loopme','loopme'),
	('InMobiInterstitial','InMobiInterstitial'),
	('AerservInterstitial','AerservInterstitial'),
	('InMobi','InMobi'),
	('Millennial media','Millennial media'),
	('aservBannerAd','aservBannerAd'),
	('MMBannerAd','MMBannerAd'),
	('AOLInterstitial','AOLInterstitial'),
	)

APP_VERSION_CHOICES = (
	('1.0','1.0'),
	('1.1','1.1'),
	('1.2','1.2'),
	('1.3','1.3'),
	('1.4','1.4'),
	('1.5','1.5'),
	)

DEVICE_CHOICES = (('ANDROID','ANDROID'),
	('IPHONE','IPHONE'))

isEnable_CHOICES = (('Active','Active'),
	('Inactive','Inactive'))

class VideoListForm(forms.Form):
	#video_provider = forms.ModelChoiceField(queryset=Tablename.objects.all(),max_length=100,required=True)
	video_provider = forms.CharField(label="app_version",max_length=80,widget =Select(choices=VIDEO_PROVIDER_CHOICES),required=True,)
	app_version = forms.CharField(label="app_version",max_length=80,widget =Select(choices=APP_VERSION_CHOICES),required=True,)
	device_type = forms.CharField(label="device_type",max_length=80,widget =Select(choices=DEVICE_CHOICES),required=True,)
	isEnable = forms.CharField(label="isEnable",max_length=80,widget =Select(choices=isEnable_CHOICES),required=True,)

PLC_CHOICES_provider = (('rewarded','rewarded'),
						('rewarded_2','rewarded_2'),
						('Yahoo_production','Yahoo_production'),
						('Vdopia_Production','Vdopia_Production'),
						('MM_Production','MM_Production'),
						('Tremor_Production','Tremor_Production'),
	
	)

class PLCListForm(forms.Form):
	#video_provider = forms.ModelChoiceField(queryset=Tablename.objects.all(),max_length=100,required=True)
	plc_provider = forms.CharField(label="App Provider",max_length=80,widget =Select(choices=PLC_CHOICES_provider),required=True,)
	app_version = forms.CharField(label="App Version",max_length=80,widget =Select(choices=APP_VERSION_CHOICES),required=True,)
	device_type = forms.CharField(label="Device Type",max_length=80,widget =Select(choices=DEVICE_CHOICES),required=True,)
	status = forms.CharField(label="Status",max_length=80,widget =Select(choices=isEnable_CHOICES),required=True,)
