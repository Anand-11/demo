import datetime
import bisect
import random
import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from yoolotto.util.time import format_datetime
from django.conf import settings
from django.core.files import File
import urllib

#InterestitalAd provider avaliable in our system
class InterestitalAdProvider(models.Model):
    priority_list_id = models.IntegerField(unique=True)
    interestialAd_provider_name = models.CharField(max_length=200,unique=True)
    active = models.BooleanField(default =True)

    class Meta:
        db_table = u"interestialAd_provider"

#to store all interestialAd count details with provider
class InterestitalAdDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    interestialAd_provider = models.ForeignKey("InterestitalAdProvider")
    interestialAd_mediator = models.CharField(max_length=100)
    interestialAd_count = models.IntegerField(default=0)
    device_type = models.CharField(max_length=100)
    app_version= models.CharField(max_length=32, null=True, blank=True)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"interestialAd_details"

class Advertisor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(blank=True,upload_to="static/second_chance/advertisor/", null=True,max_length=500)
    
    def representation(self):

        result = {
            "id": self.pk,
            "name": self.name,
            "image": self.image.name,
        }
               
        return result

    class Meta:
        db_table = u"advertisor"        
    
class AdInventory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    inventory = models.IntegerField(default=0)
    type = models.CharField(max_length=255, choices=(
         ("digital", "digital"),
         ("physical", "physical")
     ),default="physical")
    timer = models.BooleanField()
    time = models.IntegerField(default=0)
    account = models.ForeignKey(Advertisor, related_name="ad_inventory", blank=True, null=True)
    status = models.CharField(max_length=255)
    ad_id = models.CharField(max_length=255)
    coins = models.IntegerField(default=0)
        
    def representation(self):
        result = {
            "id": self.pk,
            "domain": "http://ox-d.yoolotto.com",
        }
        return result

    class Meta:
        db_table = u"ad_inventory"

    def __unicode__(self):
        return self.name
    
class AdIssue(models.Model):
    ad = models.ForeignKey(AdInventory, related_name="ad_inventory", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    device = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20,null=True, blank=True)
    won = models.BooleanField()
    added_at = models.DateTimeField(auto_now_add=True)
       
    def representation(self):
        result = {
            "type": "local",
            "id": self.pk,
            "parent": self.ad.representation(),
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            "added": format_datetime(self.added_at),
        }
        
        return result
    
    class Meta:
        db_table = u"ad_issue"
        
class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
       
    def representation(self):
        result = {
            "id": self.pk,
            "question": self.question,
            "answer": self.answer,
        }
        
        return result
    
    class Meta:
        db_table = u"faq"

        
class FiberCoins(models.Model):
    email = models.CharField(max_length=255)
    rewarded_video = models.FloatField(default=0)
    offer_wall = models.FloatField(default=0)
    class Meta:
        db_table = u"fiber_coins"

class FyberVideoDeviceDetails(models.Model):
    user =  models.ForeignKey("user.YooLottoUser")
    video_count = models.IntegerField(default=0)
    device_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=100)
    added_at = models.DateTimeField()

    class Meta:
        db_table = u"fyber_video_device_details"

class FyberVideoUserDeviceDetails(models.Model):
    user =  models.ForeignKey("user.YooLottoUser")
    user_video_count = models.IntegerField(default=0)
    device_id = models.CharField(max_length=255)
    user_added_at = models.DateTimeField()

    class Meta:
        db_table = u"fyber_video_user_device_details"

class DeviceLoginDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser", related_name="reset_coins_user")
    device = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        db_table = u"device_login_details"

class DwollaUserInfo(models.Model):
    user = models.ForeignKey("user.YooLottoUser", related_name="dwolla_user")
    email = models.CharField(max_length=255)
    dwolla_email = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    dwolla_amount = models.FloatField(default=0)
    last_cashout_amount = models.FloatField(default=0)
    phone = models.BigIntegerField(default=0)
    dwolla_pin = models.IntegerField(default=0)
    total_amount = models.FloatField(default=0)
    isDwollaUser = models.BooleanField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    
    class Meta:
	#unique_together = ('email', 'dwolla_email','isDwollaUser')
        db_table = u"dwolla_user_info"

class DwollaTransactionInfo(models.Model):
    dwolla_detail = models.ForeignKey("second_chance.DwollaUserInfo")
    source = models.CharField(max_length=255)
    source_info = models.CharField(max_length=255)
    amount_requested = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255)

    class Meta:
        db_table = u"dwolla_transaction_info"

class FantasyFAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
       
    def representation(self):
        result = {
            "id": self.pk,
            "question": self.question,
            "answer": self.answer,
        }
        
        return result
    
    class Meta:
        db_table = u"fantasy_faq"


class Events(models.Model):
    data = models.TextField()
    class Meta:
	db_table = u"events"

class EventInfo(models.Model):
    referring_user = models.CharField(max_length=255)
    referred_user = models.CharField(max_length=255)
    event_occured = models.CharField(max_length=255)
    referring_user_coins = models.FloatField(default=0)
    referred_user_coins = models.FloatField(default=0)
    updated_at = models.DateTimeField(blank= True)
    
    class Meta:
        db_table = u"events_info"


class DwollaFAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
       
    def representation(self):
        result = {
            "id": self.pk,
            "question": self.question,
            "answer": self.answer,
        }
        
        return result
    
    class Meta:
        db_table = u"dwolla_faq"

class DwollaUserHistory(models.Model):
    dwolla = models.ForeignKey(DwollaUserInfo, related_name="dwolla_history")
    cashout_amount = models.FloatField(default=0)
    cashout_status = models.BooleanField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u"dwolla_user_history"

class UserCoinsSpendHistory(models.Model):
    user = models.ForeignKey("user.YooLottoUser", related_name="user_coins_spendhistory")
    coins = models.FloatField(default=0)
    source = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = u"user_coins_spend_history"

class UserCoinsEarnHistory(models.Model):
    user = models.ForeignKey("user.YooLottoUser", related_name="user_coins_earnhistory")
    coins = models.FloatField(default=0)
    source = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add = True)
    device_type = models.CharField(max_length=255)

    class Meta:
        db_table = u"user_coins_earn_history"

class UserCoinsResetDateHistory(models.Model):
    user = models.ForeignKey("user.YooLottoUser", related_name="user_coins_resetdate")
    coins = models.FloatField(default=0)
    reset_date = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = u"user_coins_reset_date"

class FantasyLotterySpentHistory(models.Model):
    ticket = models.ForeignKey("lottery.LotteryTicket", related_name="fantasy_ticket__detail")
    user = models.ForeignKey("user.YooLottoUser",related_name="user__details")
    coins = models.FloatField(default = 0)
    added_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length = 255)

    class Meta:
        db_table = u"fantasy_ticket_spent_history"

class AppThisDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="users_details")
    click_id = models.CharField(max_length=200, blank=True, null=True)
    offer_id = models.IntegerField(blank= True)
    device_type = models.CharField(max_length=200, blank=True, null=True)
    offer_name = models.CharField(max_length=200,blank=True,null =True)
    payout = models.DecimalField(max_digits=8,decimal_places=2)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    offer_tagged = models.BooleanField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"appthis_details"

class AppThisFAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

    def representation(self):
        result = {
            "id": self.pk,
            "question": self.question,
            "answer": self.answer,
        }

        return result

    class Meta:
        db_table = u"appthis_faq"


class AppThisInstructions(models.Model):
    instructions = models.TextField()
    faq = models.TextField()

    def representation(self):
        result = {
            "id": self.pk,
            "faq": self.faq,
        }

        return result

    class Meta:
        db_table = u"appthis_instructions"


class ConfigurationSettings(models.Model):
    name = models.CharField(max_length=200,blank=True,null =True)
    value = models.IntegerField(blank= True)

    class Meta:
        db_table = u"config_settings"

class GiftCardCashoutDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="giftcard_user")
    gift_card_name = models.CharField(max_length=200,blank=True,null =True)
    user_redeem_email = models.CharField(max_length=200,blank=True,null =True)
    cashout_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"giftcard_cashout_details"

class CoinSource(models.Model):
    source_name =models.CharField(max_length=200,blank=True,null =True)
    activity_type = models.CharField(max_length=200,blank=True,null =True)
    description = models.CharField(max_length=250,blank=True,null =True)

    class Meta:
        db_table = u"coin_source"

