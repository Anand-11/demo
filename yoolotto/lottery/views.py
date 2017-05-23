from django.views.generic import View
from yoolotto.rest import exceptions
from yoolotto.rest.decorators import rest, Authenticate
from django.shortcuts import render
from yoolotto.user.models import YooLottoUser
from yoolotto.lottery.enumerations import EnumerationManager
from yoolotto.lottery.models import LotteryGame,FantasyWinnerInfo, LotteryDraw, LotteryTicket, Fantasy_Help_Info, \
    Fantasy_Game_Info, LotteryTicketAvailable, Yoocoins_Info, UserTestimonials, RulesAndInfo
from yoolotto.lottery.models import *
from yoolotto.coupon.models import CouponVendor as CouponVendorModel,\
    CouponIssue
from yoolotto.coupon.models import Coupon as CouponModel
from yoolotto.user.models import UserClientLogin
from yoolotto.coin.models import DeviceCoins, EmailCoins
from yoolotto.second_chance.models import *
from django.db.models import Max
import json

def deduct_coins_on_ticketcheck(email):
        if email is not None and email != '':
            try:
                email_coins_record = EmailCoins.objects.filter(email = email)[0]
            except:
                email_coins_record, created = EmailCoins.objects.get_or_create(email = email, defaults={'coins': 0})
            email_coins_record.coins = email_coins_record.coins - float(0.5)
            amount =round((float(0.5)/100),2)
            email_coins_record.dollar_amount = email_coins_record.dollar_amount - amount
            email_coins_record.save()

class Winner(View):
    @rest
    @Authenticate()
    def get(self, request):
        highest_winning_amount = LotteryTicket.objects.all().aggregate(Max('winnings'))
        amount = int(highest_winning_amount["winnings__max"])
        import locale
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') #use locale.format for commafication
        except locale.Error:
            locale.setlocale(locale.LC_ALL, '') #set to default locale (works on windows)
        winning_amount = locale.format('%d', amount , True)
        return {"winning_amount":winning_amount}

class Game(View):
    @rest
    @Authenticate()
    def get(self, request, id=None):
        
    	user = request.yoo["user"]
	if request.yoo["new_version"]:
		ocr_games = ['Powerball','Megamillions']        
        	if id:
            		return LotteryGame.objects.get(pk=id).representation(user)
        
        	active = request.GET.get("active", "active")
        	division = request.GET.get("division", None)
        
        	#games = LotteryGame.objects.all()
		if division == 'TX':
			games = LotteryGame.objects.all()
		else:
			games = LotteryGame.objects.filter(code__in=ocr_games)
        
        	if active:
            		if active == "active":
                		games = games.filter(active=True)
            		elif active == "inactive":
                		games = games.filter(active=False)

		if  division == 'TX':
			games = games.filter(components__division__remote_id=division)                
		return map(lambda x: x.representation(user), games)
	else:
	
        
        	if id:
            		return LotteryGame.objects.get(pk=id).representation(user)
        
        	active = request.GET.get("active", "active")
        	division = request.GET.get("division", None)
        
        	games = LotteryGame.objects.all()
        
        	if active:
            		if active == "active":
                		games = games.filter(active=True)
	            	elif active == "inactive":
                		games = games.filter(active=False)
                
        	if division:
           		games = games.filter(components__division__remote_id=division)
        
	        return map(lambda x: x.representation(user), games)
        
