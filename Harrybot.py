import discord
from discord.ext import commands
import random
from coinmarketcap import Market
import datetime
from pinance import Pinance
import json
from riotwatcher import RiotWatcher
from requests import HTTPError
import math
import sqlite3
import time
import sys


#Checks to see if master database for crypto betting games exists
#if the .db doesnt exist then the file will be created.
try:
    conn = sqlite3.connect('file:cryptocurrencyusers.db?mode=rw', uri=True)
    c = conn.cursor()
    c.close
except sqlite3.OperationalError:

    conn = sqlite3.connect('cryptocurrencyusers.db')
#if you ever need to remake the users table, you can just delete the .db file and uncomment this section
    c = conn.cursor()
    command = "CREATE TABLE users (userid text, bank float, joined text);"

    c.execute(command)
    conn.commit()
    c.close()
finally:
    conn = sqlite3.connect('cryptocurrencyusers.db')


#This will run on the initial startup and acquire all cryptocurrency values.
#The Total supply for BTC does not appear though for some reason and thus all values are indexing are off by 1.



def updatecryptos():
    t0 = time.time()
    coinmarketcap = Market()
    cryptocoins = coinmarketcap.ticker(start = 0,limit = 0)


    Allcryptos = {}
    cryptobets = {}

    for x in range(0,len(cryptocoins) - 1):
        name = cryptocoins[x]
        Allcryptos[name['symbol']] = cryptocoins[x]
        cryptobets[name['symbol']] = 0
    print('All coins have been updated')
    t1 = time.time()
    total = t1-t0
    print(total)
    return Allcryptos








