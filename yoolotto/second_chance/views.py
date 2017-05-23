import datetime
import math
import json
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic import View
from django.shortcuts import render_to_response
from yoolotto.rest import exceptions
from yoolotto.rest.decorators import rest, Authenticate,check_suspicious_user
from django.core.mail import send_mail
from yoolotto.second_chance.models import FAQ as FaqModel
from yoolotto.coupon.geo.manager import GeoManager
from yoolotto.user.models import Device, UserCoinsDetails, UserClientLogin, UserCoinsDetails,UserToken,YooLottoUser
from yoolotto.second_chance.sendemail import common_send_email
from yoolotto.lottery.models import LotteryTicket
from yoolotto.settings_local import COUPON_MAIL_CC, COUPON_REDEEM_DURATION
from yoolotto.second_chance.models import *
#from yoolotto.settings import AFTER_LOGON_OX, ox, email, password, domain, realm, consumer_key, consumer_secret
from yoolotto.second_chance.models import *
from yoolotto.second_chance.models import Advertisor as AdvertisorModel, AdInventory as InventoryModel
from django.http.response import HttpResponse
from django.conf import settings
from yoolotto.user.cipher import *
from django.db.models import F
from yoolotto.second_chance.daily_goal import *
from yoolotto.coin.models import EmailCoins, DeviceCoins
from yoolotto.second_chance.models import FiberCoins, DwollaUserInfo, DwollaTransactionInfo,EventInfo,DwollaFAQ
from yoolotto.communication.apn import APNSender
from yoolotto.communication.gcm_sender import GCMSender
from yoolotto.rest import exceptions
from yoolotto.second_chance.functions import *

def yoo_games_webpage(request):
    return render_to_response('demo.html')


def login_openx():
    import ox3apiclient

    ox = ox3apiclient.Client(
        email=email,
        password=password,
        domain=domain,
        realm=realm,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        api_path='/ox/4.0'
        )

    AFTER_LOGON_OX=ox.logon(email, password)

    return AFTER_LOGON_OX

class InAppFuelCallback(View):
	@rest
	
	def get(self,request,userID,currency,game_id,sig):
		return {"result":0}

# class to fetch the coupons of a second chance vendor
class AdCoupons(View):
    @rest
    @Authenticate()
    def get(self, request,filter="active"):
        cv_id = request.GET.get('cv_id', None)
        if filter == "active":
            adunits =  InventoryModel.objects.filter(inventory__gt = 0,account_id=cv_id,status='Active')
	    try:
            	return {'results':map(lambda x: x.representation(),adunits),"adunit_id":"537154909"}
	    except:
		return {'results':[]}
        else:
            raise exceptions.WebServiceException("Invalid Coupon Filter")

class AdColony(View):
    @rest
    @Authenticate()
    def get(self,request):
	if request.META["HTTP_YOO_DEVICE_TYPE"] == 'ANDROID':
		zone = "vz337c35351159410f8d"
	else:
        	zone = "vz3ee9d6022cef430bbb"
        return {"send_ticket":zone,"check_ticket":zone,"yoo_games":zone}

# Sample second chance game for android ( In place of In App Fuel of Iphone )        
class AndroidGame(View):
    @rest
    @Authenticate()
    def post(self, request):
        number = settings.GAME_NUMBER
        data = json.loads(request.body)
	if number == data['number']:
            return {'matched':True}
        else:
            return {'matched':False}

# class to provide range of numbers for android game 
class AndroidNumbers(View):
    @rest
    @Authenticate()
    def get(self,request):
        return {"Max":settings.ANDROID_GAME_MAX_NUMBER,"Min":settings.ANDROID_GAME_MIN_NUMBER}

# class to send fb, twitter message 
class SocialMessage(View):
    @rest
    @Authenticate()
    def get(self, request):
        return {"message":settings.SOCIAL_MESSAGE}

# class to generate unique url for sca
class SCA_url(View):
    @rest
    @Authenticate()
    def post(self, request):
        url="http://qa.yoolotto.com/yoogames"
	return{"url":url}

def dynamic_url_call(data,email):
    import urllib2
    user_details = EmailCoins.objects.get(email=email)
    _id = user_details.id
    coins = user_details.coins
    if data['add_coins']:
        if data['gameType'] == 'scratch':
            url = "https://twittaboom.herokuapp.com/dplayurl/yoolotto4?username=yoolotto&password=eE6xzvjG&user="+str(_id)+"&domain=pro&coins="+str(coins)+""
        elif data['gameType'] == 'slot':
            url = "https://twittaboom.herokuapp.com/dplayurl/yoolotto3?username=yoolotto&password=eE6xzvjG&user="+str(_id)+"&domain=pro&coins="+str(coins)+""
    else:
        url = "https://twittaboom.herokuapp.com/dplayurl/yoolottoaer?username=yoolotto&password=yoolotto739"

    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    dynamic_url = res.read()
    return dynamic_url

class SCA_url(View):
    @rest
    @Authenticate()
    def post(self, request):
        data = json.loads(request.body)
        print data
        if (request.META["HTTP_YOO_DEVICE_TYPE"]=="ANDROID" and request.META["HTTP_YOO_APP_VERSION"] <="6.1") or (request.META["HTTP_YOO_DEVICE_TYPE"]=="IPHONE" and request.META["HTTP_YOO_APP_VERSION"] <="6.0"):
            url="http://pro.yoolotto.com/yoogames"
            return{"url":url}
        elif (request.META["HTTP_YOO_DEVICE_TYPE"]=="ANDROID" and request.META["HTTP_YOO_APP_VERSION"] >="8.0") or (request.META["HTTP_YOO_DEVICE_TYPE"]=="IPHONE" and request.META["HTTP_YOO_APP_VERSION"] >="8.0"):
            email=request.META["HTTP_YOO_EMAIL_ID"]
            url = dynamic_url_call(data,email)
            return {"url":url}


# class to show dynamic ads for every screen
class ScreenAds(View):
    @rest
    @Authenticate()
    def get(self,request):              
	import random
        adunits_list = []
        sections_list = []
        result = []
	try:
           '''try:'''
           adunits =  AFTER_LOGON_OX.get('http://ox-ui.yoolotto.com/ox/4.0/adunit?limit=0')['objects']
	   '''except:
               AFTER_LOGON_OX = login_openx()
               adunits =  AFTER_LOGON_OX.get('http://ox-ui.yoolotto.com/ox/4.0/adunit?limit=0')['objects']'''

           sections =  AFTER_LOGON_OX.get('http://ox-ui.yoolotto.com/ox/4.0/sitesection?limit=0')['objects']

           for section in sections :
            if section['site_id'] == settings.OPENX_SITE_ID:
                sections_list.append({"section_id":section['id'],"site_id":section['site_id'],"name":section["name"]})

           for adunit in adunits:
            if adunit['site_id'] == settings.OPENX_SITE_ID:

                if adunit['type_full'] == 'adunit.mobile':
                    if adunit['primary_size'] == '320x50':
	                if adunit['tag_type'] == 'json':
                            adunit_type = 'adunit.bannerad'
                        elif adunit['tag_type'] == 'html':
                            adunit_type = 'adunit.text'
                    elif adunit['primary_size'] == '320x480':
                        adunit_type = 'adunit.image'
                else:
                    adunit_type = adunit['type_full']
		
                adunits_list.append({"adunit_id":adunit['id'],"section_id":adunit['sitesection_id'],"type":adunit_type})

           for index in sections_list:
            info = [{"adunit":item['adunit_id'],"screen":index["name"],"type":item["type"]} for item in adunits_list if item['section_id']==index['section_id']]
            if info:
                result.append(info[random.randint(0,len(info)-1)])

	   valid_screens = ["Yoo Games","Jackpot Result","ScanScreen"]
           valid_data = []
           for index in result:
               if index['screen'] in valid_screens:
                   valid_data.append(index)
           results =  {"ads":valid_data,"domain":"ox-d.yoolotto.com","video_ad_url":"http://ox-d.yoolotto.com/v/1.0/av?auid="}
	   return {"results":results}
	except:
	   return result
        
