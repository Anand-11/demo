from django.contrib import admin
from yoolotto.second_chance.models import *
from yoolotto.user.models import *

class FaqAdmin(admin.ModelAdmin):
    """
    displaying the faq page
    """
    
    list_display = ['id','question','answer']
    
admin.site.register(FAQ, FaqAdmin)

class InterestitalAdDetailsAdmin(admin.ModelAdmin):

    list_display = ['user','interestialAd_provider','interestialAd_mediator','interestialAd_count','device_type','app_version','added_at']
    search_fields = ['user__email']

admin.site.register(InterestitalAdDetails, InterestitalAdDetailsAdmin)

class ReferralUserInfoAdmin(admin.ModelAdmin):
    list_display = ['id','referring_user','referred_user','referral_code','referring_user_coins','referred_user_coins','referred_user_device_id','added_at']
    list_per_page = 7

admin.site.register(ReferralUserInfo,ReferralUserInfoAdmin)

class VideoProviderAdmin(admin.ModelAdmin):

    list_display = ['priority_list_id','video_provider_name','active']

admin.site.register(VideoProvider, VideoProviderAdmin)

class BannerAdProviderAdmin(admin.ModelAdmin):

    list_display = ['priority_list_id','bannerAd_provider_name','active']

admin.site.register(BannerAdProvider, BannerAdProviderAdmin)

class VideoDetailsAdmin(admin.ModelAdmin):

    list_display = ['user','video_provider','video_provider_mediator','video_count','device_type','app_version','added_at']
    search_fields = ['user__email']

admin.site.register(VideoDetails, VideoDetailsAdmin)

class BannersAdDetailsAdmin(admin.ModelAdmin):

    list_display = ['user','banner_ad_provider','banner_ad_mediator','banner_ad_count','device_type','app_version','added_at']
    search_fields = ['user__email']

admin.site.register(BannersAdDetails, BannersAdDetailsAdmin)

class FantasyFaqAdmin(admin.ModelAdmin):
    list_display = ['id','question','answer']

class ReferralCoinsConfigurationAdmin(admin.ModelAdmin):
    list_display = ['id','referring_coins','referred_coins','referral_coins_time_limit','referring_coins_percentage']
    list_per_page = 7

class UserDeviceDetailsAdmin(admin.ModelAdmin):
    list_display =['id','user','device_id','device_token','device_type','app_version','os_version','added_at']
    search_fields = ['user__email']
    list_per_page = 7

class DwollaFaqAdmin(admin.ModelAdmin):
    list_display = ['id','question','answer']

class UserHistoryAdmin(admin.ModelAdmin):
    list_display =['id','user','credit_coins','debit_coins','net_coins','credit_amount','debit_amount','net_amount','get_source_name','get_source_description','device_type','app_version','added_at']
    search_fields = ['user__email']
    list_per_page = 7

    def get_source_name(self,obj):
        return obj.source.source_name

    def get_source_description(self,obj):
        return obj.source.description

class FbDetailsAdmin(admin.ModelAdmin):
   list_display=['id','fb_id','fb_email']
   search_fields = ['fb_email']
   list_per_page = 7

class CoinSourceAdmin(admin.ModelAdmin):
   list_display=['id','source_name','activity_type','description']

class CommercialExtendedVideoDetailsAdmin(admin.ModelAdmin):
    list_display = ['user','extended_video_total_count','cycles_completed','video_balance','yoo_bux','dollar_amount']
    search_fields = ['user__email']
    list_per_page = 7

#admin.site.register(FantasyFAQ, FantasyFaqAdmin)
admin.site.register(UserDeviceDetails, UserDeviceDetailsAdmin)
#admin.site.register(AppNextDetails, AppNextDetailsAdmin)
#admin.site.register(CommercialLimitedVideoDetails, CommercialLimitedVideoDetailsAdmin)
admin.site.register(CommercialExtendedVideoDetails, CommercialExtendedVideoDetailsAdmin)
#admin.site.register(CommercialIntermediateVideoDetails, CommercialIntermediateVideoDetailsAdmin)
admin.site.register(DwollaFAQ, DwollaFaqAdmin)
#admin.site.register(AppThisFAQ, AppthisFaqAdmin)
#admin.site.register(AppThisInstructions, AppthisInstructionsFaqAdmin)
#admin.site.register(AppThisDetails, AppThisDetailsAdmin)
#admin.site.register(AppromoterPostbackDetails, AppromoterPostbackDetailsAdmin)
admin.site.register(CoinSource, CoinSourceAdmin)
admin.site.register(UserCoinsHistory, UserHistoryAdmin)
admin.site.register(FbDetails, FbDetailsAdmin)
admin.site.register(ReferralCoinsConfiguration, ReferralCoinsConfigurationAdmin)