class UserCoinsHistory(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="history_user")
    credit_coins = models.FloatField(default=0)
    debit_coins = models.FloatField(default=0)
    net_coins = models.FloatField(default=0)
    credit_amount = models.FloatField(default=0)
    debit_amount = models.FloatField(default=0)
    net_amount = models.FloatField(default=0)
    source = models.ForeignKey("second_chance.CoinSource",related_name="source_for_coins")
    device_type = models.CharField(max_length=70,blank=True,null =True)
    app_version = models.CharField(max_length=32, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def representation(self):
        result = {
            "earned_coins": self.credit_coins,
            "spend_coins": self.debit_coins,
            "available_balance":self.net_coins,
            "event_details":self.source.description,
            "date":self.added_at.strftime("%Y-%m-%d")}
        
        return result

    class Meta:
        db_table = u"user_history"

class AppThisOfferInfo(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="appthis_user")
    click_id = models.CharField(max_length=200, blank=True, null=True)
    appthis_offer_id = models.CharField(max_length=50,blank=True,null =True)
    appthis_offer_name = models.CharField(max_length=100,blank=True,null =True)
    rewarded = models.BooleanField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    android_package_name = models.CharField(max_length=200,blank=True,null =True)
    installed = models.BooleanField(default=0)
	
    def representation(self):
        result = {
            "android_package_name": self.android_package_name,
            "click_id": self.click_id,}
        
        return result

    class Meta:
        db_table = u"appthis_offers_details"

class TempTable(models.Model):
    user_id = models.IntegerField(blank= True)
    email = models.CharField(max_length=128)
    coins = models.FloatField(default=0)
    #dollar_amount = models.FloatField(default=0)

    class Meta:
        db_table = u"temp_table"

class AppromoterInstallationInfo(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="appromoter_user")
    aff_sub = models.CharField(max_length=200, blank=True, null=True)
    installed = models.BooleanField(default=0)
    android_package_name = models.CharField(max_length=200,blank=True,null =True)
    appromoter_offer_id = models.CharField(max_length=50,blank=True,null =True)
    appromoter_offer_name = models.CharField(max_length=100,blank=True,null =True)
    source = models.CharField(max_length=50, blank=True, null=True)
    rewarded = models.BooleanField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def representation(self):
        result = {
            "android_package_name": self.android_package_name,
            "aff_sub": self.aff_sub,}

        return result


    class Meta:
        db_table = u"appromoter_installation_details"

class AppromoterPostbackDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="appromoter_users_details")
    aff_sub = models.CharField(max_length=200, blank=True, null=True)
    offer_id = models.IntegerField(blank= True)
    source = models.CharField(max_length=50, blank=True, null=True)
    offer_name = models.CharField(max_length=200,blank=True,null =True)
    offer_url_id = models.CharField(max_length=200,blank=True,null =True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    device_brand = models.CharField(max_length=200, blank=True, null=True)
    device_os = models.CharField(max_length=100, blank=True, null=True)
    device_model = models.CharField(max_length=200, blank=True, null=True)
    device_os_version = models.CharField(max_length=150, blank=True, null=True)
    currency = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    payout = models.DecimalField(max_digits=8,decimal_places=2)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    datetime = models.DateTimeField()
    added_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    offer_tagged = models.BooleanField(default=0)

    class Meta:
        db_table = u"appromoter_postback_details"

class KiipUserInfo(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="kiip_user_details")
    content_id = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True)
    signature = models.CharField(max_length=200, blank=True, null=True)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"kiip_details"

class PollFishInfo(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="pollfish_user_details")
    request_uuid = models.CharField(max_length=200, blank=True, null=True)
    cpa = models.FloatField(default=0)
    coins = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    device_id = models.CharField(max_length=200, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"pollfish_details"

class RewardedVideoDeviceDetails(models.Model):
    device_id = models.CharField(max_length=255)
    fyber_video_count = models.IntegerField(default=0)
    adtoapp_video_count = models.IntegerField(default=0)
    nativex_video_count = models.IntegerField(default=0)
    adcolony_video_count = models.IntegerField(default=0)
    hypermx_video_count = models.IntegerField(default=0)
    aersrv_video_count = models.IntegerField(default=0)
    vungle_video_count = models.IntegerField(default=0)
    supersonic_video_count = models.IntegerField(default=0)
    added_at = models.DateField()

    class Meta:
        db_table = u"rewarded_video_device_details"

class RewardedVideoUserDetails(models.Model):
    user =  models.ForeignKey("user.YooLottoUser")
    fyber_video_count = models.IntegerField(default=0)
    adtoapp_video_count = models.IntegerField(default=0)
    nativex_video_count = models.IntegerField(default=0)
    adcolony_video_count = models.IntegerField(default=0)
    hypermx_video_count = models.IntegerField(default=0)
    aersrv_video_count = models.IntegerField(default=0)
    vungle_video_count = models.IntegerField(default=0)
    supersonic_video_count = models.IntegerField(default=0)
    added_at = models.DateField()

    class Meta:
        db_table = u"rewarded_video_user_details"

class NativexPostbackDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser",related_name="nativead_users_details")
    amount = models.FloatField(default=0)
    device_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50,blank=True,null =True)
    publisher_user_id = models.CharField(max_length=250,blank=True,null =True)
    offer_name = models.CharField(max_length=100, blank=True, null=True)
    offer_id = models.IntegerField(default=0)
    publisher_sessionid = models.CharField(max_length=200, blank=True, null=True)
    client_ip = models.CharField(max_length=100, blank=True, null=True)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"native_x_postback_details"