class GameCheck(View):
    @rest
    @Authenticate()
    def post(self, request, _id):
        user = request.yoo["user"]
        division=request.GET.get("division")
        client_login_record = UserClientLogin.objects.filter(device=request.yoo['device'])
        # Short-Circuit for Authentication Errors caused by invalid Device IDs
        if not request.yoo["user"] and request.yoo["auth"].get("__internal__reject__", False):
            raise exceptions.WebServiceAuthorizationFailed()
        
        draw = LotteryDraw.objects.get(pk=_id)        
        try:
            ticket = draw.tickets.get(user=user,division__remote_id=division)
        except:
            ticket = draw.tickets.filter(user=user,division__remote_id=division)[0]
    
        allocated = None

        if ticket.draw.result:
            for submission in ticket.submissions.all():
                submission.checked = True
                submission.save()

            allocated = ticket.update(request.yoo["device"],client_login_record[0].client_login,full=True)
            
        ticket = LotteryTicket.objects.get(pk=ticket.pk)
                
        _result = ticket.representation1()
        _result["coins"] = allocated
        if _id and user:
            import datetime
            now =datetime.datetime.now()
            try:
                issue = CouponIssue.objects.filter(user=user).latest('added_at')
                if (now - issue.redeemed).days > 1:
                    _result['to_show_redeem_button'] = 1
                else:

                    _result['to_show_redeem_button'] = 0 
            except Exception as e:
                _result['to_show_redeem_button'] = 1
            
            no_winning_coupon = map(lambda x: x.representation(), \
            CouponModel.objects.filter(valid_to__gte=now,redeem_limit__gte=1).order_by('sequence'))
            try:
                _result['coupon'] = no_winning_coupon[0]
            except Exception as e:
                _result['coupon'] = None
            
            Inventories = InventoryModel.objects.filter(inventory__gt = 0,status='Active')
            Vendors = [inventory.account for inventory in Inventories ]
            if Vendors:
                Vendors = [Vendors[0]]
                second_chance_vendor = map(lambda x: x.representation(),Vendors)
                _result['second_chance_vendor'] = second_chance_vendor[0]
            '''else:
                _result['second_chance_vendor'] = []'''
        print _result
        return _result

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
        
    
    
