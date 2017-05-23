from django.contrib import admin
from yoolotto.dashboard_app.models import Entries,GoogleAnalytics

# Register your models here.
admin.site.register(Entries)
admin.site.register(GoogleAnalytics)