from django.shortcuts import render,render_to_response,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from yoolotto.rest.decorators import rest, Authenticate
from django.db.models import Sum,Count
from django.http import HttpResponse, HttpResponseNotFound,HttpResponseRedirect
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import json
from datetime import datetime
import datetime
from yoolotto.dashboard_app.forms import EntriesForm,GoogleAnalyticsForm
from yoolotto.dashboard_app.models import Entries,GoogleAnalytics
import math
import csv
import glob
import MySQLdb
connection =MySQLdb.connect(host='127.0.0.1',port=3306,user='root',passwd='root',db='yoo_lat')

# Create your views here.
#### Total devices (ios and android) from GoogleAnalytics via form we have created
#### New devices via queries
### Old devices=total - new

# def calculate_no_of_android_devices(date):
# 	cursor1=connection.cursor()
# 	cursor2=connection.cursor()
# 	total_android="select nos_of_devices from google_analytics where device='ANDROID' and date(entry_date)='2017-05-11';".format(date)
# 	new_android="select count(*) from user_coins_earn_history where source='new_user' and device_type='ANDROID' and date(added_at)='{0}';".format(date)
# 	cursor1.execute(total_android)
# 	cursor2.execute(new_android)
# 	for data in cursor1.fetchall():
# 	    total_android_devices=int(data[0])
# 	    print "total_android_devices",int(total_android_devices)
# 	total_new_android_devices=int(cursor2.fetchone()[0])
# 	print "total_new_android_devices",int(total_new_android_devices)
# 	total_existing_android_devices=int(total_android_devices)-int(total_new_android_devices)
# 	return ({"total_android_devices":total_android_devices,"total_new_android_devices":total_new_android_devices,"total_existing_android_devices":total_existing_android_devices})

# print (calculate_no_of_android_devices('2016-12-06'))
	




# def calculate_no_of_ios_devices(date):
# 	cursor1=connection.cursor()
# 	cursor2=connection.cursor()
# 	total_ios_device="select nos_of_devices from google_analytics where device='IOS' and date(entry_date)='2017-05-11';".format(date)
# 	new_ios="select count(*) from user_coins_earn_history where source='new_user' and device_type='IPHONE' and date(added_at)='{0}';".format(date)
# 	cursor1.execute(total_ios_device)
# 	cursor2.execute(new_ios)
# 	for data in cursor1.fetchall():
# 	    print int (data[0])
#         total_ios=int(data[0])
            
# 	total_new_ios=int(cursor2.fetchone()[0])
#     	print int(total_new_ios)
         
	
# 	total_existing_ios_devices=int(total_ios)-int(total_new_ios)

# 	return({"total_ios":total_ios,"total_new_ios":total_new_ios,"total_existing_ios_devices":total_existing_ios_devices})


# print(calculate_no_of_ios_devices('2016-12-02'))



# def user_activity(date):
# 	cursor1=connection.cursor()
# 	cursor2=connection.cursor()
# 	cursor3=connection.cursor()
# 	total_usr="select sum(h.credit_coins) as total_coins from user_history h inner join user u on h.user_id=u.id where date(h.added_at)='{0}' group by h.user_id having total_coins >=0  order by sum(h.credit_coins) ;".format(date)
# 	usr_ernd_Zero_yoobx="select sum(h.credit_coins) as total_coins from user_history h inner join user u on h.user_id=u.id where date(h.added_at)='{0}' group by h.user_id having total_coins =0  order by sum(h.credit_coins) ;".format(date)
# 	watched_videos="select count(distinct(user_id)) as total_users from user_history where source_id in (14) and date(added_at)='{0}';".format(date)
# 	total_user=int(cursor1.execute(total_usr))
#         print "total_user",total_user
# 	user_ernd_Zero_yoobx=int(cursor2.execute(usr_ernd_Zero_yoobx))
#         print "user_ernd_Zero_yoobx",user_ernd_Zero_yoobx
# 	usr_did_activity=total_user-user_ernd_Zero_yoobx
# 	print "usr_did_activity",usr_did_activity
# 	cursor3.execute(watched_videos)
# 	usr_watched_videos=int(cursor3.fetchone()[0])
# 	print"usr_watched_videos",usr_watched_videos
# 	return({"total_user":total_user,"user_ernd_Zero_yoobx":user_ernd_Zero_yoobx,"usr_did_activity":usr_did_activity,"usr_watched_videos":usr_watched_videos})

        
# print(user_activity('2016-02-26'))
	