description = 'Harry'
bot = commands.Bot(command_prefix='.', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def repeat(times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')

@bot.command()
async def unmutev(member: discord.Member):
    #Unmutes member in voice channels.
    await bot.say('Unmuting '+ str(member) + ' from voice channels in this server.')
    await bot.server_voice_state(member,mute= False)


@bot.command()
async def mutev(member : discord.Member):
    #Mutes member in voice channels.
    await bot.say('Muting '+ str(member) + ' from voice channels in this server.')
    await bot.server_voice_state(member,mute= True)

@bot.command()
async def ban( member : discord.Member):
    #Bans a member from server
    await bot.say('Banning ' + str(member) + ' from the server.')
    await bot.ban(member, 0)



@bot.command(pass_context = True)
async def hello(ctx):
    author = ctx.message.author.name
    print(author)

    embed = discord.Embed(color = discord.Colour.purple())
    embed.set_author(name = 'Hello')
    embed.add_field(name = "User",value = author)
    await bot.say(embed=embed)


#@bot.event
#async def on_command_error(event,ctx):
    #this catches an errors with users that don't exist
    #await bot.send_message(ctx.message.channel,"User doesn't exist.")






@bot.command(pass_context = True)
async def cryptoregister(ctx):
    author = ctx.message.author

    joined = str(int(time.time()))
    c = conn.cursor()
    try:
        command = "INSERT INTO users (userid, bank,joined) VALUES ('" + author.id + "',10000," + joined + "); "
        c.execute(command)
        conn.commit()
        command = "CREATE TABLE '" + author.id +"' (coin text, amount float, worth float);"
        c.execute(command)
        conn.commit()
        string = (author.name + ' has been added to the crypto bet game. You have been awarded $10,000 to start.')
        return True
    except sqlite3.IntegrityError:
        print('Failed to insert values %d, %s')
        string = ('An error has occured.')
        return False
    except sqlite3.OperationalError:
        print('User always is registered.')
        string = ('You are already registered for the crypto betting game.')
    finally:
        c.close()
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_author(name='Crypto Register Status')
        embed.add_field(name="User", value=author)
        embed.add_field(name = 'status',value = string)
        await bot.say(embed=embed)




@bot.command(pass_context = True)
async def cryptobetstatus(ctx):

    Allcryptos = updatecryptos()
    author = ctx.message.author
    c = conn.cursor()
    userid =(author.id,)

    c.execute('SELECT * FROM users WHERE userid=?',userid)
    userinformation = c.fetchone()
    if userinformation == None:
        string = ('You are currently not registered. To register type the command: cryptoregister')
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_author(name='Crypto Bet Status')
        embed.add_field(name="User", value=author)
        embed.add_field(name = 'status',value = string)
        await bot.say(embed=embed)
        return
    datejoined = datetime.datetime.fromtimestamp(int(userinformation[2])).strftime('%Y-%m-%d')
    bank = ('$'  + str(math.floor(userinformation[1])))
    joined = ('You joined on ' + datejoined + '.')

    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(c.fetchall())


    #fetches coin investments from userid's table
    c.execute('SELECT * FROM \'' + author.id + "';")
    investments = c.fetchall()
    print(len(investments))
    print(investments)

    totalwealth = math.floor(userinformation[1])

    embed = discord.Embed(color=discord.Colour.purple())
    embed.set_author(name='Current Portfolio')
    embed.add_field(name="User", value=author)
    embed.add_field(name='Status', value='Registered')
    embed.add_field(name = 'Joined',value = joined)
    embed.add_field(name = 'Bank',value = bank)
    embed.add_field(name = 'Coins',value = '(Coins owned, Total Value, Overall Change)',inline = False)




    if len(investments) != 0:
        for x in range(0, len(investments)):
            investment = investments[x]
            coin = investment[0]
            amount = investment[1]
            price = float(Allcryptos[coin]['price_usd'])
            total = price*amount
            totalwealth = totalwealth + total

            if price*amount > investment[2]:
                percentchange = round(((price*amount)/investment[2] - 1)*100,2)
            elif price*amount < investment[2]:
                percentchange = 0 - round((investment[2]/(price*amount) -1)*100,2)
            else:
                percentchange = 0
            cointotal = str(amount)
            pricevalue = ('$' + str(round(total,2)))
            percentvalue = (str(percentchange)+ '%')
            embed.add_field(name = coin, value =(cointotal +'     ' + pricevalue + '     ' + percentvalue),inline= False)

    else:
        string = ('You currently do not own any cryptocoins.')
        clear_fields()
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_author(name='Current Portfolio')
        embed.add_field(name="User", value=author)
        embed.add_field(name='Status', value='Registered')
        embed.add_field(name = 'Coins',value ='None',inline = False)
        embed.add_field(name='Total Wealth', value=bank,inline = False)


    wealth = ('$' + str(round(totalwealth,2)))
    embed.add_field(name = 'Total Wealth',value =wealth)

    await bot.say(embed=embed)

@bot.command(pass_context = True)
async def cryptobet(ctx, order : str, coin = None, payment =None):

    order = order.upper()
    print(order)
    if order == "HELP":
        await bot.say('Command is written as: ",cryptobet <order> <coin> <amount>". Bot only can take input of cryptocoins symbol such as BTC or ETH. To buy 5 Bitcoins one would type ",cryptobet BUY BTC 5"')
        return
    elif order != "BUY" and order != "SELL":
        await bot.say('Order has to be either "HELP", "BUY" or "SELL".')
        return

    #If help command was not inputted than ensure that a coin was inputted
    try:
        coin = coin.upper()
    except AttributeError:
        await bot.say('No cryptocoin was inputted.')
        return




    Allcryptos = updatecryptos()
    c = conn.cursor()
    author = ctx.message.author
    userid = (author.id,)

    #checks to see if coin exists
    try:
        price = float(Allcryptos[coin]['price_usd'])
    except KeyError:
        await bot.say('No cryptocoin inputted or invalid crypto. Coins are pulled from coinmarketcap.com. Command is written as: ",cryptobet <order> <coin> <amount>"')
        return

    print(order)
    print(coin)
    print(payment)
    print(author.id)


    # If help command was not inputted than ensure that a payment was inputted
    try:
        payment = payment.upper()
    except AttributeError:
        await bot.say('No payment was inputted')
        return


    if payment != "ALL":
        try:
            payment = float(payment)
        except TypeError:
            await bot.say('No payment was inputted.')
            return
        except ValueError:
            await bot.say('Payment was not a valid input.')
            return



    # get total cash available for user
    c.execute('SELECT * FROM users WHERE userid=?', userid)
    userinformation = c.fetchone()
    cashavaiable = userinformation[1]




    if order == "BUY":

        #if there isnt enough cash or value is negative than the functions ends
        if price*payment >= cashavaiable:
            await bot.say('Not enough cash to buy this amount of '+ coin +'.')
            c.close()
            return

        elif payment < 0:
            await bot.say('Payment can not be a negative number.')
            c.close()
            return
        elif payment == 0:
            await bot.say('You can not buy 0 worth of cryptocoins')
            c.close()
            return



        #CALCULATE CASH REMAINING AND UPDATE USERS TABLE
        cashavaiable = cashavaiable - price*payment
        print(cashavaiable)

        c.execute("UPDATE users SET bank = ? WHERE userid = ?",(cashavaiable,author.id))
        conn.commit()


        c.execute("SELECT 1 FROM  \'" + author.id + "' WHERE coin = '" + coin + "'")
        if c.fetchone():
            c.execute("SELECT amount FROM  \'" + author.id + "' WHERE coin = '" + coin + "'")
            currentamount = c.fetchone()
            updatedamount = currentamount[0] + payment

            c.execute("SELECT worth FROM  \'" + author.id + "' WHERE coin = '" + coin + "'")
            coinworth = list(c.fetchone())
            print(coinworth)
            coinworth[0] = coinworth[0] + payment*price
            print(type(updatedamount))
            print(type(coinworth))
            print(coinworth)
            c.execute('UPDATE  \'' + author.id + "' SET amount =?, worth = ?  WHERE coin = ?",(updatedamount,coinworth[0],coin))
            conn.commit()

            await bot.say(author.name + ' you have bought ' + str(payment) + ' ' + coin + ' for a total of $' + str(round(price * payment,3)) + '.')
            await bot.say('You now own ' + str(updatedamount) + ' ' + coin + '.')

        else:
            coinworth = payment*price
            c.execute('INSERT INTO  \'' + author.id + "' (coin,amount,worth) VALUES ('" + coin + "'," + str(payment) +"," +str(coinworth) +");")
            conn.commit()
            updatedamount = payment
            await bot.say(author.name + ' you have bought ' + str(payment) + ' ' + coin + ' for a total of $' + str(round(price*payment,3)) +'.')

    elif order == "SELL":




        c.execute("SELECT 1 FROM  \'" + author.id + "' WHERE coin = '" + coin + "'")
        if c.fetchone():
            c.execute("SELECT amount FROM  \'" + author.id + "' WHERE coin = '" + coin + "'")
            currentamount = c.fetchone()


            if payment == "ALL":
                cashavaiable = cashavaiable + price* currentamount[0]
                c.execute("UPDATE users SET bank = ? WHERE userid = ?", (cashavaiable, author.id))
                conn.commit()
                c.execute('DELETE FROM  \'' + author.id + "' WHERE coin = ?", (coin,))
                conn.commit()
                await bot.say('You have sold all of your investment in ' + coin + ' for a total of $' + str(round(price * currentamount[0], 3)) + '.')


            elif payment <= currentamount[0] and payment > 0:
                updatedamount = currentamount[0] - payment
                print(updatedamount)
                c.execute('UPDATE  \'' + author.id + "' SET amount =? WHERE coin = ?",(updatedamount,coin))
                conn.commit()

                # CALCULATE CASH REMAINING AND UPDATE USERS TABLE
                cashavaiable = cashavaiable + price * payment
                print(cashavaiable)

                c.execute("UPDATE users SET bank = ? WHERE userid = ?", (cashavaiable, author.id))
                conn.commit()

                if updatedamount != 0:


                    await bot.say(author.name + ' you have sold ' + str(payment) + ' ' + coin + ' for a total of $' + str(round(price * payment,3)) + '.')
                    await bot.say('You now own ' + str(updatedamount) + ' ' + coin + '.')
                else:
                    c.execute('DELETE FROM  \'' + author.id + "' WHERE coin = ?", (coin,))
                    conn.commit()

                    await bot.say('You have sold all of your investment in ' + coin + ' for a total of $' + str(round(price * payment,3)) + '.' )


            elif payment < 0:
                await bot.say('You can not sell a negative amount of coins.')
            else:
                await bot.say('You do not own enough of ' + coin + ' to complete this order. You currently posses ' + str(currentamount[0]) + ' ' + coin + '.')

        else:
            await bot.say('You do not own any ' + coin + '.')

    else:
        await bot.say("'" + order + "' is not a valid command. Only 'BUY' and 'SELL' are commands.")



        c.close()

@bot.command()
async def crypto(coin : str):

    Allcryptos = updatecryptos()
    coin = coin.upper()
    if  coin == "HELP":
        await bot.say('Command is written as: ",crypto <currency>". Bot only can take input of cryptocoins symbol such as BTC or ETH. To get data on Ethereum one would type ",crypto ETH".')
    else:
        try:
            coinchosen = Allcryptos[coin]
            name = coinchosen['name']
            rank = coinchosen['rank']
            price = coinchosen['price_usd']
            change1hr = coinchosen['percent_change_1h']
            change24hr = coinchosen['percent_change_24h']
            change7d = coinchosen['percent_change_7d']
            lastupdate = coinchosen['last_updated']
            timeupdated = datetime.datetime.fromtimestamp(int(lastupdate)).strftime('%Y-%m-%d %H:%M:%S')
            await bot.say(name + ' is currently rank ' + rank +' and is priced at $' + price +'. The percentage change for the last hour is ' +change1hr +'% while the percentage change for 24 hours is '+ change24hr +'% and finally the percentage change for the last 7 days is '+ change7d +'%. This was last updated at '+ timeupdated +'.')
        except KeyError:
            await bot.say('Error: This input is not a cryptocurrency symbol.')


@bot.command()
async def cryptomarket():
    coinmarketcapstats = coinmarketcap.stats()
    bitcoin_percentage_of_market_cap = coinmarketcapstats['bitcoin_percentage_of_market_cap']
    total_currencies = coinmarketcapstats['active_currencies']
    total_markets = coinmarketcapstats['active_markets']
    lastupdate = coinmarketcapstats['last_updated']
    timeupdated = datetime.datetime.fromtimestamp(int(lastupdate)).strftime('%Y-%m-%d %H:%M:%S')

    await bot.say("Bitcoin is "+ str(bitcoin_percentage_of_market_cap) + "%" + " of the market. There are currently: " +str(total_currencies) +' cryptocurrencies on the market, spread through: '+ str(total_markets) +' markets on the internet.This was last updated at '+ timeupdated +'.')

@bot.command()
async def stock(symbol: str):
    symbol = symbol.upper()
    if  symbol == "HELP":
        await bot.say('Command is written as: ",stock <Stock>". Bot only can take input of stock symbol such as AAPL or GOOGL. To get data on Apple one would type ",crypto AAPL".')
    else:
        try:

            company = Pinance(symbol)
            company.get_quotes()
            stock = company.quotes_data

            price = stock['regularMarketPrice']
            percentchange = stock['regularMarketChangePercent']
            index = stock['fullExchangeName']
            lastupdate = stock['regularMarketTime']
            timeupdated = datetime.datetime.fromtimestamp(int(lastupdate)).strftime('%Y-%m-%d %H:%M:%S')
            await bot.say(symbol + ' is currently trading at $' + str(price) + ' corresponding to a ' + str(percentchange) +'% change. This was last updated at '+ timeupdated)

        except KeyError:
            await bot.say('Error: This input is not a stock symbol.')






@bot.command()
async def league(summonername : str):
    watcher = RiotWatcher('League Of Legends API required')
    my_region = 'na1'

    try:
        me = watcher.summoner.by_name(my_region, summonername)

        my_ranked_stats = watcher.league.positions_by_summoner(my_region,me['id'])
        print(my_ranked_stats)
        solo_tier = None
        solo_rank = None
        solo_win = None
        solo_lose = None
        flex_tier = None
        flex_rank = None
        flex_win = None
        flex_lose = None


        if len(my_ranked_stats) == 0:
            await bot.say('You currently aren\'t placed in rank.')
        else:
            for x in range(0,len(my_ranked_stats)):
                if my_ranked_stats[x]['queueType'] == 'RANKED_FLEX_SR':
                    flex_tier = my_ranked_stats[x]['tier']
                    flex_rank = my_ranked_stats[x]['rank']
                    flex_win = my_ranked_stats[x]['wins']
                    flex_lose = my_ranked_stats[x]['losses']
                    winpercentflex = round((flex_win/(flex_win+flex_lose))*100,1)
                elif my_ranked_stats[x]['queueType'] == 'RANKED_SOLO_5x5':
                    solo_tier = my_ranked_stats[x]['tier']
                    solo_rank = my_ranked_stats[x]['rank']
                    solo_win = my_ranked_stats[x]['wins']
                    solo_lose = my_ranked_stats[x]['losses']
                    winpercentsolo = round((solo_win/(solo_win+solo_lose))*100,1)


            if flex_rank == None and solo_rank != None:
                await bot.say(
                    'Your Solo rank is: ' + str(solo_tier) + ' ' + str(solo_rank) + ' and your Flex rank is: Unranked.')
                await bot.say('Your Solo winrate is: ' + str(winpercentsolo) + '%.')
            elif flex_rank != None and solo_rank == None:
                await bot.say('Your Solo rank is: Unranked' + ' and your Flex rank is: ' + str(flex_tier) + ' ' + str(
                    flex_rank) + '.')
                await bot.say('Your Flex winrate is: ' + str(winpercentflex) + '%.')
            elif flex_rank != None and solo_rank != None:
                await bot.say(
                    'Your Solo rank is: ' + str(solo_tier) + ' ' + str(solo_rank) + ' and your Flex rank is: ' + str(
                        flex_tier) + ' ' + str(flex_rank) + '.')
                await bot.say('Your Solo winrate is: ' + str(winpercentsolo) + '% and your Flex winrate is: ' + str(
                    winpercentflex) + '%.')


    except HTTPError as err:
        if err.response.status_code == 429:
            await bot.say('We should retry in {} seconds.'.format(e.headers['Retry-After']))
            await bot.say('this retry-after is handled by default by the RiotWatcher library')
            await bot.say('future requests wait until the retry-after time passes')
        elif err.response.status_code == 404:
            await bot.say('Summoner with that ridiculous name not found.')
        else:
                raise
                # print(my_ranked_stats)
 #    if len(my_ranked_stats) > 1:
 #
 #        flex_ranked_stats = my_ranked_stats[0]
 #        solo_ranked_stats = my_ranked_stats[1]
 #        print(flex_ranked_stats)
 #        print(solo_ranked_stats)
 #        flex_rank_tier = flex_ranked_stats['tier']
 #        flex_rank_divsion = flex_ranked_stats['rank']
 #        solo_rank_tier = solo_ranked_stats['tier']
 #        solo_rank_divsion = solo_ranked_stats['rank']
 #        await bot.say('Your Solo rank is: ' + str(solo_rank_tier) +' ' + str(solo_rank_divsion) +' and your Flex rank is: ' + str(flex_rank_tier)+ ' ' + str(flex_rank_divsion) +'.')
 #    else:
 #        await bot.say('You currently aren\'t placed in rank.')




@bot.command()
async def Help():

    embed = discord.Embed(color=discord.Colour.purple())
    embed.set_author(name='Commands')
    for i in range(0,len(functions)):
        embed.add_field(name='Command', value=functions[i])

    await bot.say(embed=embed)




# helps create a list of functions that are in this module
functions = dir()
functions.remove('HTTPError')
functions.remove('Market')
functions.remove('Pinance')
functions.remove('RiotWatcher')
functions.remove('__annotations__')
functions.remove('__builtins__')
functions.remove('__cached__')
functions.remove('__doc__')
functions.remove('__file__')
functions.remove('__loader__')
functions.remove('__name__')
functions.remove('__package__')
functions.remove('__spec__')
functions.remove('c')
functions.remove('conn')
functions.remove('datetime')
functions.remove('discord')
functions.remove('description')
functions.remove('commands')
functions.remove('json')
functions.remove('math')
functions.remove('on_ready')
functions.remove('random')
functions.remove('sqlite3')
functions.remove('sys')
functions.remove('time')

bot.run('DISCORD API REQUIRED')