class SpecificTicketCheck(View):
    @rest
    @Authenticate()
    def post(self, request):
        user = request.yoo["user"]
        print "user",user.id
        data = json.loads(request.body)
        print data
        version = request.META["HTTP_YOO_APP_VERSION"]
        device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
        division=data["division"]
        # Short-Circuit for Authentication Errors caused by invalid Device IDs
        if not request.yoo["user"] and request.yoo["auth"].get("__internal__reject__", False):
            raise exceptions.WebServiceAuthorizationFailed()

        draw = LotteryDraw.objects.get(pk=data["draw_id"])
        ticket = draw.tickets.get(pk=int(data["ticket_id"]))
        tickets = LotteryTicket.objects.filter(user_id = user.id)
        allocated = None
        if ticket.draw.result:
            for submission in ticket.submissions.all():
                import datetime
                ticket.updated_at = datetime.datetime.now()
                ticket.save()
                submission.checked = True
                submission.save()
            allocated = ticket.update1(request.yoo["device"],request.META['HTTP_YOO_EMAIL_ID'],full=True)
        ticket = LotteryTicket.objects.get(pk=ticket.pk)
        if ticket.add_coins == 0 and ticket.fantasy != 0:
            email_record = EmailCoins.objects.get(email = request.META['HTTP_YOO_EMAIL_ID'])#[0]
            email_record.coins = float(email_record.coins) + float(ticket.winnings_coins)
            amount = float(ticket.winnings_coins)/100
            email_record.dollar_amount = email_record.dollar_amount + amount
            ticket.add_coins = 1
            ticket.save()
            email_record.save()
        if ticket.fantasy!=0 and ticket.ticket_history_recorded==0:
            if ticket.winnings>0 or ticket.winnings_coins>0:
                print 11111111111111111
                email_record = EmailCoins.objects.get(email = request.META['HTTP_YOO_EMAIL_ID'])
                game_type_info = LotteryTicketAvailable.objects.filter(ticket_id = ticket.id)[0]
                game_type = game_type_info.gameType
                if ticket.winnings_coins>0:
                    print "in winnings_coins"
                    if int(game_type) == 13 or int(game_type) == 0:
                        source ="fantasy_mm_earn_coins"
                    elif int(game_type) == 11 or int(game_type)==1:
                        source ="fantasy_pb_earn_coins"
                    print source
                    coin_source = CoinSource.objects.get(source_name = source)
                    users_winning_history = UserCoinsHistory(user = user,credit_coins = ticket.winnings_coins ,source = coin_source,credit_amount = ticket.winnings,device_type = device_type,net_amount = email_record.dollar_amount,net_coins = email_record.coins,app_version=version)
                if ticket.winnings>0:
                    print "in winnings"
                    if int(game_type) == 13 or int(game_type) == 0:
                        source ="fantasy_mm_earn_cash"
                    elif int(game_type) == 11 or int(game_type)==1:
                        source ="fantasy_pb_earn_cash"
                    print source
                    coin_source = CoinSource.objects.get(source_name = source)
                    users_winning_history = UserCoinsHistory(user = user,credit_coins = ticket.winnings_coins,source = coin_source,credit_amount = ticket.winnings,device_type = device_type,net_amount = email_record.dollar_amount,net_coins = email_record.coins,app_version =version)
                users_winning_history.save()
                ticket.ticket_history_recorded=1
                ticket.save()
        _result = 1
        _result = ticket.representation(request.META['HTTP_YOO_EMAIL_ID'],version,device_type)
        #_result = ticket.representation("")
        _result["coins"] = ticket.winnings_coins
        return _result

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class GetMyTicket(View):
    @rest
    @Authenticate()
    def get(self, request):
        ticket_id = request.GET.get("ticket_id")
        ticket = LotteryTicket.objects.get(id=ticket_id)
        coins_info = EmailCoins.objects.get(email = request.META["HTTP_YOO_EMAIL_ID"])
        plays = LotteryTicketPlay.objects.filter(ticket_id= ticket.id)
        count = len(plays)
        user = YooLottoUser.objects.get(email=request.META["HTTP_YOO_EMAIL_ID"])
        if ticket.ticket_submissions.all()[0].pending != 0:
            if int(ticket.ticket_submissions.all()[0].gameType) == 0 or int(ticket.ticket_submissions.all()[0].gameType) == 13:
                if coins_info.coins >= count *1:
                    coins_info.coins = coins_info.coins - count *1
                    amount = float(count *1)/100
                    coins_info.dollar_amount = coins_info.dollar_amount - amount
                    coins_info.save()
                    ticket_available = LotteryTicketAvailable.objects.filter(ticket_id = ticket.id)
                    for tic in ticket_available:
                        tic.pending = 0
                        tic.save()
                    source = "fantasy_mm_spend_coins"
                    coin_source = CoinSource.objects.get(source_name = source)
                    user_history = UserCoinsHistory(user = user,debit_coins = count*1 ,source = coin_source,debit_amount = amount,net_amount = coins_info.dollar_amount,net_coins = coins_info.coins)
                    user_history.save()
            else:
                if coins_info.coins >= count *2:
                    coins_info.coins = coins_info.coins - count *2
                    amount = float(count *2)/100
                    coins_info.dollar_amount = coins_info.dollar_amount - amount
                    coins_info.save()
                    ticket_available = LotteryTicketAvailable.objects.filter(ticket_id = ticket.id)
                    for tic in ticket_available:
                        tic.pending = 0
                        tic.save()
                    source = "fantasy_pb_spend_coins"
                    coin_source = CoinSource.objects.get(source_name = source)
                    user_history = UserCoinsHistory(user = user,debit_coins = count*2 ,source = coin_source,debit_amount = amount,net_amount = coins_info.dollar_amount,net_coins = coins_info.coins)
                    user_history.save()
            coins_info = EmailCoins.objects.get(email = request.META["HTTP_YOO_EMAIL_ID"])
        return {"coins":coins_info.coins}


class UserProfile(View):
    @rest
    @Authenticate()
    def post(self, request):
        user = request.yoo["user"]
        device = request.yoo["device"]
        data = json.loads(request.body)
        name = user.name
        #if client_login_info.device == (str(device.id) + ":" + device.device_id):
        emailcoins = EmailCoins.objects.filter(email=data['email'])[0]
        total_coins = emailcoins.coins
        gametypes = LotteryTicketAvailable.objects.filter(ticket__user = user,ticket__fantasy=True).values("gameType").distinct()
        gamelist = []
        for x in gametypes:
            gamelist.append(x["gameType"])
        gamelist = [x if x not in [u'11', u'1'] else 1 for x in gamelist]
        gamelist = [x if x not in [u'13', u'0'] else 0 for x in gamelist]
        powerball_vars = [u'11', u'1']
        megamillion_vars = [u'13', u'0']
        powerball_count = LotteryTicketAvailable.objects.filter(ticket__user = user, gameType__in = powerball_vars,ticket__fantasy=True).values("ticket").distinct().count()
        megamillion_count = LotteryTicketAvailable.objects.filter(ticket__user = user, gameType__in = megamillion_vars,ticket__fantasy=True).values("ticket").distinct().count()
        gamesnotplayed = list(set([0,1]) - set(gamelist))
        data1 = {"name": name, "coins": total_coins, "powerball_count": powerball_count, "megamillion_count": megamillion_count, "games_not_played": gamesnotplayed}
        return data1