# def avg_of_device_per_user(date):
# 	cursor1=connection.cursor()
# 	cursor2=connection.cursor()
# 	cursor3=connection.cursor()
# 	cursor4=connection.cursor()
# 	cursor5=connection.cursor()
# 	cursor6=connection.cursor()
# 	total_ios_device="select nos_of_devices from google_analytics where device='IOS' and date(entry_date)='2017-05-11';".format(date)
# 	total_android="select nos_of_devices from google_analytics where device='ANDROID' and date(entry_date)='2017-05-11';".format(date)
# 	usr_ernd_one_or_more_yoobx="select sum(h.credit_coins) as total_coins from user_history h inner join user u on h.user_id=u.id where date(h.added_at)='{0}' group by h.user_id having total_coins >= 1  order by sum(h.credit_coins) ;".format(date)
# 	watched_videos="select count(distinct(user_id)) as total_users from user_history where source_id in (14) and date(added_at)='{0}';".format(date)
# 	ios_usr_in_hun_clb ="select sum(h.credit_coins) as total_coins from user_history h inner join user u on h.user_id=u.id where date(h.added_at)='{0}'and device_type='IPHONE' group by h.user_id having total_coins >=10 order by sum(h.credit_coins) ;".format(date)
# 	android_usr_in_hun_clb="select sum(h.credit_coins) as total_coins from user_history h inner join user u on h.user_id=u.id where date(h.added_at)='{0}'and device_type='ANDROID' group by h.user_id having total_coins >=10 order by sum(h.credit_coins) ;".format(date)
# 	cursor1.execute(total_ios_device)
# 	cursor2.execute(total_android)
# 	user_earned_one_or_more_yoobux=cursor3.execute(usr_ernd_one_or_more_yoobx)
# 	print "user_earned_one_or_more_yoobux",user_earned_one_or_more_yoobux
# 	for data in cursor1.fetchall():
# 	    total_IOS_devices=int(data[0])
# 	    print "total_IOS_devices",int(total_IOS_devices)
# 	for data in cursor2.fetchall():
# 	    total_ANDROID_device=int(data[0])
#         print"total_ANDROID_device",int(total_ANDROID_device)

# 	total_device=total_IOS_devices+total_ANDROID_device
# 	print "total_device",total_device

# 	cursor4.execute(watched_videos)
#  	usr_watched_videos=int(cursor4.fetchone()[0])
#  	print"usr_watched_videos",usr_watched_videos
#  	cursor5.execute(ios_usr_in_hun_clb)
#  	try:
# 	 	ios_user_in_hundred_club=cursor5.execute(ios_usr_in_hun_clb)
# 	 	print"ios_user_in_hundred_club",ios_user_in_hundred_club
# 	except:
# 		print "test"
# 		pass
# 	cursor6.execute(android_usr_in_hun_clb)
# 	try:
# 		android_user_in_hundred_club=cursor6.execute(android_usr_in_hun_clb)
# 		print"android_user_in_hundred_club",android_user_in_hundred_club
# 	except:
# 		print "test ok"
#  	try:
# 		Average=float(total_device)/float(user_earned_one_or_more_yoobux)
# 		print"Average",round(Average,2)
# 		Average_of_devices_per_video_usr=float(total_device-(user_earned_one_or_more_yoobux-usr_watched_videos))/float(usr_watched_videos)
# 		print"Average_of_devices_per_video_usr",Average_of_devices_per_video_usr
# 	except:
# 		pass
# avg_of_device_per_user('2016-12-06')
 		
		



class FillDetails(View):
	@rest
	def get(self,request):
		form = EntriesForm()
		return render(request,'dashboard/entries.html',{'form': form})
		
	
	def post(self,request):
		form = EntriesForm(request.POST)
		if form.is_valid():
			entry = form.save(commit=False)
			#print "impressions",type(form.cleaned_data['impressions'])
			#print "revenue",type(form.cleaned_data['revenue'])
			impressions=float(form.cleaned_data['impressions'])
			revenue=float(form.cleaned_data['revenue'])
			#import pdb;
			#pdb.set_trace()
			try:
				entry.ecpm = round(float(revenue*1000)/impressions,2)
				print "ok"
				print entry.ecpm
			except:
				entry.ecpm=0
				print "error"
			entry.save()
			return HttpResponseRedirect("/dashboard/")


class DailyReport(View):
	def get(self,request):
		date=request.GET.get('date','')
		video_revenue_date_wise=Entries.objects.filter(provider_type='video',entry_date=date).aggregate(Sum('revenue'))['revenue__sum']
		banner_revenue_date_wise=Entries.objects.filter(provider_type='banner',entry_date=date).aggregate(Sum('revenue'))['revenue__sum']
		interstitial_revenue_date_wise=Entries.objects.filter(provider_type='interstitial',entry_date=date).aggregate(Sum('revenue'))['revenue__sum']
		sum_ecpm=Entries.objects.filter(provider_type__in=['video','banner','interstitial'],entry_date=date).aggregate(Sum('ecpm'))['ecpm__sum']
		count_ecpm=Entries.objects.filter(provider_type__in=['video','banner','interstitial'],entry_date=date).aggregate(Count('ecpm'))['ecpm__count']
		try:
			avg_ecpm=round(sum_ecpm/count_ecpm,2)
		except:
			avg_ecpm=0


		f = open('DailyReport-{0}.csv'.format(date),'wb')
		try:
		    writer = csv.writer(f)
		    writer.writerow( ('Date','Video revenue', 'Banner revenue', 'Interstitial revenue','Avg ecpm') )
		    writer.writerow( (date,video_revenue_date_wise, banner_revenue_date_wise, interstitial_revenue_date_wise, avg_ecpm) )
		finally:
		    f.close()
		return HttpResponse("Ok")
		
