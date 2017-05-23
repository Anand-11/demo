from django.conf.urls import patterns, include, url
from yoolotto.promo.views import PromoLanding
from yoolotto.user.views import *
from yoolotto.communication.views import Notification
from yoolotto.util.views import *
from yoolotto.openx_adunits.views import in_app_fuel, YooGames
from yoolotto.second_chance.views import *
from yoolotto.openx_adunits.views import SCACoins,SCATest,EmailVerifyyy
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('^ad', include('yoolotto.ad.urls')),
    url(r'^$', 'yoolotto.analytics.views.main_page', name="main_page"),
    url('^yoogames','yoolotto.second_chance.views.yoo_games_webpage'),
    url('^verify_email', EmailVerifyyy.as_view()),
    url('^coupon/', include('yoolotto.coupon.urls')),
    #url('^aerserv_postback',AerservPostback.as_view()),
    url('^supersonic_postback', SupersonicPostback.as_view()),
    url(r'^plc_list/', 'yoolotto.analytics.views.PLC_list', name="plc_list"),
    url('^nativead_postback',NativexPostback.as_view()),
    url('^second_chance/', include('yoolotto.second_chance.urls')),
    url('^pollfish_postback',PollFillDetails.as_view()),
    url('^lottery/', include('yoolotto.lottery.urls')),
    url('^user/', include('yoolotto.user.urls')),
    url('^play_store', PlayStoreLink.as_view()),
    url('^appnext_postback',AppNextInfo.as_view()),
    #url('^fantasy_lottery/', include('yoolotto.fantasy_lottery.urls')),
    url('^games', include('yoolotto.games.urls')),
    url('^coingames', include('yoolotto.games.urls')),
    url('^promo$', PromoLanding.as_view()),
    url('^promo/(?P<mode>.*)', PromoLanding.as_view()),
    url('^appromoter_postback', ApPromotersPostback.as_view()),
    url(r'^update_email_coins/', 'yoolotto.analytics.views.update_email_coins', name="update_coins"),    
    url('^private/communication/notification', Notification.as_view()),
    url('^_util/version', BuildVersion.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^analytics/', 'yoolotto.analytics.views.generate_report', name="analytics"),
    url(r'^video_list/', 'yoolotto.analytics.views.video_list', name="video_list"),
    url(r'^notification/', 'yoolotto.analytics.views.notifications', name="notifications"),
    url(r'^winnings/', 'yoolotto.analytics.views.winnings', name="winnings"),
    url('^openx/', include('yoolotto.openx_adunits.urls')),
    url(r'^bulk_notification/', 'yoolotto.yoolotto_debug.views.send_bulk_notification', name="bulk_notification"),
    url('^other/in_app_fuel',in_app_fuel.as_view()),
    url('^sca_coins',SCACoins.as_view()),
    url('^sca_test',SCATest.as_view()),
    url(r'^dte_images/', 'yoolotto.yoolotto_debug.views.data_entry_images'),
    url(r'^yoo_games', YooGames.as_view()),
    url('^dashboard/', include('yoolotto.dashboard_app.urls'))

    
    
    
)

