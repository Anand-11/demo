import time
import json
import logging
import traceback
import hashlib

from yoolotto.user.cipher import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse
from datetime import datetime
from yoolotto.user.models import UserDeviceDetails, YooLottoUser , SuspectedUser, UserDeviceImpression, IPStatus, UserDeviceStatus, \
    VideoBanerLengthDetails, ReasonToUnBlock, ReasonToBlock
from yoolotto.second_chance.models import VideoProvider, BannerAdProvider

from yoolotto.rest.exceptions import WebServiceException, WebServiceObjectDoesNotExist, \
    WebServiceAuthenticationFailed
from yoolotto.rest.error import format_error

from yoolotto.user.models import UserDeviceDetails, YooLottoUser
from yoolotto.coin.models import DeviceCoins

class Authenticate(object):
    
    INVALID_IOS7_DEVICE_ID = "fd31e787d5d187c079c924883431093a"
            
    def __init__(self, create=True):
        self._create = create
        
    def __call__(self, fn):
        def wrapped(*args, **kwargs):
            request = args[1]
            if request.META["HTTP_YOO_APP_VERSION"] >= "6.0":
                
                if not isinstance(request, WSGIRequest):
                    raise RuntimeError("Invalid Request Object")
                
                if "HTTP_YOO_DEVICE_ID" not in request.META:
                    raise WebServiceAuthenticationFailed()
                #hashstring = hashlib.sha1("@#!" + request.META['HTTP_YOO_EMAIL_ID'] + "yoolottospa").hexdigest()
                #print type(request.META["HTTP_YOO_AUTH_TOKEN"])
                #print type(hashstring)
                #if hashstring != request.META["HTTP_YOO_AUTH_TOKEN"]:
                #    raise WebServiceAuthenticationFailed()
                required_user = YooLottoUser.objects.get(email = request.META['HTTP_YOO_EMAIL_ID'])
                request.yoo["new_version"] = False
                request.yoo["user"] = required_user
                enum_old_version = {"IPHONE":3.0,"ANDROID":3.6}
                old_version = enum_old_version[request.META["HTTP_YOO_DEVICE_TYPE"]]
                
                if str(request.META["HTTP_YOO_APP_VERSION"]) > str(old_version):
                    request.yoo["new_version"] = True
                print "the user is ", request.yoo["user"].id        
                try:
                    print request.yoo["user"]
                    device = UserDeviceDetails.objects.get(device_id=request.META["HTTP_YOO_DEVICE_ID"])
                    device.user = request.yoo["user"]
                    device.save()
                except:
                    #time.sleep(0.05)
                    try:
                        device,created = UserDeviceDetails.objects.get_or_create(device_id=request.META["HTTP_YOO_DEVICE_ID"], user = request.yoo["user"])[0]
                    except:
                        device = UserDeviceDetails.objects.filter(device_id=request.META["HTTP_YOO_DEVICE_ID"], user = request.yoo["user"])[0]
                device.device_type = request.META.get("HTTP_YOO_DEVICE_TYPE", None)
                device.app_version = request.META.get("HTTP_YOO_APP_VERSION", None)
                device.os_version = request.META.get("HTTP_YOO_OS_VERSION", None)
                
                if not device.device_type:
                    device.device_type = "UNKNOWN"
                        
                request.yoo["device"] = device
                request.yoo["auth"]["success"] = True
                device.save()
                            
                return fn(*args, **kwargs)
            else:
                if not isinstance(request, WSGIRequest):
                    raise RuntimeError("Invalid Request Object")
                
                if "HTTP_YOO_DEVICE_ID" not in request.META:
                    raise WebServiceAuthenticationFailed()
                
                if request.META["HTTP_YOO_DEVICE_ID"] == self.INVALID_IOS7_DEVICE_ID:
                    request.yoo["device"] = None
                    request.yoo["user"] = None
                    request.yoo["auth"]["success"] = False
                    request.yoo["auth"]["__internal__reject__"] = True
                    
                    return fn(*args, **kwargs)

                request.yoo["new_version"] = False

                enum_old_version = {"IPHONE":3.0,"ANDROID":3.6}
                old_version = enum_old_version[request.META["HTTP_YOO_DEVICE_TYPE"]]
                
                if str(request.META["HTTP_YOO_APP_VERSION"]) > str(old_version):
                    request.yoo["new_version"] = True
                        
                try:
                    device =UserDeviceDetails.objects.filter(device_id=request.META["HTTP_YOO_DEVICE_ID"])[0]               
                except:
                    if not self._create:
                        raise WebServiceAuthenticationFailed()
                    else:
                        user = YooLottoUser()
                        user.save()
                        
                        device = UserDeviceDetails(user=user, device_id=request.META["HTTP_YOO_DEVICE_ID"])
                
                device.device_type = request.META.get("HTTP_YOO_DEVICE_TYPE", None)
                device.app_version = request.META.get("HTTP_YOO_APP_VERSION", None)
                device.os_version = request.META.get("HTTP_YOO_OS_VERSION", None)
                
                if not device.device_type:
                    device.device_type = "UNKNOWN"
                
                try:
                    device.save()
                except IntegrityError:
                    try:
                        time.sleep(0.05)
                        _device = UserDeviceDetails.objects.get(device_id=request.META["HTTP_YOO_DEVICE_ID"])
                    except UserDeviceDetails.DoesNotExist:
                        device.save()
                    else:
                        device = _device
                        
                request.yoo["device"] = device
                request.yoo["user"] = device.user
                request.yoo["auth"]["success"] = True
                            
                return fn(*args, **kwargs)

        return wrapped

