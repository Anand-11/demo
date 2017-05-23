from django.conf.urls import patterns, include, url

from yoolotto.dashboard_app.views import *

urlpatterns = patterns('',
    url(r'^$',FillDetails.as_view()),
    url(r'^daily_report/$',DailyReport.as_view()),
    url(r'^monthly_report/$',MonthlyReport.as_view()),
    url(r'^googleform/$',GoogleAnalyticsDetail.as_view()),
    url(r'^test/$',Detail.as_view()),
    # url(r'^device_count/$',DeviceCount.as_view()),


   
)