# class to add coins to device or email on invitation or message        
class InviteFriends(View):
    @rest
    @Authenticate()
    def post(self, request):
        data = json.loads(request.body)
	device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
	app_version = request.META["HTTP_YOO_APP_VERSION"]
        print "dataaaaaa",data
        coins_record, created = EmailCoins.objects.get_or_create(email=data['email'],defaults={'coins': 0})
        user = YooLottoUser.objects.get(email = data['email'])
        
        if data['share']:
            coins_record.coins = coins_record.coins + float(data['share'])*2
            coins_record.share = int(coins_record.share) + int(data['share'])
	    share = int(data["share"])
            amount = float((share)*2)/100
            #amount = round((float((data['share'])*2)/100),2)
            coins_record.dollar_amount = coins_record.dollar_amount + amount
            coins_record.save()
            print coins_record.email
            print coins_record.coins
            share_coins = float(data['share'])*2
	    try:
		if data["share_source"]:
		    if data["share_source"]=="Twitter":
			source = "share_tw_coins"
		    elif data["share_source"]=="Facebook":
			source = "share_fb_coins"
		    else:
			source="share"
	    except:
		source="share"
        user_share_history = UserCoinsEarnHistory(user = user, coins = share_coins,source =source,device_type=device_type)
        user_share_history.save()
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user,credit_coins = share_coins,source = coin_source,credit_amount = amount,device_type = device_type,net_amount = coins_record.dollar_amount,net_coins = coins_record.coins,app_version =app_version)
        user_history.save()
	coins = share_coins
	code = "rewarded"
	send_rewarded_notification(user.id,coins,code)
        email_coins = EmailCoins.objects.filter(email=data['email'])[0]
        total_coins = email_coins.coins
        red_alert = data['red_alert']
        ticket_id = data['ticket_id']
        from yoolotto.lottery.models import LotteryTicket
        try:
            ticket_info = LotteryTicket.objects.filter(id = ticket_id)[0]
            print "ticket_red_alert_info",ticket_info
            ticket_info.red_alert = red_alert
            ticket_info.save()
            red_alertt = ticket_info.red_alert
        except:
            red_alertt = 0
        
        return {"total_coins":total_coins,"coins":coins,"red_alert":red_alertt}

# class to add coins to device or email, when user plays IPhone game (In App Fuel)        
class AddCoins(View):# used for fiber
    @rest
    @Authenticate()
    def post(self, request):
        data = json.loads(request.body)
	user = request.yoo["user"]
    	device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
    	app_version = request.META["HTTP_YOO_APP_VERSION"]
        device_id = request.META["HTTP_YOO_DEVICE_ID"]
        now = datetime.date.today()
        if data['rewarded_video'] !=0:
            try:
                fyber_video_details = FyberVideoDeviceDetails.objects.get(device_id = device_id,added_at__startswith=now)
            except:
                fyber_video_details = FyberVideoDeviceDetails.objects.create(user = user,device_id = device_id,added_at=now)
                fyber_video_details.device_type = device_type
            fyber_video_details.video_count = fyber_video_details.video_count+1
            fyber_video_details.save()
	    try:
                fyber_user_video_details = FyberVideoUserDeviceDetails.objects.get(user = user,user_added_at__startswith=now)
            except:
                fyber_user_video_details = FyberVideoUserDeviceDetails.objects.create(user= user,device_id = device_id,user_added_at=now)
            fyber_user_video_details.user_video_count = fyber_user_video_details.user_video_count+int(1)
            fyber_user_video_details.save()
	try:
	    coins_record = EmailCoins.objects.filter(email = request.META['HTTP_YOO_EMAIL_ID'])[0]
	except:
	    coins_record,created = EmailCoins.objects.get_or_create(email = request.META['HTTP_YOO_EMAIL_ID'] )
	total_coins = coins_record.coins
        if fyber_video_details.video_count <=50 or fyber_user_video_details.user_video_count <=50:
            try:
               coins_data = FiberCoins.objects.filter(email = coins_record.email)[0]
            except: 
                coins_data ,created = FiberCoins.objects.get_or_create(email = coins_record.email)
            coins_data.offer_wall =int(coins_data.offer_wall) + int(data['offer_wall'])
            coins_data.rewarded_video = int(coins_data.rewarded_video) + int(1)#int(data['rewarded_video'])
            coins_data.save()
            coins_record.coins = float(coins_record.coins) + float(data['offer_wall']) + float(data['rewarded_video'])
            temp = float(data['offer_wall']) + float(1)#float(data['rewarded_video'])
            amount = round((float(temp)/100),2)
            coins_record.dollar_amount = coins_record.dollar_amount + amount
            coins_record.save()
            total_coins = coins_record.coins
            user_info = YooLottoUser.objects.get(email = coins_record.email)
            if data['offer_wall'] != 0:
                user_history_info = UserCoinsEarnHistory(user = user_info,coins= data['offer_wall'],source="fiber_ow",device_type=device_type)
                user_history_info.save()
                source = "fyber_ow_coins"
                coins = data['offer_wall']
            if data['rewarded_video'] !=0:
                user_history_info = UserCoinsEarnHistory(user = user_info,coins= data['rewarded_video'],source="fiber_rv",device_type=device_type)
                user_history_info.save()
                source = "fyber_rv_coins"
                coins = float(1)#data['rewarded_video']
            coin_source = CoinSource.objects.get(source_name = source)
            user_history = UserCoinsHistory(user = user_info,credit_coins = coins,source = coin_source,credit_amount = amount,device_type = device_type,net_amount = coins_record.dollar_amount,net_coins = coins_record.coins,app_version =app_version)
            user_history.save()
	    code = "rewarded"
            send_rewarded_notification(user_info.id,coins,code)
        red_alert = data['red_alert']
        ticket_id = data['ticket_id']
        from yoolotto.lottery.models import LotteryTicket
        try:
            ticket_info = LotteryTicket.objects.filter(id = ticket_id)[0]
            print "ticket_red_alert_info",ticket_info
            ticket_info.red_alert = red_alert
            ticket_info.save()
            red_alertt = ticket_info.red_alert
        except:
            red_alertt = 0

        return {"total_coins":total_coins,"red_alert":red_alertt}

class CoinsReduction(View):
    @rest
    @Authenticate()
    def post(self, request):
        data = json.loads(request.body)
        device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
        app_version = request.META["HTTP_YOO_APP_VERSION"]
        email_coins_record = EmailCoins.objects.get(email=request.META["HTTP_YOO_EMAIL_ID"])
        if data["game"] =="scratch":
            coins_to_be_deducted = 3
        else:
            coins_to_be_deducted = 2
        source = "yoogames_spend_coins"
        email_coins_record.coins = email_coins_record.coins -coins_to_be_deducted
        #amount = round(float(coins_to_be_deducted)/1000,4)
        amount = float(coins_to_be_deducted)/100
        email_coins_record.dollar_amount = email_coins_record.dollar_amount - amount
        email_coins_record.save()
        user = YooLottoUser.objects.get(email = request.META["HTTP_YOO_EMAIL_ID"])
        email_history = UserCoinsSpendHistory(user = user,coins= coins_to_be_deducted,source=source)
        email_history.save()
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user,debit_coins = coins_to_be_deducted,source = coin_source,debit_amount = amount,device_type = device_type,net_amount = email_coins_record.dollar_amount,net_coins = email_coins_record.coins,app_version =app_version)
        user_history.save()
        return {"success":True}