class AdToAppInfo(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    ad_provider = models.CharField(max_length=100)
    currency_value = models.FloatField(default=0)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = u"ad_to_app_info"

class AervservPostbackDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    client_id = models.CharField(max_length=255)
    amount = models.FloatField(default=0)
    device_id = models.CharField(max_length=255,blank=True,null =True)
    device_type = models.CharField(max_length=50,blank=True,null =True)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"aerserv_postback_details"

class SupersonicPostbackDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    device_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    event_id = models.CharField(max_length=255)
    rewards = models.FloatField(default=0)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"supersonic_postback_details"

class CommercialVideoRewardsDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    limited_video_count = models.IntegerField(default=0)
    extended_video_count = models.IntegerField(default=0)
    intermediate_video_count = models.IntegerField(default=0)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"commercial_video_rewards"

class CommercialLimitedVideoDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    limited_video_total_count = models.IntegerField(default=0)
    cycles_completed = models.IntegerField(default=0)
    video_balance = models.IntegerField(default=0)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"commercial_limited_video_details"

class CommercialIntermediateVideoDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    intermediate_video_total_count = models.IntegerField(default=0)
    cycles_completed = models.IntegerField(default=0)
    video_balance = models.IntegerField(default=0)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"commercial_intermediate_video_details"

class AppNextDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    client_id = models.CharField(max_length=100)
    device_id = models.CharField(max_length=255,blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    amount_rewarded = models.FloatField(default=0)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"appnext_details"

class CommercialExtendedVideoDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    extended_video_total_count = models.IntegerField(default=0)
    banner_ad_count = models.IntegerField(default=0)
    cycles_completed = models.IntegerField(default=0)
    video_balance = models.IntegerField(default=0)
    bannerAd_balance = models.IntegerField(default=0)
    yoo_bux = models.FloatField(default=0)
    dollar_amount = models.FloatField(default=0)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"commercial_extended_video_details"

class VideoParams(models.Model):
    video_exchange_rate = models.IntegerField(default=0)
    bannerAd_exchange_rate_per_video_cycle = models.FloatField(default=0)
    bannerAd_exchange_rate = models.IntegerField(default=0)

    class Meta:
        db_table = u"video_params"

class VideoProvider(models.Model):
    priority_list_id = models.IntegerField(unique=True)
    video_provider_name = models.CharField(max_length=200,unique=True)
    active = models.BooleanField(default =True)

    def __unicode__(self):
        return self.video_provider_name


    class Meta:
        db_table = u"video_provider"

class BannerAdProvider(models.Model):
    priority_list_id = models.IntegerField(unique=True)
    bannerAd_provider_name = models.CharField(max_length=200,unique=True)
    active = models.BooleanField(default =True)

    class Meta:
        db_table = u"bannerAd_provider"

class VideoDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    video_provider = models.ForeignKey("VideoProvider")
    video_provider_mediator = models.CharField(max_length=255)
    video_count = models.IntegerField(default=0)
    device_type = models.CharField(max_length=100)
    app_version= models.CharField(max_length=32, null=True, blank=True)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"video_details"

class BannersAdDetails(models.Model):
    user = models.ForeignKey("user.YooLottoUser")
    banner_ad_provider = models.ForeignKey("BannerAdProvider")
    banner_ad_mediator = models.CharField(max_length=100)
    banner_ad_count = models.IntegerField(default=0)
    device_type = models.CharField(max_length=100)
    app_version= models.CharField(max_length=32, null=True, blank=True)
    added_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = u"bannerAd_details"