class FantasyHelpInfo(View):
    @rest
    @Authenticate()
    def get(self, request):
        helpinfo = Fantasy_Help_Info.objects.all()
        return map(lambda x: x.representation(), helpinfo)

class FantasyGameInfo(View):
    @rest
    @Authenticate()
    def get(self, request):
        data = {}
        gameinformation = Fantasy_Game_Info.objects.all()
        for info in gameinformation:
            data["gameinfo"] = info.gameinfo
        return data

class Testimonials(View):
    @rest
    @Authenticate()
    def get(self, request):
        testimonials = UserTestimonials.objects.all()
        return map(lambda x: x.representation(), testimonials)

#  Function to manage earn cash screen
#  @params yoo_info The list of all earn cash buttons data
#  @params priorityList The list to set priority
def ManageEarnCashList(yoo_info,priorityList):
    finalList = []
    for i in priorityList:
        finalList.append(yoo_info[i-1])
    return finalList

#  Function to remove item from list
#  @params yoo_info The list of all earn cash buttons data
#  @params _id The id to remove from list
def remove_id_yoocoins_info(yoo_info,_id):
    for i in yoo_info:
        for k, v in i.items():
            if k=='id':
                if int(v)== _id:
                    yoo_info.remove(i)
    return yoo_info

class YoocoinsInfo(View):
    @rest
    @Authenticate()
    def get(self, request):
        user = request.yoo["user"]
        yoocoin_info = Yoocoins_Info.objects.all().order_by("-id")
        yoo_info = map(lambda x: x.representation(), yoocoin_info)
        device_type = request.META["HTTP_YOO_DEVICE_TYPE"]
        app_version = request.META["HTTP_YOO_APP_VERSION"]
        device_id = request.META["HTTP_YOO_DEVICE_ID"]
        print yoo_info
        now = datetime.date.today()
	#android_version = ["1.0","1.1","1.2"]
	try:
            videos_priority_details = VideoPriorityList.objects.filter(isEnable=True,app_version = app_version ,device_type = device_type)
            videos_priority = map(lambda x: x.representation(), videos_priority_details)
	    plc_priority_details = AeservPLCPriorityList.objects.filter(isEnable=True,app_version = app_version ,device_type = device_type)
            plc_priority = map(lambda x: x.representation(), plc_priority_details)
        except:
            videos_priority = []
	    plc_priority = []
        aerserv_plcs_priority = plc_priority
        videos_details = {"min_cycle_count": 1, "mid_cycle_count": 5, "max_cycle_count": 100000, "video_cycle_count":18,
                          "videos_priority": videos_priority, "performance_videos_priority": [],"aerserv_plcs_priority": aerserv_plcs_priority}
        data = {"yoo_info":yoo_info, "no_of_share":1, "hot_icon_image":"/static/more_coins/hot_icon.png",
                "yoobux_icon_image":"/static/more_coins/yoobux_icon.png","appthis_total_campaigns":30,
                "appthis_payout_rate":23,"appromoters_payout_rate":23,"videos_details": videos_details}
        return data

class Rules(View):
    @rest
    @Authenticate()
    def get(self, request):
        rules = RulesAndInfo.objects.all()
        return map(lambda x: x.representation(), rules)

class Fantasy_Winner(View):
    @rest
    @Authenticate()
    def post(self,request):
        data = json.loads(request.body)
        print data
        winner_details = FantasyWinnerInfo(login_email = request.META['HTTP_YOO_EMAIL_ID'],user_email = data['user_email'],ticket_id = data['ticket_id'],winning_amount = data['winning_amount'])
        winner_details.save()
        return {"success":True}

class YoocoinsInfo_7_0(View):
    @rest
    @Authenticate()
    def get(self, request):
        yoocoin_info = Yoocoins_Info_7_0.objects.all()
        yoo_info = map(lambda x: x.representation(), yoocoin_info)
        data = {"yoo_info":yoo_info,"no_of_share":1}
        return data

