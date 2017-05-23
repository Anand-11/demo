from django import forms
from yoolotto.dashboard_app.models import Entries,GoogleAnalytics

class EntriesForm(forms.ModelForm):
	class Meta:
		model=Entries
		exclude = ['ecpm']

class GoogleAnalyticsForm(forms.ModelForm):
	class Meta:
		model=GoogleAnalytics
		fields=['entry_date','nos_of_devices','device']