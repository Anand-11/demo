import requests
from yoolotto.user.models import IPStatus
from django.http import HttpResponseForbidden


# class FilterIPMiddleware(object):
# # Check if client IP is allowed
# 	def process_request(self, request):
# 	# Authorized ip's
# 		if 'HTTP_YOO_DEVICE_ID' in request.META.keys():
# 			ip = request.META.get('REMOTE_ADDR') # Get client IP
# 			ip_object = IPStatus.objects.get(ip_address= ip)

# 			if ip_object.is_blocked:
# 				return HttpResponseForbidden("ip blocked") # If user is not allowed raise Error

# 		# If IP is allowed we don't do anything
# 		return None
# class FilterIPMiddleware(object):
# 	def process_exception(self, request, exception):
# 		print exception.__class__.__name__
# 		print exception.message
# 		return None




from django.conf import settings

class FilterIPMiddleware(object):
    def process_exception(self, request, exception):
        if settings.DEBUG:
            print exception.__class__.__name__
            print exception.message
        return None

