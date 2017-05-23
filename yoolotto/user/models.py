import uuid
from django.db import models
from yoolotto.coin.models import CoinWallet
from django.contrib.auth.models import User

class YooLottoUser(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True, unique=True)
    #email_source = models.CharField(max_length=255,null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    referral = models.CharField(max_length=64, null=True, blank=True)
    identifier = models.CharField(max_length=32, null=True, blank=True, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    device_coins_moved = models.BooleanField(default=False)
    add_initial_coins = models.BooleanField(default=0)
    not_referred = models.BooleanField(default=1)
    is_blocked = models.BooleanField(default=False)
    
    def get_wallet(self):
        try:
            return self.wallet
        except CoinWallet.DoesNotExist:
            self.wallet = CoinWallet(user=self)
            self.wallet.save()
            
        return self.wallet
    
    def get_identifier(self):
        if not self.identifier:
            self.identifier = uuid.uuid4().hex
            self.save()
            
        return self.identifier
    
    def __unicode__(self):
        return "%s:%s" % (self.email, self.pk)
    
    class Meta:
        db_table = u"user"

class UserDeviceDetails(models.Model):
    user = models.ForeignKey(YooLottoUser, related_name="user_devices")
    
    device_type = models.CharField(max_length=64, default="UNKNOWN")
    device_id = models.CharField(max_length=128,unique=True)
    
    # Push Notification Token
    device_token = models.CharField(max_length=192, null=True, blank=True, db_index=True)
    
    app_version = models.CharField(max_length=32, null=True, blank=True)
    os_version = models.CharField(max_length=32, null=True, blank=True)
    not_referred = models.BooleanField(default=0)
    advertiser_id = models.CharField(max_length=250,null=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    def is_ios(self):
        return True if self.device_type in ["IPHONE", "IPAD", "IPOD"] else False
    
    def is_android(self):
        return True if self.device_type in ["ANDROID"] else False
    
    def __unicode__(self):
        return "%s:%s" % (self.pk, self.device_id)
    
    class Meta:
        db_table = u"user_device_details"
        
class UserDetails(models.Model):
        user = models.ForeignKey(YooLottoUser, related_name="details")
        phone = models.CharField(max_length=20,null=True, blank=True)
        address = models.CharField(max_length=255,null=True, blank=True)
        
        class Meta:
            db_table = u"user_details"
            
class UserClientLogin(models.Model):
        device = models.CharField(max_length=50)
        client_login = models.CharField(max_length=255,null=True, blank=True)
        #email_source = models.CharField(max_length=255,null=True, blank=True)
        
        class Meta:
            db_table = u"user_client_login"
            
class UserCoinsDetails(models.Model):
    email = models.CharField(max_length=255,null=True, blank=True)
    total_coins = models.IntegerField(default=0)
    user_coins = models.IntegerField(default=0)
    
    class Meta:
            db_table = u"user_coins_details"
            
class PasswordReset(models.Model):
    email = models.CharField(max_length=255,null=True, blank=True)
    code = models.IntegerField(max_length= 10)
    reset = models.BooleanField()
    
    class Meta:
            db_table = u"password_reset"
        
class UserToken(models.Model):
    user = models.ForeignKey(YooLottoUser, related_name="tokens")
    name = models.CharField(max_length=32)
    token = models.TextField()
    
    class Meta:
        db_table = u"user_tokens"
    
class UserPreference(models.Model):
    user = models.OneToOneField(YooLottoUser, related_name="preferences")
    
    jackpot_drawing = models.BooleanField(default=True)
    jackpot_frenzy = models.BooleanField(default=True)
    
    newsletter = models.BooleanField(default=False)
    
    class Meta:
        db_table = u"user_preference"

class Device(models.Model):
    user = models.ForeignKey(YooLottoUser, related_name="devices")
    
    device_type = models.CharField(max_length=64, default="UNKNOWN")
    device_id = models.CharField(max_length=128)
    
    # Push Notification Token
    device_token = models.CharField(max_length=192, null=True, blank=True, db_index=True)
    
    app_version = models.CharField(max_length=32, null=True, blank=True)
    os_version = models.CharField(max_length=32, null=True, blank=True)
    
    added_at = models.DateTimeField(auto_now_add=True)
    
    def is_ios(self):
        return True if self.device_type in ["IPHONE", "IPAD", "IPOD"] else False
    
    def is_android(self):
        return True if self.device_type in ["ANDROID"] else False
    
    def __unicode__(self):
        return "%s:%s" % (self.pk, self.device_id)
    
    class Meta:
        unique_together = ('user', 'device_id')
        db_table = u"user_device"

class FbDetails(models.Model):
    fb_id = models.CharField(max_length=32)
    fb_email = models.CharField(max_length=32)

    class Meta:
        db_table = u"fb_details"

class ReferralCoinsConfiguration(models.Model):
    referring_coins = models.FloatField(default=0)
    referred_coins = models.FloatField(default=0)
    referral_coins_time_limit = models.IntegerField(default=0)
    referring_coins_percentage = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u"referral_coins_configuration"

class ReferralUserInfo(models.Model):
    referring_user = models.ForeignKey(YooLottoUser,related_name="referringUser")
    referred_user = models.ForeignKey(YooLottoUser,related_name="referredUser")
    referral_code = models.CharField(max_length=50,null=True, blank=True)
    referring_user_coins = models.FloatField(default=0)
    referred_user_coins = models.FloatField(default=0)
    total_coins = models.FloatField(default=0)
    balance_coins = models.FloatField(default=0)
    referring_yoobux_rewarded = models.FloatField(default=0)
    referred_yoobux_rewarded = models.FloatField(default=0)
    referred_user_device_id = models.CharField(max_length=250,null=True, blank=True)
    added_at =models.DateField(auto_now_add=True)

    class Meta:
        db_table =u"referral_user_info"

###############################################################################################
################## Models below are to identify suspesious user  ##############################
class ReasonToBlock(models.Model):
    reason=models.CharField(max_length=200)
    created_date=models.DateTimeField(auto_now =True)


    class Meta:
        db_table = u"reason_to_block"

class ReasonToUnBlock(models.Model):
    reason=models.CharField(max_length=200)
    created_date=models.DateTimeField(auto_now =True)


    class Meta:
        db_table = u"reason_to_unblock"


class VideoBanerLengthDetails(models.Model):
    max_length_video_in_seconds = models.IntegerField()
    min_length_video_in_seconds = models.IntegerField()
    max_length_banner_in_seconds = models.IntegerField()
    min_length_banner_in_seconds = models.IntegerField()
    created_date = models.DateTimeField(auto_now = True)
    created_by = models.ForeignKey(User)
    is_active= models.BooleanField(default=True)

    # def save(self,*args, **kwargs):
    #     if VideoBanerLengthDetails.objects.exists():
    #         raise ObjectLimitExceedException("Model Does Not Allow To Create More Than One Object")
    #     else:
    #         super(VideoBanerLengthDetails,self).save(self,*args, **kwargs)    

    class Meta:
        db_table = u"video_baner_length_details"


class UserDeviceStatus(models.Model):
    user = models.ForeignKey(YooLottoUser,related_name="user_devicestatus")
    device_id = models.CharField(null=False,blank=False,max_length=200)
    is_blocked = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now =True)
    reason_to_block = models.ForeignKey(ReasonToBlock,null=True)
    last_blocked_date = models.DateTimeField(null=True)
    last_blocked_by = models.ForeignKey(User,null=True,related_name="adminuser_blocked_device")
    reason_to_unblock = models.ForeignKey(ReasonToUnBlock,null=True)
    last_unblocked_date = models.DateTimeField(null=True)
    last_unblocked_by = models.ForeignKey(User,null=True,related_name="adminuser_unblocked_device")
    no_times_update = models.IntegerField(default=0)


    class Meta:
        db_table = u"user_device_status"
        unique_together = (("user", "device_id"),)


class IPStatus(models.Model):
    ip_address = models.CharField(unique=True,null=False,blank=False,max_length=30)
    is_blocked = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    reason_to_block = models.ForeignKey(ReasonToBlock,null=True,blank=True)
    last_blocked_date = models.DateTimeField(null=True,blank=True)
    last_blocked_by = models.ForeignKey(User,null=True,related_name="adminuser_blocked_IP")
    reason_to_unblock =models.ForeignKey(ReasonToUnBlock,null=True,blank=True)
    last_unblocked_date = models.DateTimeField(null=True,blank=True)
    last_unblocked_by=models.ForeignKey(User,null=True,blank=True,related_name="adminuser_unblocked_IP")
    no_times_update=models.IntegerField(default=0)


    class Meta:
        db_table= u"ip_status"



class UserDeviceImpression(models.Model):
    user_device = models.ForeignKey(UserDeviceStatus)
    user_ip = models.CharField(max_length=30)
    #impression= JSONField()
    total_video_count = models.IntegerField()
    total_banner_count = models.IntegerField()
    list_of_providers = models.CharField(max_length=225)
    created_date = models.DateTimeField(auto_now=True)


    class Meta:
        db_table=u"user_device_impression"



class SuspectedUser(models.Model):
    user_device = models.ForeignKey(UserDeviceStatus)
    reason = models.CharField(max_length=200)
    impression_ref = models.ForeignKey(UserDeviceImpression, null=True)
    created_date = models.DateTimeField(auto_now=True)

    def user(self):
        return str(self.user_device.user.email)+':'+ str(self.user_device.user.id)

    def device_id(self):
        return self.user_device.device_id

    def video_count_requested(self):
        return self.impression_ref.total_video_count

    def banner_count_requested(self):
        return self.impression_ref.total_banner_count     

    def providers(self):
        return self.impression_ref.list_of_providers       

    def user_ip(self):
        return self.impression_ref.user_ip     

    class Meta:
        db_table=u"suspected_user"

#####################end  of models to identify suspesious user  ##############################
#########################################################################################
