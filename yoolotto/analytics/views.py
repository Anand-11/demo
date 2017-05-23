from yoolotto.analytics.forms import *
from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse
import csv
from django.shortcuts import redirect
from yoolotto.user.models import *
from yoolotto.coin.models import *
from yoolotto.second_chance.models import *
from yoolotto.lottery.models import *
from django.db import IntegrityError
from yoolotto.rest import exceptions

def notifications(request):
    cursor = connection.cursor()
    query = """
    SELECT lottery_draw.date, lottery_draw.jackpot, lottery_game_component.name,
    COUNT(1) as notified FROM lottery_ticket INNER JOIN lottery_draw ON
    lottery_draw.id = lottery_ticket.draw_id INNER JOIN lottery_game_component ON
    lottery_game_component.id = lottery_draw.component_id WHERE notified = 1 GROUP BY
    draw_id ORDER BY notified DESC;
    """
    

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename=notifications.csv'
    writer = csv.writer(response)
    writer.writerow(['Date','Jackpot','Game','Notifications'])
    result_count = cursor.execute(query)
    result = cursor.fetchall()
    if request.method == "POST":
        for notifications in result:
            data = [notifications[0], notifications[1],notifications[2],notifications[3]]
            writer.writerow(data)
        return response

    context = {'result':result, 'result_count':result_count}
    template = "analytics/notifications.html"
    return render(request, template, context)

def main_page(request):
    website_url ="http://www.yoorewards.com/"
    return redirect(website_url)

def winnings(request):
    query = """
    SELECT lottery_draw.date, lottery_draw.jackpot, lottery_game_component.name,
    lottery_ticket.winnings FROM lottery_ticket INNER JOIN lottery_draw ON
    lottery_draw.id = lottery_ticket.draw_id INNER JOIN lottery_game_component
    ON lottery_game_component.id = lottery_draw.component_id WHERE winnings
    > 0 AND user_id NOT IN (11, 25, 1131, 2667, 10538, 1568) ORDER BY winnings DESC;
    """
    cursor = connection.cursor()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment;filename=winnings.csv'
    writer = csv.writer(response)
    writer.writerow(['Date','Jackpot','Game','Winnings'])
    result_count = cursor.execute(query)
    result = cursor.fetchall()
    if request.method == "POST":
        for winnings in result:
            data = [winnings[0], winnings[1], winnings[2], winnings[3]]
            writer.writerow(data)
        return response
    
    template = "analytics/winnings.html"
    context = {'result_count':result_count, 'result':result}
    return render(request, template, context)

def powerball_stats(date_from,date_to):
    query = """
    SELECT distinct lottery_ticket.id as "Tick ID", lottery_ticket.user_id as "User ID",lottery_ticket_available.gameType as "PB",lottery_ticket_play.play,lottery_ticket.added_at as "Date",user.email as "User Login" 
    FROM lottery_ticket INNER JOIN lottery_ticket_available ON lottery_ticket.id=lottery_ticket_available.ticket_id 
    JOIN lottery_ticket_play ON lottery_ticket.id=lottery_ticket_play.ticket_id JOIN user ON user.id=lottery_ticket.user_id 
    where lottery_ticket.fantasy=1 and (lottery_ticket_available.gameType="1" or lottery_ticket_available.gameType="11") 
    and lottery_ticket.added_at BETWEEN "%s 2:00:00" AND "%s 1:59:59";
    """ % ( date_from,date_to)

    cursor = connection.cursor()
    result_count = cursor.execute(query)
    result = cursor.fetchall()
    return result

def megamillion_stats(date_from,date_to):
    query = """
    SELECT distinct lottery_ticket.id as "Tick ID", lottery_ticket.user_id as "User ID",lottery_ticket_available.gameType as "PB",lottery_ticket_play.play,lottery_ticket.added_at as "Date",user.email as "User Login" 
    FROM lottery_ticket INNER JOIN lottery_ticket_available ON lottery_ticket.id=lottery_ticket_available.ticket_id 
    JOIN lottery_ticket_play ON lottery_ticket.id=lottery_ticket_play.ticket_id JOIN user ON user.id=lottery_ticket.user_id 
    where lottery_ticket.fantasy=1 and (lottery_ticket_available.gameType="0" or lottery_ticket_available.gameType="13") 
    and lottery_ticket.added_at BETWEEN "%s 2:00:00" AND "%s 1:59:59";
    """ % ( date_from,date_to)

    cursor = connection.cursor()
    result_count = cursor.execute(query)
    result = cursor.fetchall()
    return result