class MonthlyReport(View):
	def post(self,request):
		interesting_files = glob.glob("*.csv") 
		f = open('output.csv','wb')
		writer = csv.writer(f)
		writer.writerow(("Date","Video revenue","Banner revenue","Interstitial revenue"))
		for filename in interesting_files:
			f = open(filename, 'rb')
			header = next(f,"None")
			reader=csv.reader(f)
			for line in reader:
				writer.writerow(line)

		return HttpResponse("Ok")
		


class GoogleAnalyticsDetail(View):
	# @rest
	def get(self,request):
		form = GoogleAnalyticsForm()
		return render(request,'dashboard/googleanalytics.html',{'form': form})

	def post(self,request):
		form = GoogleAnalyticsForm(request.POST)
		if form.is_valid():
			form.save()
			# nos_of_devices=form.cleaned_data['nos_of_devices']
			# print type(nos_of_devices),nos_of_devices
			# device_type=form.cleaned_data['device']
			# print "device_type",device_type
			# print "Done"
			return HttpResponseRedirect("/dashboard/googleform/")






class Detail(View):
	@rest
	def get(self,request):
		import MySQLdb
		connection =MySQLdb.connect(host='127.0.0.1',port=3306,user='root',passwd='root',db='yoo_lat')
		cursor1=connection.cursor()
		cursor2=connection.cursor()
		cursor3=connection.cursor()
		cursor4=connection.cursor()
		cursor5=connection.cursor()
		cursor6=connection.cursor()
		cursor7=connection.cursor()
		cursor8=connection.cursor()
		cursor9=connection.cursor()
		cursor10=connection.cursor()




		query1="select count(*) from user_coins_earn_history where source='new_user' and device_type='IPHONE' and date(added_at)='2016-12-02';"
		query2="select count(*) from user_coins_earn_history where source='new_user' and device_type='ANDROID' and date(added_at)='2016-12-06';"
		query3="select nos_of_devices from google_analytics where device='ANDROID' and entry_date='2017-05-11';"
		query4="select nos_of_devices from google_analytics where device='IOS' and entry_date='2017-05-11';"
		query5="select count(distinct(user_id)) as total_users from user_history where source_id in (14) and date(added_at)='2016-02-26';"
		query6="select h.user_id,sum(h.credit_coins) as total_coins, u.email,h.device_type from user_history h inner join user u on h.user_id=u.id where date(h.added_at)='2016-02-26' group by h.user_id order by sum(h.credit_coins) desc;"
		query7="select sum(extended_video_count) from commercial_video_rewards where date(added_at)='2016-06-29' UNION select sum(intermediate_video_count) from commercial_video_rewards where date(added_at)='2016-06-29' UNION select sum(limited_video_count) from commercial_video_rewards where date(added_at)='2016-06-29';"
		query8="select sum(banner_ad_count) from bannerAd_details where date(added_at)='2016-11-29';"
		query9="select sum(credit_coins) from user_history where source_id in (14) and date(added_at)='2016-02-26';"
		query10="select sum(credit_coins) from user_history where source_id in (14) and date(added_at)='2016-02-26';"

        # query5=query4-query1
        # print query5

		cursor1.execute(query1)
		cursor2.execute(query2)
		cursor3.execute(query3)
		cursor4.execute(query4)
		cursor5.execute(query5)
		cursor6.execute(query6)
		cursor7.execute(query7)
		cursor8.execute(query8)
		cursor9.execute(query9)
		cursor10.execute(query10)







		for row in cursor1.fetchall():
			print row[0]
			new_iphone_user=row[0]

		for row in cursor2.fetchall():
			print row[0]
			new_android_user=row[0]

		for row in cursor3.fetchall():
			print row[0]
			total_android__user=row[0]

		for row in cursor4.fetchall():
			print row[0]
			total_ios__user=row[0]

		for row in cursor5.fetchall():
			print row[0]
			total_existing__user=row[0]

		for row in cursor6.fetchall():
			print row[0],
			total_existing__user=row[1]

		for row in cursor7.fetchall():
			print row[0]
			total_existing__user=row[0]

		for row in cursor8.fetchall():
			print row[0]
			total_existing__user=row[0]


		for row in cursor9.fetchall():
			print row[0]
			total_existing__user=row[0]



		for row in cursor10.fetchall():
			print row[0]
			total_existing__user=row[0]

			existinguser=total_android__user-new_android_user
			print existinguser






		return HttpResponse("Ok")
