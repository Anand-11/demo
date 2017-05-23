from yoolotto.second_chance.models import *
from yoolotto.user.models import *
from yoolotto.coin.models import *
from yoolotto.rest import exceptions

def assign_referral_coins(code,device_id,email):
    referred_user_device_id = device_id
    referred_user_info = YooLottoUser.objects.get(email =email)
    print referred_user_info.email
    if referred_user_info.referral == code:
	return False
    referring_user_info = YooLottoUser.objects.get(referral =code)
    print referring_user_info.email
    referral_config = ReferralCoinsConfiguration.objects.get(id=1)
    referring_user_coins = referral_config.referring_coins
    referred_user_coins = referral_config.referred_coins
    try:
        _referred_user_info = ReferralUserInfo.objects.get(referred_user=referred_user_info)
        referred = 1
    except:
        _referred_user_info = ReferralUserInfo.objects.create(referred_user=referred_user_info,referring_user_id=referring_user_info.id)
        referred = 0
    try:
	referred_user_device_info = ReferralUserInfo.objects.filter(referred_user_device_id = referred_user_device_id)[0]
	referring = 1
    except:
	if referred == 1:
	    referring = 1
	else:
	    _referred_user_info.referred_user_device_id = referred_user_device_id
	    _referred_user_info.save()
	    referring = 0
    #dt = {"referred":referred,"referring":referring,"abc":referred_user_info.not_referred,"device_id":device_id}
    device_details = UserDeviceDetails.objects.get(device_id = device_id)
    '''import logging
    LOG_FILENAME = 'logging_ample.out'
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
    logging.debug(dt)'''
    if (referred == 0 and referring == 0 and referred_user_info.not_referred == 0 and device_details.not_referred == 0):
	_referred_user_info.referral_code = code
        _referred_user_info.referred_user_coins = referred_user_coins
        _referred_user_info.referring_user_coins = referring_user_coins
        _referred_user_info.referred_user_device_id = referred_user_device_id
        _referred_user_info.save()
	referred_user_info.not_referred = 1
	referred_user_info.save()
	device_details.not_referred = 1
        device_details.save()
        referred_email_info = EmailCoins.objects.get(email = referred_user_info.email)
        referred_email_info.coins = referred_email_info.coins + referred_user_coins
	dollar_amount = float(referred_user_coins)/100
        referred_email_info.dollar_amount = float(referred_email_info.dollar_amount) + dollar_amount
        referred_email_info.save()
        source = "referred_user_coins"
        coin_source = CoinSource.objects.get(source_name = source)
        referred_user_history = UserCoinsHistory(user = referred_user_info,credit_coins = referred_user_coins ,source = coin_source,credit_amount = dollar_amount,device_type = None,net_amount = referred_email_info.dollar_amount,net_coins = referred_email_info.coins)
        referred_user_history.save()

     
