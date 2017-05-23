from yoolotto.second_chance.models import UserCoinsHistory,CoinSource
from yoolotto.coin.models import EmailCoins
from yoolotto.user.models import YooLottoUser
from yoolotto.user.models import Device
from yoolotto.communication.apn import APNSender
from yoolotto.communication.gcm_sender import GCMSender
import time

def send_rewarded_notification(user_id,coins,code):
    log = ''
    user_devices = Device.objects.filter(user_id = user_id)
    text ="Congratulations!!! You got %s YooBux"%(coins)
    print text
    device_token_dic_ios =[]
    device_token_dic_android = []
    for device in user_devices:
        if device.device_token is not None:
	    if device.is_ios():
		if device.device_token not in device_token_dic_ios:
		    device_token_dic_ios.append(device.device_token)
		else:
		    pass
	    elif device.is_android():
		if device.device_token not in device_token_dic_android:
		    device_token_dic_android.append(device.device_token)
		else:
		    pass
    for token in set(device_token_dic_ios):
        apn = APNSender(token, text=text,custom={"code": code,"sound":"earned yoocoins.aiff"})
        apn.send()
    for token in set(device_token_dic_android):
        gcm = GCMSender(to=[token], data={"text": text,"code": "rewarded"})
        gcm.send()
        log += "\nGCM Outbound: %s" % token

def send_offer_download_notification(user_id):
        secs = 350
        time.sleep(secs)
        log = ''
        user_devices = Device.objects.filter(user_id = user_id)
        text ="Almost there, complete tasks & get cash. Click now."
        device_token_dic_ios =[]
        device_token_dic_android = []
        for device in user_devices:
                if device.device_token is not None:
                        if device.is_ios():
                                if device.device_token not in device_token_dic_ios:
                                        device_token_dic_ios.append(device.device_token)
                                else:
                                        pass
                        elif device.is_android():
                                if device.device_token not in device_token_dic_android:
                                        device_token_dic_android.append(device.device_token)
                                else:
                                        pass
        for token in set(device_token_dic_ios):
                print token
                apn = APNSender(token, text=text,custom={"code": "offer_download"})
                apn.send()
                print "notification successful"
                log += "\nAPN Outbound: %s" % token
        for token in set(device_token_dic_android):
                gcm = GCMSender(to=[token], data={"text": text,"code": "offer_download"})
                gcm.send()
                log += "\nGCM Outbound: %s" % token