class AdRedeem(View):
    @rest
    @Authenticate()
    def post(self, request):
    #valid = False
        data = json.loads(request.body)
        #return_data = {}    
        client_login_record = UserClientLogin.objects.filter(device = request.yoo['device'])[0]
        device_coins_record = DeviceCoins.objects.filter(device_id=request.yoo['device'])[0]
        device_coins = device_coins_record.coins

        if device_coins_record.get_coins() >= 20:
            device_coins_record.coins = F('coins') - 20
            device_coins_record.save()

        else:
            if client_login_record.client_login:
                email_coins_record = EmailCoins.objects.get(email=client_login_record.client_login)
                if email_coins_record.get_coins() >= 20:
                    email_coins_record.coins = F('coins') - 20
                    email_coins_record.save()

        return {"success":True}

        '''if inventory > 0:
            if device_coins >= int(ad_data_source["coins"]):
                valid = True
            else:
                if client_login_record.client_login:
                    email_coins_record = EmailCoins.objects.filter(email=client_login_record.client_login)[0]
                    if email_coins_record.coins >= int(ad_data_source["coins"]):
                        valid = True

            if valid:
                if data["winner"]:
                    ad_data_source["inventory"] = inventory - 1
                    jsonString = json.dumps(ad_data_source)
                    info = {"source": jsonString}
                    AFTER_LOGON_OX.put('http://ox-ui.yoolotto.com/ox/4.0/ad/'+str(InventoryRecord.ad_id)+'',info) # update single lineitem
                    updated_inventory = inventory - 1
                else:
                    updated_inventory = inventory
                try:
                    InventoryRecord.ad_image = ad_data_source['ad_image']
                except:
                    InventoryRecord.ad_image = None
                try:
                    InventoryRecord.vendor = ad_data_source['vendor']
                except:
                    InventoryRecord.vendor = None
                try:
                    InventoryRecord.vendor_image = ad_data_source['vendor_image']
                except:
                    InventoryRecord.vendor_image = None
                try:
                    InventoryRecord.coins = ad_data_source['coins']
                except:
                    InventoryRecord.coins = 0
                try:
                    InventoryRecord.InventoryRecord.timer = ad_data_source['timer']
                except:
                    InventoryRecord.timer = False
                try:
                    InventoryRecord.ad_type = ad_data_source['type']
                except:
                    InventoryRecord.ad_type = None
                try:
                    InventoryRecord.video_url = ad_data_source['videourl']
                except:
                    InventoryRecord.video_url = None
                InventoryRecord.inventory = updated_inventory
                
                InventoryRecord.save()

                if InventoryRecord.type == 'physical':
                    AdIssueRecord = AdIssue(ad=InventoryRecord,address=data['address'],email=data['email'],device=request.yoo['device'],phone=data['phone'],won=data['winner'])
                else:
                    AdIssueRecord = AdIssue(ad=InventoryRecord,email=data['email'],device=request.yoo['device'],won=data['winner'])
                AdIssueRecord.save()

                if data['winner']:
                    subject = "Second Chance Ad"
                    context = {}
                    text_template_path = "second_chance_email.txt"
                    html_template_path = "second_chance_email.html"
                    context_data = {'second_chance_obj': InventoryRecord}
                    recipients = [data['email'], 'subodh.deoli@spa-systems.com', 'kapil.soni@spa-systems.com']
		    common_send_email(subject, text_template_path, html_template_path,context_data, recipients)
		    
                    return_data['email'] = 1
		    return_data['message'] = 'Email is sent'
                    return_data['screen'] = settings.SECOND_CHANCE_WINNING_MESSAGE 
                else:
                    return_data['email'] = 0
		    #return_data['message'] = 'Better luck next time'
		    return_data['screen'] = settings.SECOND_CHANCE_LOOSING_MESSAGE

                
                if device_coins_record.get_coins() >= 20:
                    device_coins_record.coins = F('coins') - 20
                    device_coins_record.save()

                    
                else:
                    if client_login_record.client_login:
                        email_coins_record = EmailCoins.objects.get(email=client_login_record.client_login)
                        if email_coins_record.get_coins() >= 20:
                            email_coins_record.coins = F('coins') - 20
                            email_coins_record.save()

            else:
                return_data['email'] = 0
                return_data['message'] = 'You do not have enough coins'
                return_data['screen'] = settings.SECOND_CHANCE_LOOSING_MESSAGE
                
                
        else:
            
	    return_data['email'] = 0
            return_data['message'] = 'No Inventory left for this ad in OpenX'
            return_data['screen'] = settings.SECOND_CHANCE_LOOSING_MESSAGE

	return return_data'''

#class to show the list of advertisors for second chance
class Advertisors(View):
    @rest
    @Authenticate()
    def get(self, request):
	user = request.yoo["user"]
        
        Inventories = InventoryModel.objects.filter(inventory__gt = 0,status='Active')
        Vendors = set([inventory.account for inventory in Inventories ])
        
        return map(lambda x: x.representation(),Vendors)

#class to show the list of frequently asked questions and answers
class FrequentQuestions(View):
    @rest
    def get(self, request):
        Faqs = FaqModel.objects.all()
        return map(lambda x: x.representation(), Faqs)
        
class TimerAd(View):
    @rest
    @Authenticate()
    def post(self, request):
        user = request.yoo["user"]
        data = json.loads(request.body)
        _id = int(data['id'])
        
        #issue = AdIssue.objects.get(pk=_id)
        
        try:
            #ad_stores = AdStoresModel.objects.filter(ad=issue.ad)
            result = []
            
            _result1 = {
                "name": "Dominos",
                "code": "Dominos",
                "address": "Sector q",
                "address_2": "Sector 18",
                "city": "Noida",
                "state": "Uttar Pradesh",
                "postal_code": "248001",
                "phone": "9999998899",
                "latitude": "28.646951",
                "longitude": "77.310984",
                "distance": "280"
            }
            
            result.append(_result1)
            
            _result2 = {
                "name": "KFC",
                "code": "KFC",
                "address": "Block A",
                "address_2": "Sector 1",
                "city": "Gurgaon",
                "state": "Haryana",
                "postal_code": "248332",
                "phone": "8989898898",
                "latitude": "28.644897",
                "longitude": "77.335583",
                "distance": "780"
            }
            
            result.append(_result2)     

            return result
        except:
            raise exceptions.WebServiceException("This is not a timer coupon")
            
            
class TimeCal(View):
    @rest
    @Authenticate()
    def get(self,request):
        #client_login_details = UserClientLogin.objects.filter(device = request.yoo['device'2])[0]
        email_coins_info = EmailCoins.objects.get(email = request.META['HTTP_YOO_EMAIL_ID'])
        now = datetime.datetime.now()
        now = datetime.datetime.now()
        reset_date = email_coins_info.reset_date + datetime.timedelta(days=69)
        time_left = (reset_date - now).total_seconds()
        return {"time_left":time_left}

class Dwolla(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        device_type = request.META['HTTP_YOO_DEVICE_TYPE']
        app_version = request.META["HTTP_YOO_APP_VERSION"]
        android_version = ["1.0","1.1"]
        if (device_type == "ANDROID" and app_version in android_version):
            decrypted_data = androidDecryptionsecurity(request.body)
            data = json.loads(decrypted_data)
        else:
	    data = json.loads(request.body)
        # print data
	    #raise exceptions.WebServiceException("Please update your app to continue earnings")
        coins_reduced=0
        user_details = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
        dwolla_email= data['redeem_email']
        dwolla_amount= data['amount']
        coins_info = EmailCoins.objects.get(email= user_details.email)
        
        if data['source'] == "coins":
            if float(coins_info.dollar_amount) - float(data['amount']) >=0:
                dwolla_info = DwollaUserInfo(user = user_details,dwolla_email= dwolla_email,dwolla_amount= dwolla_amount)
                dwolla_info.save()
                coins_info.dollar_amount = float(coins_info.dollar_amount) - float(data['amount'])
                coins_reduced = float(data['amount'])* 100
                coins_info.coins = float(coins_info.coins) - float(coins_reduced)
                coins_info.save()
            else:
                return{"success":False,"reason":"Insufficient balance for cashout"}

        source = "dwolla_cash"
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user_details,debit_coins = coins_reduced ,source = coin_source,debit_amount = data['amount'],device_type = device_type,net_amount = coins_info.dollar_amount,net_coins = coins_info.coins,app_version =app_version)
        user_history.save()
        return {"success":True,"total_coins":coins_info.coins,"dollar_amount":coins_info.dollar_amount}  