def cashfive_stats():
    query = """
    SELECT "Total Players" as data, COUNT(DISTINCT user_id) as count FROM
    lottery_ticket INNER JOIN lottery_draw ON lottery_draw.id = lottery_ticket.draw_id
    WHERE lottery_draw.component_id = 10 UNION SELECT "Total Plays" as data,
    COUNT(1) as count FROM lottery_ticket INNER JOIN lottery_draw ON lottery_draw.id
    = lottery_ticket.draw_id WHERE lottery_draw.component_id = 10 UNION SELECT
    "Total Winning Plays" as data, COUNT(1) as count FROM lottery_ticket INNER
    JOIN lottery_draw ON lottery_draw.id = lottery_ticket.draw_id WHERE
    lottery_draw.component_id = 10 AND lottery_ticket.winnings > 0 UNION SELECT
    "Total Lines" as data, COUNT(1) as count FROM lottery_ticket INNER JOIN lottery_draw
    ON lottery_draw.id = lottery_ticket.draw_id LEFT OUTER JOIN lottery_ticket_play ON
    lottery_ticket_play.ticket_id = lottery_ticket.id WHERE lottery_draw.component_id = 10;
    """
    cursor = connection.cursor()
    result_count = cursor.execute(query)
    result = cursor.fetchall()
    return result  

def twostep_stats():

    query = """
    SELECT "Total Players" as data, COUNT(DISTINCT user_id)
    as count FROM lottery_ticket INNER JOIN lottery_draw ON
    lottery_draw.id = lottery_ticket.draw_id WHERE lottery_draw.component_id
    = 5 UNION SELECT "Total Plays" as data, COUNT(1) as count FROM lottery_ticket
    INNER JOIN lottery_draw ON lottery_draw.id = lottery_ticket.draw_id WHERE
    lottery_draw.component_id = 5 UNION SELECT "Total Winning Plays" as data,
    COUNT(1) as count FROM lottery_ticket INNER JOIN lottery_draw ON
    lottery_draw.id = lottery_ticket.draw_id WHERE lottery_draw.component_id
    = 5 AND lottery_ticket.winnings > 0 UNION SELECT "Total Lines" as data,
    COUNT(1) as count FROM lottery_ticket INNER JOIN lottery_draw ON
    lottery_draw.id = lottery_ticket.draw_id LEFT OUTER JOIN lottery_ticket_play
    ON lottery_ticket_play.ticket_id = lottery_ticket.id WHERE lottery_draw.component_id = 5;
    """
    cursor = connection.cursor()
    result_count = cursor.execute(query)
    result = cursor.fetchall()
    return result


