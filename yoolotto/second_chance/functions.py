import datetime
from yoolotto.second_chance.models import *
from yoolotto.coin.models import *
from yoolotto.user.models import *

def reward_coins(email,source,user,device_type,payout,exchange_rate=1):
    user_info = user
    email_info =EmailCoins.objects.get(email = email)    
    dollar_exchange_rate=100
    yoo_bux_cal = float(payout)*exchange_rate
    email_info.coins = float(email_info.coins) + float(yoo_bux_cal)
    amount = round((float(yoo_bux_cal)/dollar_exchange_rate),2)
    email_info.dollar_amount = email_info.dollar_amount + amount
    email_info.save()
    source = source
    coin_source = CoinSource.objects.get(source_name = source)
    user_history = UserCoinsHistory(user = user_info,credit_coins = yoo_bux_cal ,source = coin_source,credit_amount = amount,net_amount = email_info.dollar_amount,net_coins = email_info.coins,device_type=device_type)
    user_history.save()
    data = {"coins":float(yoo_bux_cal),"dollar_amount":amount}
    return data

def referral_tracking(user_id,coins):
    referred_user_details =  ReferralUserInfo.objects.get(referred_user=user_id)
    referred_user_details.total_coins = referred_user_details.total_coins + coins
    referred_user_details.balance_coins = referred_user_details.balance_coins + coins
    referred_user_details.save()
    referral_coins_settg = ReferralCoinsConfiguration.objects.get(id=1)
    #todays_date = date.today()
    #time = referred_user_details.added_at + relativedelta(months=+12) 
    if referred_user_details.balance_coins >= referral_coins_settg.referring_coins_percentage:
	yoobux_rewarded = int((referred_user_details.balance_coins)/referral_coins_settg.referring_coins_percentage)
        yoobux_debited = yoobux_rewarded*referral_coins_settg.referring_coins_percentage
        referred_user_details.balance_coins = referred_user_details.balance_coins - yoobux_debited
        referred_user_details.referring_yoobux_rewarded = yoobux_rewarded
        referred_user_details.save()
        email = referred_user_details.referring_user.email
        #email = user_info.email
        user_info = YooLottoUser.objects.get(id = referred_user_details.referring_user.id)
        source = "referral"
        device_type = None
        reward_coins(email,source,user_info,device_type,yoobux_rewarded)

def updateVideoDevice(device_id, coins_source):
    now = datetime.date.today()
    device_info,created = RewardedVideoDeviceDetails.objects.get_or_create(device_id = device_id, added_at=now)
    if coins_source == "fyber":
        device_info.fyber_video_count += 1
    elif coins_source == "adtoapp":
        print "right here"
        device_info.adtoapp_video_count += 1
    elif coins_source == "nativex":
        device_info.nativex_video_count += 1
    elif coins_source == "hypermx":
        device_info.hypermx_video_count += 1
    elif coins_source == "aersrv":
        device_info.aersrv_video_count += 1
    elif coins_source == "vungle":
        device_info.vungle_video_count += 1
    elif coins_source == "adcolony":
        device_info.adcolony_video_count += 1
    elif coins_source == "supersonic_coins":
        device_info.supersonic_video_count += 1
    device_info.save()

def updateVideoUser(user, coins_source):
    now = datetime.date.today()
    user_info,created = RewardedVideoUserDetails.objects.get_or_create(user=user, added_at=now)
    print user_info
    if coins_source == "fyber":
        user_info.fyber_video_count += 1
    elif coins_source == "adtoapp":
        user_info.adtoapp_video_count += 1
    elif coins_source == "nativex":
        user_info.nativex_video_count += 1
    elif coins_source == "hypermx":
        user_info.hypermx_video_count += 1
    elif coins_source == "aersrv":
        user_info.aersrv_video_count += 1
    elif coins_source == "vungle":
        user_info.vungle_video_count += 1
    elif coins_source == "adcolony":
        user_info.adcolony_video_count += 1
    elif coins_source == "supersonic_coins":
        user_info.supersonic_video_count += 1
    user_info.save()