logger = logging.getLogger("yoolotto.uncaught")


def rest(fn):
    def wrapped(*args, **kwargs):
        try:
            request = args[1]
            
            if not hasattr(request, "yoo"):
                request.yoo = {
                    "user": None,
                    "auth": {
                        "success": False,
                        "required": False
                    }
                }
            
            result = fn(*args, **kwargs)
        except WebServiceException as e:
            return e.response()
        except ObjectDoesNotExist as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            if settings.DEBUG:
                _e = WebServiceObjectDoesNotExist(e.message)
            else:
                _e = WebServiceObjectDoesNotExist("ObjectDoesNotExist")
            return _e.response()
        except Exception as e:
            _err = ""
            
            try:
                _err = format_error(request, e)
            except:
                _err = str(e)
            
            try:    
                logger.error(_err)
            except:
                _err += "\n !COULD NOT LOG EXCEPTION LOCALLY!"
            
            from yoolotto.lottery.game.base import LotteryPlayInvalidException
            
            '''if settings.ERROR_NOTIFICATION and not isinstance(e, LotteryPlayInvalidException):
                try:
                    from yoolotto.communication.email import EmailSender
                    email = EmailSender(settings.ERROR_EMAIL, "YL Exception: " + str(e), 
                        text=_err)
                    email.send()
                except:
                    logger.error("\n\nERROR HANDLING EXCEPTION")
                    logger.error(traceback.format_exc() + "\n\n")'''
            
            if hasattr(e, "representation"):
                return e.representation()
            
            raise
        
        if not isinstance(result, HttpResponse):
            result = json.dumps(result)
            result = HttpResponse(result, content_type="application/json")
        return result
    return wrapped

def find_total_video_count(data):
    video_count = 0
    banner_ad_count = 0
    providers_list = []
    for key in data.keys():
        for provider in data[key]:
            for provider_key in provider.keys():
                for val in provider[provider_key]:
                    mediator = val['name']
                    count = int(val['count'])
                    provider = provider_key
                    if key == "video_provider_list" or key == "videogh_imprsn_listlkh":
                        video_count += count
                        if not provider in providers_list:
                            providers_list.append(provider)

                    elif key == "banner_provider_list" or key == "bannergh_imprsn_listqwert" or key == "interstitialrgh_imprsn_listqwert":
                        banner_ad_count += count
                        if not provider in providers_list:
                            providers_list.append(provider)

    return {'video_count':video_count,'banner_ad_count':banner_ad_count,'providers_list':providers_list}   
