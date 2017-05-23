from django.contrib import admin
from yoolotto.user.models import *
from django.db.models import Q

class Reason_To_Block(admin.ModelAdmin):
    
    list_display = ['reason','created_date']
    
admin.site.register(ReasonToBlock, Reason_To_Block)


class Reason_To_UnBlock(admin.ModelAdmin):
	list_display = ['reason','created_date']
     
admin.site.register(ReasonToUnBlock,Reason_To_UnBlock)


class VideoBannerLengthDetails(admin.ModelAdmin):
	list_display = ['max_length_video_in_seconds','min_length_video_in_seconds','max_length_banner_in_seconds','min_length_banner_in_seconds','is_active']

admin.site.register(VideoBanerLengthDetails,VideoBannerLengthDetails)



class User_Device_status(admin.ModelAdmin):
	list_display =['device_id','is_blocked','last_blocked_date','last_blocked_by','last_unblocked_by','no_times_update']
admin.site.register(UserDeviceStatus,User_Device_status)


class IP_Status(admin.ModelAdmin):
	list_display = ['ip_address','is_blocked','no_times_update']
	readonly_fields = ['last_blocked_by','last_blocked_date','last_unblocked_date','last_unblocked_by','no_times_update']
admin.site.register(IPStatus,IP_Status)


class User_Device_Impression(admin.ModelAdmin):
	list_display = ['user_ip','total_video_count','total_banner_count','list_of_providers','created_date']
admin.site.register(UserDeviceImpression,User_Device_Impression)


from django.utils.translation import ugettext_lazy as _

class SuspectedListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Blocked User')

    # Parameter for the filter that will be used in the URL query.

    parameter_name = 'blocked'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('blocked', _('blocked user email')),
        )
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'blocked':
            return queryset.filter(user_device__user__is_blocked=True)
class Suspected_User(admin.ModelAdmin):
	list_display = ['user','user_ip','device_id','created_date','reason','video_count_requested','banner_count_requested','providers']
	search_fields = ['user_device__user__email','impression_ref__user_ip','user_device__device_id','created_date']
	# list_filter = (SuspectedListFilter,)
	def get_queryset(self, request):
		qs = super(Suspected_User, self).get_queryset(request)
		return qs.order_by("-created_date")

	def get_search_results(self, request, queryset, search_term):
		queryset = queryset.filter(Q(user_device__user__email__iexact=search_term) | Q(impression_ref__user_ip__iexact=search_term) | Q(user_device__device_id__iexact=search_term) | Q(created_date__icontains=search_term))
		queryset, use_distinct = super(Suspected_User, self).get_search_results(request, queryset, search_term)
		return queryset,use_distinct

admin.site.register(SuspectedUser,Suspected_User)
	 