def generate_report(request):
    """
    Generate the Analytics
    """
    stats = None
    if request.method == "POST":
        form_data = AnalyticForm(request.POST)
        if form_data.is_valid():
            cd = form_data.cleaned_data
            if cd['game'] == "Powerball":
                stats = powerball_stats(cd['date_from'],cd['date_to'])
            elif cd['game'] == "MEGA Millions":
                stats = megamillion_stats(cd['date_from'],cd['date_to'])
            elif cd['game'] == "Pick Three":
                stats = pickthree_stats()
            elif cd['game'] == "All or Nothing":
                stats = allornothing_stats()
            elif cd['game'] == "Cash Five":
                stats = cashfive_stats()
            elif cd['game'] == "Daily Four":
                stats = dailyfour_stats
            elif cd['game'] == "Two Step":
                stats = twostep_stats()
            elif cd['game'] == "Lotto Texas":
                stats = lotto_stats()
            if 'export' in request.POST:
                if cd['game'] == "Powerball":
                    game_type = "PB"
                elif cd['game'] == "MEGA Millions":
                    game_type = "MM"
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment;filename=%s.csv' % cd['game']
                writer = csv.writer(response, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                writer.writerow(['Tick ID','User ID',game_type,'','No1','No2','No3','No4','No5','No6','Date','User Login'])
                for analytic in stats:
                    writer.writerow(analytic)
                return response
            template = "analytics/generate_report.html"
            context = {'active':'active', 'form_data':form_data, 'stats':stats}
            return render(request, template, context)
    else:
        form_data = AnalyticForm()
    template = "analytics/generate_report.html"
    context = {'active':'active', 'form_data':form_data, 'stats':stats}
    return render(request, template, context)

def update_email_coins(request):
   
    stats = None
    if request.method == "POST":
        print "right here"
        form_data = UpdateCoinsForm(request.POST)
        print form_data
        if form_data.is_valid():
            cd = form_data.cleaned_data
            print "cd",cd
            email= cd['email']
            coins =cd['coins']
            try:
                user_info = YooLottoUser.objects.get(email=email)
                email_info = EmailCoins.objects.get(email= email)
            except:
                from django.shortcuts import render_to_response
                return render_to_response('analytics/user_doesnot_exists.html')
                
            email_info.coins = email_info.coins + float(coins)
            dollar_amount = float(coins)/100
            email_info.dollar_amount = email_info.dollar_amount +dollar_amount
            email_info.save()
            source = "yoolotto_reward_coins"
            coin_source = CoinSource.objects.get(source_name = source)
            user_history = UserCoinsHistory(user = user_info,credit_coins = coins ,source = coin_source,credit_amount = dollar_amount,net_amount = email_info.dollar_amount,net_coins = email_info.coins)
            user_history.save()
            template = "analytics/coins_successfully_added.html"
            print template
            context = {'active':'active'}
            print context
            print "request",request
            return render(request, template, context)
    else:
        form_data = UpdateCoinsForm()
    template = "analytics/update_coins.html"
    context = {'active':'active', 'form_data':form_data, 'stats':stats}
    return render(request, template, context)

def video_list(request):
    """
    Generate the Analytics
    """
    if request.method == "POST":
        #print request.POST
        form_data = VideoListForm(request.POST)
        #print form_data
        if form_data.is_valid():
            cd = form_data.cleaned_data
            app_version = cd['app_version']
            device_type = cd['device_type']
            video_provider = cd['video_provider']
            isEnable = cd['isEnable']
            now = datetime.datetime.now()
            try:
                video_provider_details = VideoPriorityList.objects.get(app_version = app_version,device_type = device_type,video_provider =video_provider,added_at=now)
                video_provider_details.updated_at = now
            except:

                if video_provider == "inneractive":
                    priority_list_id = 6
                elif video_provider == "loopme":
                    priority_list_id = 5
                elif video_provider == "yume":
                    priority_list_id = 4
                elif video_provider == "aerserv":
                    priority_list_id = 3
                elif video_provider == "AerservInterstitial":
                    priority_list_id = 12
                elif video_provider == "InMobiInterstitial":
                    priority_list_id = 13
		elif video_provider == "InMobi":
                    priority_list_id = 7
		elif video_provider == "Millennial media":
                    priority_list_id = 8
		elif video_provider == "aservBannerAd":
		    priority_list_id = 9
		elif video_provider == "MMBannerAd":
		    priority_list_id = 11
		elif video_provider == "AOLInterstitial":
		    priority_list_id = 14
                video_provider_details = VideoPriorityList.objects.create(priority_list_id=priority_list_id,app_version = app_version,device_type = device_type,video_provider =video_provider,updated_at= now)  
            if isEnable == "Active":
                isEnable = 1
            else:
                isEnable = 0
            video_provider_details.isEnable = isEnable
            video_provider_details.save()
            return HttpResponse("Changes saved successfully")
    else:
        form_data = VideoListForm() 
        print form_data
        template = "analytics/video_list.html"
        context = {'active':'active', 'form_data':form_data}
        return render(request, template, context)


def PLC_list(request):
    """
    Generate the Analytics
    """
    if request.method == "POST":
        #print request.POST
        form_data = PLCListForm(request.POST)
        if form_data.is_valid():
            clean_data = form_data.cleaned_data
            app_version = clean_data['app_version']
            device_type = clean_data['device_type']
            plc_provider = clean_data['plc_provider']
            isEnable = clean_data['status']
            if isEnable == "Active":
                    isEnable = 1
            else:
                isEnable = 0
            try:
                PLC_provider_details = AeservPLCPriorityList.objects.get(app_version = app_version,device_type = device_type,plc_provider =plc_provider)
                PLC_provider_details.isEnable = isEnable
                PLC_provider_details.updated_at = datetime.datetime.now()
                PLC_provider_details.save()

            except:

                if plc_provider == "rewarded":
                    priority_list_id = 1
                    plc_value = "1023340"
                elif plc_provider == "rewarded_2":
                    priority_list_id = 2
                    plc_value = "1023340"
                elif plc_provider == "Yahoo_production":
                    priority_list_id = 3
                    plc_value = "1023340"
                elif plc_provider == "Vdopia_Production":
                    priority_list_id = 4
                    plc_value = "1023340"
                elif plc_provider == "MM_Production":
                    priority_list_id = 5
                    plc_value = "1023340"
                elif plc_provider == "Tremor_Production":
                    priority_list_id = 6 
                    plc_value = "1023340"

                PLC_provider_details = AeservPLCPriorityList.objects.create(priority_list_id=priority_list_id,plc_value = plc_value,app_version = app_version,device_type = device_type,plc_provider =plc_provider,updated_at= datetime.datetime.now())  
            return HttpResponse("Changes saved successfully")
    else:
        form_data = PLCListForm() 
        template = "analytics/plc_list.html"
        context = {'active':'active', 'form_data':form_data}
        return render(request, template, context)