def get_client_ip(request):
    
    ip = request.META.get('REMOTE_ADDR')
        
       
    return ip

def check_suspicious_user(function):
    def wrap(*args, **kwargs):
        request = args[1]
        client_ip = get_client_ip(request)
        client_ip_status,ip_created = IPStatus.objects.get_or_create(ip_address = client_ip)
        if not client_ip_status.is_blocked:
            device_type = request.META['HTTP_YOO_DEVICE_TYPE']
            try:
                user = YooLottoUser.objects.get(email=request.META['HTTP_YOO_EMAIL_ID'])
            except:
                return function(*args, **kwargs)
            if not user.is_blocked:
                if device_type == "IPHONE":
                    decrypted_data = iOSdecryptionsecurity(request.body)
                    data = json.loads(decrypted_data)
                elif device_type == "ANDROID" :
		    data = json.loads(request.body)
                    #decrypted_data = androidDecryptionsecurity(request.body)
                    #data = json.loads(decrypted_data)
                else:
                    data = json.loads(request.body)
                count_dict = find_total_video_count(data)
                video_count = count_dict['video_count']
                banner_ad_count = count_dict['banner_ad_count']
                providers_list = count_dict['providers_list']
                try:
                    user_device_status,device_created = UserDeviceStatus.objects.get_or_create(user=user,device_id = request.META["HTTP_YOO_DEVICE_ID"],is_blocked = False)
                except:
                    raise UserBlockedException("User's device is blocked") 
                black_listed_providers = list(VideoProvider.objects.filter(active=False).values_list('video_provider_name',flat=True)) + list(BannerAdProvider.objects.filter(active=False).values_list('bannerAd_provider_name',flat=True))
                video_length_obj = VideoBanerLengthDetails.objects.first()  
                eqivalent_time_estimate =  video_count*video_length_obj.min_length_video_in_seconds + banner_ad_count*video_length_obj.min_length_banner_in_seconds
                new_suspected_user = None
                if not device_created:
                    if not user_device_status.is_blocked:
                        user_last_impresssion = UserDeviceImpression.objects.filter(user_device=user_device_status)
                        if user_last_impresssion:
                            user_last_impresssion=user_last_impresssion.latest('created_date')
                            reason_for_suspision = ''
                            blaclisted_request = False
                            for provider in black_listed_providers:
                                if provider in providers_list:
                                    blaclisted_request = True
                                    break
                            if user_last_impresssion:
                                reason_for_suspision = ''
                                if (datetime.now() - user_last_impresssion.created_date.replace(tzinfo=None)).total_seconds() < eqivalent_time_estimate and not blaclisted_request:
                                    reason_for_suspision = "Large number of video and banner count sent by user"

                                elif blaclisted_request and not (datetime.now() - user_last_impresssion.created_date).total_seconds() < eqivalent_time_estimate:
                                    reason_for_suspision = "request from black listed provider"
                                elif blaclisted_request and (datetime.now() - user_last_impresssion.created_date).total_seconds() < eqivalent_time_estimate:
                                    reason_for_suspision = "Large number of video and banner count and request from black listed provider both"       
                                
                                if reason_for_suspision:    
                                    new_suspected_user = SuspectedUser.objects.create(user_device = user_device_status,reason = reason_for_suspision)
                         
                    else:  
                        raise UserBlockedException("User's device has been blocked")
                impression_obj = UserDeviceImpression.objects.create(user_device = user_device_status,user_ip = client_ip,
                total_video_count=video_count,total_banner_count=banner_ad_count,list_of_providers=providers_list)
                if new_suspected_user:
                    new_suspected_user.impression_ref = impression_obj 
                    new_suspected_user.save()             
                return function(*args, **kwargs)
            else:
                raise UserBlockedException("User's email is blocked")   
            
        else:
            raise UserBlockedException("User's IP has been blocked")      
    return wrap



