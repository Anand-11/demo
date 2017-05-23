'''from yoolotto.second_chance.models import DeviceLoginDetails
from yoolotto.coin.models import DeviceCoins, EmailCoins
from celery.task import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from datetime import date
from django.db.models import Q

def get_1month_previous_date(dt, d_years=0, d_months=0):
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m, 1)

def get_2month_previous_date(dt, d_years=0, d_months=0):
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m-1, 2)

@periodic_task(run_every=crontab(hour='5', minute='0', day_of_week="*"))
def removecoins():
	d = date.today()
	start_date = get_2month_previous_date(d)
	end_date = get_1month_previous_date(d)
	email_info = EmailCoins.objects.filter(Q(reset_date__range=(start_date, end_date))| Q(reset_date=end_date))
	for emial in email_info:
		emial.coins = 0
		emial.dollar_amount = 0
		emial.reset_date = d
		emial.save()
	dev_info = DeviceCoins.objects.filter(Q(reset_date__range=(start_date, end_date))| Q(reset_date=end_date))
	for dev in dev_info:
	    dev.coins = 0
	    dev.reset_date = d
	    dev.save()'''