class FantasyFrequentQuestions(View):
    @rest
    def get(self, request):
        faqs = FantasyFAQ.objects.all()
        return map(lambda x: x.representation(), faqs)

class EventTracking(View):
    #@rest
    def post(self,request):
	data = json.loads(request.body)
	referring_user = data['first_referring_identity']
	event_occured = data['event']
	event_details = EventInfo(referring_user = referring_user,event_occured = event_occured)
	event_details.save()
	user_details = YooLottoUser.objects.get(email = referring_user)
	user_device_details = Device.objects.filter(user = user_details.id)
	for device in user_device_details:
	    text = "You have been awarded for referral"
	    try:
                if device.device_type == "IPHONE":
                    apn = APNSender(device.device_token, text=text,custom={"code": "referral_tracking"})
                    apn.send()
                elif device.device_type == "ANDROID":
                    gcm = GCMSender(to=[device.device_token], data={"text": text,"code": "referral_tracking"})
                    gcm.send()
            except:
                pass
            print "everything successfullllllllllllllll"
        return HttpResponse('result')


class CoinsAdditionReferral(View):
    @rest
    def post(self,request):
    	data = json.loads(request.body)
    	referring_user = data['referring_user']
        device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
        app_version = request.META["HTTP_YOO_APP_VERSION"]
    	import datetime
        now= datetime.datetime.now()
    	referring_user_coins = data['referring_user_coins']
    	referred_user_coins = data['referred_user_coins']
    	try:
    	    event_details = EventInfo.objects.get(referring_user = referring_user,referred_user= data['referred_user'])
    	except:
    	    try:
                event_details = EventInfo.objects.filter(referring_user = referring_user,referred_user = '')[0]
                event_details.referred_user = data['referred_user']
    	    except:
    		    event_details,created = EventInfo.objects.get_or_create(referring_user = referring_user,referred_user = '')
    	event_details.referred_user_coins = event_details.referred_user_coins + float(data['referred_user_coins'])
    	event_details.referring_user_coins = event_details.referring_user_coins + float(data['referring_user_coins'])
    	event_details.updated_at = now
    	event_details.save()
    	try:
    	    referring_coins = EmailCoins.objects.get(email = referring_user)
            referring_coins.coins = referring_coins.coins + float(data['referring_user_coins'])
            amount = float(data['referring_user_coins'])/100
            referring_coins.dollar_amount = referring_coins.dollar_amount + amount
            referring_coins.save()
            if data['referred_user']:
                r_user = data['referred_user']
                referred_coins = EmailCoins.objects.get(email = r_user)
                referred_coins.coins = referred_coins.coins + float(data['referred_user_coins'])
                amount = float(data['referred_user_coins'])/100
                referred_coins.dollar_amount = referred_coins.dollar_amount + amount
                referred_coins.save()
    	except:
    	    pass
        try:
            if referring_user_coins>0:
                source = "referral_coins"
                user_info = YooLottoUser.objects.get(email=referring_user)
                coins_record = EmailCoins.objects.get(email=user_info.email)
                coin_source = CoinSource.objects.get(source_name = source)
                amount = float(data['referring_user_coins'])/100
                user_history = UserCoinsHistory(user = user_info,credit_coins = referring_user_coins,source = coin_source,credit_amount = amount,device_type = device_type,net_amount = coins_record.dollar_amount,net_coins = coins_record.coins,app_version =app_version)
                user_history.save()
		coins = data['referring_user_coins']
            elif referred_user_coins>0:
                source="referred_coins"
                user_info = YooLottoUser.objects.get(email=data['referred_user'])
                coins_record = EmailCoins.objects.get(email=user_info.email)
                coin_source = CoinSource.objects.get(source_name = source)
                amount = float(data['referred_user_coins'])/100
                user_history = UserCoinsHistory(user = user_info,credit_coins = referred_user_coins,source = coin_source,credit_amount = amount,device_type = device_type,net_amount = coins_record.dollar_amount,net_coins = coins_record.coins,app_version =app_version)
                user_history.save()
		coins = data['referred_user_coins']
        except:
            pass
	code = "rewarded"
	send_rewarded_notification(user_info.id,coins,code)
	return {"success":True}


class DwollaFrequentQuestions(View):
    @rest
    def get(self, request):
        faqs = DwollaFAQ.objects.all()
        return map(lambda x: x.representation(), faqs)

class AppThisPostback(View):
    @rest
    def get(self, request):
        click_id = request.GET.get("c")
        _payout = request.GET.get("p")
        payout=_payout
        offer_id =request.GET.get("offer_id")
        offer_name=request.GET.get("offer_name")
        user_details = click_id.split("_")
        user_id=user_details[0]
        device_type = user_details[1]
        offer_type = user_details[2]
        device_type = device_type.upper()
        user_info=YooLottoUser.objects.get(id=user_id)
        appthis_info = AppThisDetails(user=user_info,click_id=click_id,offer_id=offer_id,offer_name=offer_name,device_type=device_type)
        email_info =EmailCoins.objects.get(email = user_info.email)
        config_details = ConfigurationSettings.objects.get(name="appthis_exchange_rate_coins")
        exchange_rate = config_details.value
        yoo_bux_cal = float(payout)*exchange_rate
        import math
        yoo_bux_cal = math.floor(yoo_bux_cal)
        email_info.coins = float(email_info.coins) + float(yoo_bux_cal)
        amount = round((float(yoo_bux_cal)/100),2)
        email_info.dollar_amount = email_info.dollar_amount + amount
        email_info.save()
        appthis_info.dollar_amount=amount
        appthis_info.yoo_bux=yoo_bux_cal
	appthis_info.payout =float(payout)
        appthis_info.save()
        mystery ="Mystery"
        realtime = "RealTime"
        if realtime in offer_type:
            source = "appthis_ow_coins"
        elif mystery in offer_type:
            source ="appthis_mystery_coins"
	else:
	    source ="appthis_coins"
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user_info,credit_coins = yoo_bux_cal ,source = coin_source,credit_amount = amount,device_type = device_type,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
        user_history.save()
	try:
	    offer_details = AppThisOfferInfo.objects.get(click_id = click_id)
            offer_details.rewarded = 1
            offer_details.save()
	except:
	    pass
	code = "rewarded"
	send_rewarded_notification(user_info.id,yoo_bux_cal,code)
        return HttpResponse('result')

def offer_details(offer_det):
        result = {"offer_name": offer_det.offer_name,"yoo_bux": float(offer_det.yoo_bux)}
        return result

class AppThisTransactionHistory(View):
    @rest
    @Authenticate()
    def get(self,request):
        user_details = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
        #user_details = YooLottoUser.objects.get(email="spa5@gmail.com");
        users_offers = AppThisDetails.objects.filter(user_id = user_details).order_by("-added_at")
        tranc_hist =[]
        for det in users_offers:
            tranc_hist.append(offer_details(det))
        '''import logging 
        LOG_FILENAME = 'logging_trans.out'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
        logging.debug(tranc_hist)'''
        return {"tranc_history":tranc_hist}


class AppThisFrequentQuestions(View):
    @rest
    def get(self, request):
        faqs = AppThisFAQ.objects.all()
        return {"faqs":map(lambda x: x.representation(), faqs)}

class AppThisInstructionsFAQ(View):
    @rest
    @Authenticate()
    def post(self, request):
        data=json.loads(request.body)
        offers_record = AppThisDetails.objects.filter(offer_id=data["offer_id"]).count()
        faqs = AppThisInstructions.objects.all()
        instructions_info = AppThisInstructions.objects.get(id=1)
        instructions =instructions_info.instructions
        _faq =map(lambda x: x.representation(), faqs)
        return {"faq":_faq,"offer_count":offers_record,"instructions":instructions}

class GiftCardCashout(View):
    @rest
    @Authenticate()
    def post(self,request):
        device_type = request.META['HTTP_YOO_DEVICE_TYPE']
        app_version = request.META["HTTP_YOO_APP_VERSION"]
        android_version = ["1.0","1.1"]
        # if (device_type == "ANDROID" and app_version in android_version):
        #     decrypted_data = androidDecryptionsecurity(request.body)
        #     data = json.loads(decrypted_data)
        # else:
        #     raise exceptions.WebServiceException("Please update your app to continue earnings")
        data=json.loads(request.body)
        coins_reduced=0
        user_details = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
        gift_card_name = data['gift_card_name']
        user_redeem_email= data['redeem_email']
        cashout_amount= data['amount']
        coins_info = EmailCoins.objects.get(email= user_details.email)
        if data['source'] == "coins":
            if float(coins_info.dollar_amount) - float(data['amount'])>= 0:
                gift_card_details = GiftCardCashoutDetails(user = user_details,gift_card_name = gift_card_name,user_redeem_email= user_redeem_email,cashout_amount= cashout_amount)
                gift_card_details.save()
                coins_info.dollar_amount = float(coins_info.dollar_amount) - float(data['amount'])
                coins_reduced = float(data['amount'])* 100
                coins_info.coins = float(coins_info.coins) - float(coins_reduced)
                coins_info.save()
            else:
                return{"success":False,"reason":"Insufficient balance for cashout"}

        source = "giftcard_cash"
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user_details,debit_coins = coins_reduced ,source = coin_source,debit_amount = data['amount'],device_type = device_type,net_amount = coins_info.dollar_amount,net_coins = coins_info.coins,app_version =app_version)
        user_history.save()
        return {"success":True,"total_coins":coins_info.coins,"dollar_amount":coins_info.dollar_amount}
        

class TransactionHistory(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        page_no = data['page_no']
        paginate_by = 10
        result =[]
        user = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
        user_details = UserCoinsHistory.objects.filter(user_id =user.id).order_by("-added_at")
        print len(user_details)
        paginator = Paginator(user_details, paginate_by)
        try:
            details = paginator.page(page_no)
        except:
            pass
        if paginator.page(page_no).has_next() == True:
            load_more = True
        else:
            load_more = False
        for user in details:
            _result = user.representation()
            result.append(_result)
        print result
        return{"result":result,"load_more":load_more}

class AppThisOfferDetails(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        click_id = data['click_id']
        user_details = click_id.split("_")
        user_id=user_details[0]
        user_info=YooLottoUser.objects.get(id=user_id)
	try:
            android_package_name = data['android_package_name']
        except:
            android_package_name =""
        appthis_info,created = AppThisOfferInfo.objects.get_or_create(user=user_info,click_id=click_id,appthis_offer_id=data['offer_id'],appthis_offer_name=data['offer_name'],android_package_name= android_package_name)
        appthis_info.save()
	#send_offer_download_notification(user_id)
        return{"success":True}

class AppThisAndroidPackageDetails(View):
    @rest
    @Authenticate()
    def get(self,request):
        from datetime import date
        todays_date = date.today()
        result=[]
        email = request.META['HTTP_YOO_EMAIL_ID']
        user_info = YooLottoUser.objects.get(email =  email)
        offer_details = AppThisOfferInfo.objects.filter(user = user_info,added_at__startswith=todays_date)
        #print "offer_details",offer_details
        for user in offer_details:
            _result = user.representation()
            result.append(_result)
        #print result
        return{"offer_details":result}

class AppThisAndroidInstalledOfferDetails(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        #try:
        for click_id in data['click_details']:
            appthis_info = AppThisOfferInfo.objects.get(click_id = click_id)
            appthis_info.installed =1
            appthis_info.save()
        return {"success":True}

class ApPromotersPostback(View):
    @rest
    def get(self, request):
        import logging
        LOG_FILENAME = 'appromoter_postback_log.out'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
    	logging.debug(request)
    	#try:
        aff_sub = request.GET.get("aff_sub")
        _payout = request.GET.get("payout")
        payout=_payout
        offer_id =request.GET.get("offer_id")
        offer_name=request.GET.get("offer_name")
        currency=request.GET.get("currency")
        offer_url_id=request.GET.get("offer_url_id")
        ip=request.GET.get("ip")
        device_os_version=request.GET.get("device_os_version")
        device_model=request.GET.get("device_model")
        print "jsakkkkkkk"
        datetime=request.GET.get("datetime")
        print datetime
        device_os=request.GET.get("device_os")
        print device_os
        device_source=request.GET.get("source")
        device_brand=request.GET.get("device_brand")
        #user_agent=request.GET.get("user_agent")
        transaction_id=request.GET.get("transaction_id")
        user_details = aff_sub.split("_")
        print user_details
        user_id=user_details[0]
        user_info=YooLottoUser.objects.get(id=user_id)
        print "uservb",user_info
        appthis_info = AppromoterPostbackDetails(user=user_info,aff_sub=aff_sub,offer_id=offer_id,offer_name=offer_name,device_os=device_os,source=device_source,transaction_id=transaction_id,currency=currency,offer_url_id=offer_url_id,device_os_version=device_os_version,ip=ip,device_brand=device_brand,device_model=device_model,datetime=datetime)
        email_info =EmailCoins.objects.get(email = user_info.email)
        #config_details = ConfigurationSettings.objects.get(key_name="APPROMOTER_EXCHANGE_RATE")
        #exchange_rate = config_details.value
        #config_details = ConfigurationSettings.objects.get(key_name="DOLLAR_EXCHANGE_RATE")
        #dollar_exchange_rate = config_details.value
	exchange_rate = 23
	dollar_exchange_rate=100
        yoo_bux_cal = float(payout)*exchange_rate
        import math
        yoo_bux_cal = math.floor(yoo_bux_cal)
        email_info.coins = float(email_info.coins) + float(yoo_bux_cal)
        amount = round((float(yoo_bux_cal)/dollar_exchange_rate),2)
        email_info.dollar_amount = email_info.dollar_amount + amount
        email_info.save()
        appthis_info.dollar_amount=amount
        appthis_info.yoo_bux=yoo_bux_cal
        appthis_info.payout =float(payout)
        appthis_info.save()
        source = "appromoter_coins"
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user_info,credit_coins = yoo_bux_cal ,source = coin_source,credit_amount = amount,device_type = device_source,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
        user_history.save()
        try:
            offer_details = AppromoterInstallationInfo.objects.get(aff_sub = aff_sub)
            offer_details.rewarded = 1
            offer_details.save()
        except:
            pass
	code = "rewarded"
	send_rewarded_notification(user_info.id,yoo_bux_cal,code)
        return {"success":True}
	

'''class AppromoterInstalledDetails(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        aff_sub = data['aff_sub']
        user_details = aff_sub.split("_")
        user_id=user_details[0]
        user_info=YooLottoUser.objects.get(id=user_id)
        appromoter_info,created = AppromoterInstallationInfo.objects.get_or_create(user=user_info,aff_sub=aff_sub,appromoter_offer_id=data['offer_id'],appromoter_offer_name=data['offer_name'],source=data['source'])
        appromoter_info.save()
	#send_offer_download_notification(user_id)
        return{"success":True}'''

def appthis_representation(data):
    result = {
            "id":data.id,
            "offer_id": data.offer_id,
            "offer_name": data.offer_name,
            "coins": data.yoo_bux
        }
        
    return result

def appromoters_representation(data):
    result = {
            "id":data.id,
            "offer_id": data.offer_id,
            "offer_name": data.offer_name,
            "coins": data.coins
        }
        
    return result

class LifeTimeValueStatus(View):
    @rest
    #@Authenticate()
    def get(self,request):
        from datetime import date
        todays_date = date.today()
        print todays_date
        appthis_result = []
        appromoters_result = []
        user_info = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
        #user_info = YooLottoUser.objects.get(email ="hi@mailinator.com")
        appromoters_info = AppromoterPostbackDetails.objects.filter(user = user_info,offer_tagged =0,added_at__startswith=todays_date)
        print appromoters_info
        appthis_info = AppThisDetails.objects.filter(user = user_info,offer_tagged =0,added_at__startswith=todays_date)
        print appthis_info
        for data in appthis_info:
            print data
            _result = appthis_representation(data)
            appthis_result.append(_result)
        for data in appromoters_result:
            print data
            _result = appromoters_representation(data)
            appromoters_result.append(_result)
        return{"appthis_offers_details":appthis_result,"appromoters_offers_details":appromoters_result}

            
class LifeTimeValueOfferId(View):
    @rest
    #@Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        print data
        appromoter_id_list = data['appromoter_id_list']
        appthis_id_list = data['appthis_id_list']
        if len(appromoter_id_list)>0:
            for i in appromoter_id_list:
                appromoter_offer_list = AppromoterPostbackDetails.objects.get(id=i)
                appromoter_offer_list.offer_tagged=1
                appromoter_offer_list.save()
        if len(appthis_id_list)>0:
            for i in appthis_id_list:
                appthis_offer_list = AppThisDetails.objects.get(id=i)
                appthis_offer_list.offer_tagged=1
                appthis_offer_list.save()
        return {"success":True}

class KiipDetails(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        print data
        user_info = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
	#device_source = request.META['HTTP_YOO_DEVICE_TYPE']
	device_source = request.META["HTTP_YOO_DEVICE_TYPE"]
        content_id = data['content_id']
        transaction_id = data['transaction_id']
        yoo_bux = data['yoo_bux']
        signature = data['signature']
	dollar_amount = float(yoo_bux)/100
        kiip_info = KiipUserInfo(user = user_info,content_id= content_id,transaction_id= transaction_id,yoo_bux= yoo_bux,signature= signature,source=device_source,dollar_amount = dollar_amount)
        kiip_info.save()
        source = "kiip_coins"
        coin_source = CoinSource.objects.get(source_name = source)
	email_info = EmailCoins.objects.get(email= user_info.email)
	email_info.coins= email_info.coins+yoo_bux
	email_info.dollar_amount = email_info.dollar_amount+dollar_amount
	email_info.save()
        user_history = UserCoinsHistory(user = user_info,credit_coins = yoo_bux ,source = coin_source,credit_amount = dollar_amount,device_type = device_source,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
        user_history.save()
	code = "rewarded"
	send_rewarded_notification(user_info.id,yoo_bux,code)
	return {"success":True,"total_coins":email_info.coins}

class PollFillDetails(View):
    @rest
    def get(self, request):
        request_uuid =request.GET.get("request_uuid")
        cpa =request.GET.get("cpa")
        device_id =request.GET.get("device_id")
        user_details = request_uuid.split("_")
        user_id=user_details[0]
        user_info=YooLottoUser.objects.get(id=user_id)
        email_info =EmailCoins.objects.get(email = user_info.email)
        #exchange_rate = 23
        dollar_exchange_rate = 100
        yoo_bux_cal = 5
        yoo_bux_cal = math.floor(yoo_bux_cal)
        email_info.coins = float(email_info.coins) + float(yoo_bux_cal)
        amount = round((float(yoo_bux_cal)/dollar_exchange_rate),2)
        email_info.dollar_amount = email_info.dollar_amount + amount
        email_info.save()
        pollfish_info = PollFishInfo(user = user_info,cpa= cpa,request_uuid=request_uuid,coins= yoo_bux_cal,dollar_amount= amount,device_id=device_id)
        pollfish_info.save()
        source = "pollfish_coins"
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user_info,credit_coins = yoo_bux_cal ,source = coin_source,credit_amount = amount,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
        user_history.save()
	code = "rewarded"
	send_rewarded_notification(user_info.id,yoo_bux_cal,code)
        return {"success":True}

'''class DailyCheckInReward(View):
    @rest
    @Authenticate()
    def get(self,request):
        user_info = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
        #user_info = YooLottoUser.objects.get(email ="hi@mailinator.com")
        device_source = request.META['HTTP_YOO_DEVICE_TYPE']
        email_info =EmailCoins.objects.get(email = user_info.email)
        daily_once_reward_coins = 1
        daily_once_reward_amount = float(1)/100
        email_info.coins=email_info.coins+daily_once_reward_coins
        email_info.dollar_amount= email_info.dollar_amount+ daily_once_reward_amount
        email_info.save()
        source="daily_checkin_rewards"
        coin_source = CoinSource.objects.get(source_name = source)
        user_history = UserCoinsHistory(user = user_info,credit_coins = daily_once_reward_coins ,source = coin_source,credit_amount = daily_once_reward_amount,device_type = device_source,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
        user_history.save()
	send_rewarded_notification(user_info.id,daily_once_reward_coins)
        return {"success":True,"total_coins":email_info.coins}'''

class DailyCheckInReward(View):
    @rest
    @Authenticate()
    def get(self,request):
        iphone_version = ["8.0","8.1","8.2","8.3","8.4","8.5","8.6","8.7","8.8","8.9","8.10"]
        android_version = ["1.0","1.1"]
        device_source = request.META['HTTP_YOO_DEVICE_TYPE']
	app_version = request.META["HTTP_YOO_APP_VERSION"]
        if (device_source == "IPHONE" and app_version in iphone_version) or (device_source == "ANDROID" and app_version in iphone_version):
            user_info = YooLottoUser.objects.get(email =request.META['HTTP_YOO_EMAIL_ID'])
            now = datetime.date.today()
            source="daily_checkin_rewards"
            coin_source = CoinSource.objects.get(source_name = source)
            try:
                user_history = UserCoinsHistory.objects.filter(user = user_info,source = coin_source,added_at__startswith = now) 
            except:
                user_history=[]
            email_info =EmailCoins.objects.get(email = user_info.email)
            if len(user_history) == 0:
                daily_once_reward_coins = 1
                daily_once_reward_amount = float(1)/100
                email_info.coins=email_info.coins+daily_once_reward_coins
                email_info.dollar_amount= email_info.dollar_amount+ daily_once_reward_amount
                email_info.save()
                coin_source = CoinSource.objects.get(source_name = source)
                user_history = UserCoinsHistory(user = user_info,credit_coins = daily_once_reward_coins ,source = coin_source,credit_amount = daily_once_reward_amount,device_type = device_source,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
                user_history.save()
		code = "rewarded"
		#send_rewarded_notification(user_info.id,daily_once_reward_coins,code)
		return {"success":True,"total_coins":email_info.coins}
	    else:
		raise exceptions.WebServiceException("You can play only once in a day")
	else:
	    raise exceptions.WebServiceException("Please update your app to continue earnings")

class AppromoterParametersValues(View):
    @rest
    @Authenticate()
    def get(self,request):
        return {"status":"active","limit":30,"Incent":"yes","conversion_type":None,"max_payout":0,"min_payout":0,"app_price":"free","offset":0,"appromoters_payout":23}

class AppromoterInstalledDetails(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        aff_sub = data['aff_sub']
        user_details = aff_sub.split("_")
        user_id=user_details[0]
        try:
            android_package_name = data['android_package_name']
        except:
            android_package_name =""
        user_info=YooLottoUser.objects.get(id=user_id)
        appromoter_info,created = AppromoterInstallationInfo.objects.get_or_create(user=user_info,aff_sub=aff_sub,appromoter_offer_id = data['offer_id'],appromoter_offer_name=data['offer_name'],source=data['source'],android_package_name=android_package_name)
        appromoter_info.save()
        #send_offer_download_notification(user_id)
        return{"success":True}

class AppromotersAndroidPackageDetails(View):
    @rest
    @Authenticate()
    def get(self,request):
        from datetime import date
        todays_date = date.today()
        result=[]
        email = request.META['HTTP_YOO_EMAIL_ID']
        #email="hi@mailinator.com"
        user_info = YooLottoUser.objects.get(email =  email)
        offer_details = AppromoterInstallationInfo.objects.filter(user = user_info,added_at__startswith=todays_date)
        #print "offer_details",offer_details
        for user in offer_details:
            _result = user.representation()
            result.append(_result)
        return{"offer_details":result}

class AppromotersAndroidInstalledOfferDetails(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        #try:
        for aff_sub_id in data['aff_sub_details']:
            appthis_info = AppromoterInstallationInfo.objects.get(aff_sub = aff_sub_id)
            appthis_info.installed =1
            appthis_info.save()
        return {"success":True}

class AddToAppDetails(View):# used for fiber
    @rest
    @Authenticate()
    def post(self, request):
        data = json.loads(request.body)
        email = request.META['HTTP_YOO_EMAIL_ID']
        user = YooLottoUser.objects.get(email = email)
        device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
        device_id = request.META["HTTP_YOO_DEVICE_ID"]
        now = datetime.date.today()
        currency_value = data['currency_value']
        ad_provider = data['ad_provider']
        coins_record = EmailCoins.objects.get(email = email)
        if currency_value !=0:
            coins_source ="adtoapp"
            updateVideoDevice(device_id, coins_source)
            updateVideoUser(user, coins_source)
        device_video_details,created = RewardedVideoDeviceDetails.objects.get_or_create(device_id = device_id, added_at=now)
        user_video_details,created = RewardedVideoUserDetails.objects.get_or_create(user=user, added_at=now)
        try:
            adtoapp_details = AdToAppInfo.objects.get(user = user,ad_provider=ad_provider)
            adtoapp_details.currency_value = adtoapp_details.currency_value + float(currency_value)
            adtoapp_details.save()
        except:
            print "in except"
            adtoapp_details = AdToAppInfo.objects.create(user = user,ad_provider=ad_provider,currency_value= currency_value) 
        if (device_video_details.adtoapp_video_count <=50 or user_video_details.adtoapp_video_count <=50) and user_video_details.adtoapp_video_count % 2 == 0:
            payout= currency_value
            source = "ApToApp_Coins"
            coins_data =reward_coins(email,source,user,device_type,payout,exchange_rate=1)
            adtoapp_details.yoo_bux += coins_data['coins']
            adtoapp_details.dollar_amount += coins_data['dollar_amount']
            adtoapp_details.save()
	    code = "rewarded"
            send_rewarded_notification(user.id,coins_data['coins'],code)
	    return {"total_coins":coins_record.coins}

class NativexPostback(View):
    @rest
    def get(self, request):
        import logging
        LOG_FILENAME = 'nativex_postback_log.out'
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
        logging.debug(request)
        amount = request.GET.get("amount")
        offer_id =request.GET.get("offer_id")
        offer_name=request.GET.get("offer_name")
        client_ip=request.GET.get("client_ip")
        publisher_sessionid=request.GET.get("publisher_sessionid")
        publisher_user_id=request.GET.get("accountId")
        user_details = publisher_user_id.split("_")
        user_id=user_details[0]
        device_type = user_details[1]
        device_id = user_details[2]
        user_info=YooLottoUser.objects.get(id=user_id)
        nativead_info = NativexPostbackDetails.objects.create(user=user_info, publisher_user_id=publisher_user_id,
                                                               device_id=device_id, offer_id=offer_id, offer_name=offer_name,
                                                               publisher_sessionid=publisher_sessionid,
                                                               client_ip=client_ip, device_type=device_type,amount=amount)
        if amount != 0:
            coins_source = "nativex"
            now = datetime.date.today()
            video_device_info,created = RewardedVideoDeviceDetails.objects.get_or_create(device_id=device_id, added_at=now)
            video_user_info,created = RewardedVideoUserDetails.objects.get_or_create(user=user_info, added_at=now)
            updateVideoDevice(device_id, coins_source)
            updateVideoUser(user_id, coins_source)
        if (video_device_info.nativex_video_count <= 50 or video_user_info.nativex_video_count <= 50) and video_user_info.nativex_video_count % 2 == 0:
            source = "NativeAd_Coins"
            coins_info = reward_coins(user_info.email, source, user_info, device_type, amount)
            yoo_bux_cal = coins_info["coins"]
            dollar_amt = coins_info["dollar_amount"]
            nativead_info.yoo_bux = yoo_bux_cal
            nativead_info.dollar_amount = dollar_amt
            nativead_info.save()

            # To send notification of coins
	    code = "rewarded"
            send_rewarded_notification(user_info.id, yoo_bux_cal,code)
        return {"success": True}

class AerservPostback(View):
    @rest
    def get(self,request):
        print "in aerserv post"
        client_id = request.GET.get("user")
        amount = request.GET.get("amount")
        #currency = request.GET.get("currency")
        print client_id, amount
        user_details = client_id.split("_")
        user_id = user_details[0]
        device_type = user_details[1]
        device_id = user_details[2]
        user_info = YooLottoUser.objects.get(id=user_id)
        print "user_info", user_info
        amount = 1
        aerserv_info = AervservPostbackDetails.objects.create(user=user_info, client_id=client_id, amount=amount,
                                                              device_id=device_id, device_type=device_type)
        now = datetime.datetime.now()
        coins_source = "aersrv"
        print "coins", coins_source
        updateVideoDevice(device_id, coins_source)
        user_video_count = updateVideoUser(user_id, coins_source)
        print user_video_count,"user_video_count"
        return {"success": True}

class SupersonicPostback(View):
    @rest
    def get(self, request):
        user_details = request.GET.get("appUserId")
        print "user_details:", user_details
        user_details_list = user_details.split("_")
        user_id = user_details_list[0]
        device_type = user_details_list[1]
        device_id = user_details_list[2]
        user_info = YooLottoUser.objects.get(id=user_id)
        rewards = request.GET.get("rewards")
        event_id = request.GET.get("eventId")
        print rewards, "eventid", event_id
        supersonic_info = SupersonicPostbackDetails.objects.create(user=user_info, device_id=device_id,
                                                                   device_type=device_type, event_id=event_id,
                                                                   rewards=rewards)
        coins_source = "supersonic_coins"
        updateVideoDevice(device_id, coins_source)
        user_video_count = updateVideoUser(user_info, coins_source)
    	e=str(event_id)
    	r = '%s:%s' % (e, "OK")
    	return HttpResponse(r)

def video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed):
    user_id = user_info.id
    coins_details = reward_coins(email, source, user_info, device_type, payout)
    try:
        referral_tracking(user_id,payout)
    except:
        pass
    video_details.cycles_completed += cycles_completed
    video_details.yoo_bux += coins_details['coins']
    video_details.dollar_amount += coins_details['dollar_amount']
    video_details.save()

def maintain_video_rewarding(current_video_count,current_bannerAd_count,video_details, email, user_info, device_type):
    payout = 1
    cycles_completed = 1
    #video_exchange_rate = 15
    source = "Commercial_ads"
    code = "video_channels"
    video_params_info = VideoParams.objects.first()#get(id=1)
    video_exchange_rate = video_params_info.video_exchange_rate
    bannerAd_exchange_rate_per_video_cycle = video_params_info.bannerAd_exchange_rate_per_video_cycle
    bannerAd_exchange_rate =  video_params_info.bannerAd_exchange_rate
    if current_video_count == video_exchange_rate:
        video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed)
        video_details.video_balance = 0
    elif current_video_count > video_exchange_rate:
        video_details.video_balance = current_video_count - video_exchange_rate
        video_details.video_balance = (current_video_count)% video_exchange_rate
        cycles_completed = (current_video_count)/ video_exchange_rate
        payout = cycles_completed
        video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed)
    elif current_video_count < video_exchange_rate:
        video_details.video_balance = current_video_count
        video_details.save()
    
    banner_cycle_count = current_bannerAd_count * bannerAd_exchange_rate_per_video_cycle 
    if banner_cycle_count == bannerAd_exchange_rate:
        video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed)
        video_details.bannerAd_balance =0
    elif banner_cycle_count > bannerAd_exchange_rate:
        video_details.bannerAd_balance = ((banner_cycle_count)% bannerAd_exchange_rate)*10
	video_details.bannerAd_balance = int(round(video_details.bannerAd_balance,2))
        cycles_completed = int((banner_cycle_count)/ bannerAd_exchange_rate)
        payout = cycles_completed
        video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed)
    elif banner_cycle_count < bannerAd_exchange_rate:
        bannerAd_exchange_rate_vc = (bannerAd_exchange_rate_per_video_cycle )*100
        video_details.bannerAd_balance = (banner_cycle_count)*bannerAd_exchange_rate_vc
        video_details.save()
        video_balance_count = video_details.video_balance
        total_count = video_balance_count + banner_cycle_count
        if total_count > video_exchange_rate:
	    balance_left=((total_count*10 - video_exchange_rate*10))
            video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed)
            balance_left=int(balance_left)
            video_balance_left = balance_left/10
            bannerAd_balance_left = balance_left%10
            video_details.bannerAd_balance = bannerAd_balance_left
            video_details.video_balance = video_balance_left
            video_details.save()
        elif total_count == video_exchange_rate:
            video_banner_coins_reward(email, source, user_info, device_type, payout,video_details,cycles_completed)
            video_details.video_balance = 0
            video_details.bannerAd_balance =0
    video_details.save()

class CommercialVideoRewardsInfo(View):
    @rest
    @Authenticate()
    #@check_suspicious_user
    def post(self,request):
        device_type = request.META['HTTP_YOO_DEVICE_TYPE']
        app_version = request.META["HTTP_YOO_APP_VERSION"]
        email = request.META['HTTP_YOO_EMAIL_ID']
        android_version = ["1.0","1.1"]
        # if (device_type == "ANDROID" and app_version in android_version):
        #     decrypted_data = androidDecryptionsecurity(request.body)
        #     data = json.loads(decrypted_data)
        # else:
        #     data = json.loads(request.body)
        #     raise exceptions.WebServiceException("Please update your app to continue earnings")
        data = json.loads(request.body)
        user_info = YooLottoUser.objects.get(email = email)
        now = datetime.date.today()
        message = None
        video_count = 0
        banner_ad_count = 0
        if device_type == "IPHONE" and app_version in iphone_version:
            for key in data.keys():
                print key
                for provider in data[key]:
                    print provider
                    for provider_key in provider.keys():
                        
                        for val in provider[provider_key]:
                            print val
                            mediator = val['name']
                            count = int(val['count'])
                            provider = provider_key
                            if key == "video_provider_list":
                                video_provider_obj = VideoProvider.objects.get(video_provider_name__icontains = provider)
                                try:
                                    video_info,created = VideoDetails.objects.get_or_create(user= user_info,video_provider= video_provider_obj,video_provider_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                except:
                                    video_info = VideoDetails.objects.filter(user= user_info,video_provider= video_provider_obj,video_provider_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                    video_info.video_count = video_info.video_count + count
                                    video_info.save()
                                    video_count += count
                            elif key == "banner_provider_list":
                                bannerAd_provider = BannerAdProvider.objects.get(bannerAd_provider_name__icontains = provider)
                                banner_info, created = BannersAdDetails.objects.get_or_create(user= user_info,banner_ad_provider= bannerAd_provider,banner_ad_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                banner_info.banner_ad_count = banner_info.banner_ad_count + count
                                banner_info.save()
                                banner_ad_count += count
            video_details,created = CommercialExtendedVideoDetails.objects.get_or_create(user = user_info)
            video_details.extended_video_total_count += video_count
            video_details.banner_ad_count += banner_ad_count
            video_details.save()
            user_video_details,created = CommercialVideoRewardsDetails.objects.get_or_create(user = user_info,added_at = now)
            user_video_details.extended_video_count += video_count
            user_video_details.save()
            current_video_count = video_details.video_balance + video_count
            current_bannerAd_count = video_details.bannerAd_balance +banner_ad_count
            maintain_video_rewarding(current_video_count,current_bannerAd_count,video_details, email, user_info, device_type)
            email_coins = EmailCoins.objects.get(email= email)
        else:
            for key in data.keys():
                for provider in data[key]:
                    for provider_key in provider.keys():
                        for val in provider[provider_key]:
                            mediator = val['name']
                            count = int(val['count'])
                            provider = provider_key
                            if key == "videogh_imprsn_listlkh":
                                video_provider_obj = VideoProvider.objects.get(video_provider_name__icontains = provider)
                                try:
                                    video_info,created = VideoDetails.objects.get_or_create(user= user_info,video_provider= video_provider_obj,video_provider_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                except:
                                    video_info = VideoDetails.objects.filter(user= user_info,video_provider= video_provider_obj,video_provider_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                    video_info.video_count = video_info.video_count + count
                                    video_info.save()
                                    video_count += count
                            elif key == "bannergh_imprsn_listqwert":
                                bannerAd_provider = BannerAdProvider.objects.get(bannerAd_provider_name__icontains = provider)
                                banner_info, created = BannersAdDetails.objects.get_or_create(user= user_info,banner_ad_provider= bannerAd_provider,banner_ad_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                banner_info.banner_ad_count = banner_info.banner_ad_count + count
                                banner_info.save()
                                banner_ad_count += count
                            elif key == "interstitialrgh_imprsn_listqwert":
                                interstitalAd_provider = InterestitalAdProvider.objects.get(interestialAd_provider_name__icontains = provider)
                                interstital_info, created = InterestitalAdDetails.objects.get_or_create(user= user_info,interestialAd_provider= interstitalAd_provider,interestialAd_mediator=mediator,added_at = now,device_type= device_type,app_version=app_version)
                                interstital_info.interestialAd_count = interstital_info.interestialAd_count + count
                                interstital_info.save()
                                banner_ad_count += count
            video_details,created = CommercialExtendedVideoDetails.objects.get_or_create(user = user_info)
            video_details.extended_video_total_count += video_count
            video_details.banner_ad_count += banner_ad_count
            video_details.save()
            user_video_details,created = CommercialVideoRewardsDetails.objects.get_or_create(user = user_info,added_at = now)
            user_video_details.extended_video_count += video_count
            user_video_details.save()
            current_video_count = video_details.video_balance + video_count
            current_bannerAd_count = video_details.bannerAd_balance +banner_ad_count
            maintain_video_rewarding(current_video_count,current_bannerAd_count,video_details, email, user_info, device_type)
            email_coins = EmailCoins.objects.get(email= email)            
            return{"coins":email_coins.coins, "message": message}

class AppNextInfo(View):
    @rest
    def get(self,request):
        print "in aerserv post"
        client_id = request.GET.get("user_id")
        amount = request.GET.get("amount_rewarded")
        user_details = client_id.split("_")
        user_id = user_details[0]
        device_type = user_details[1]
        device_id = user_details[2]
        user_info = YooLottoUser.objects.get(id=user_id)
        appnext_info = AppNextDetails.objects.create(user=user_info, client_id=client_id, amount_rewarded=amount,
                                                              device_id=device_id, device_type=device_type)
        appnext_info.save()
        return {"success": True}
