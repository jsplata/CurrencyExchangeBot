import requests
import json
import re
import discord

#This method converts any amount from one currency to all currencies available
def convert(amount, currency):
    r =requests.get('https://api.exchangeratesapi.io/latest?base=' + currency)
    if r.status_code == 400:
        print("Sorry, I don't understand what you mean.")
        return "Sorry I don't understand what you mean."
    else:
        parsed = json.loads(r.text)
        rates = []
        for (k, v) in parsed['rates'].items():
            print(k + ':' + str(round((v*amount),2)))
            rates.append(k + ':' + str(round((v*amount),2)))
        return rates
#This method converts any amount from one currency to one specific currency
def convert_to(amount, currency_from, currency_to):
    #If currency_from is the euro, we have to do a different process as it is the base returned by the API always
    if currency_from == "EUR":
        r_to = requests.get('https://api.exchangeratesapi.io/latest?symbols=' + currency_to)
        if r_to == 400:
            print("Sorry, I don't understand what you mean.")
            return "Sorry, I don't understand what you mean."
        else:
            parsed_to = json.loads(r_to.text)['rates']
            float_to = float([x for x in parsed_to.values()][0])
            print(str(amount) + "EUR = " + str(round(amount*float_to,2)) + currency_to)
            return (str(amount) + "EUR = " + str(round(amount*float_to,2)) + currency_to)
    else:
        #Same as currency_from, but with a different process
        if currency_to == "EUR":
            r_from = requests.get('https://api.exchangeratesapi.io/latest?symbols=' + currency_from)
            if r_from == 400:
                print("Sorry, I don't understand what you mean.")
                return "Sorry, I don't understand what you mean."
            else:
                parsed_from = json.loads(r_from.text)['rates']
                float_from = float([x for x in parsed_from.values()][0])
                print(str(amount) + currency_from + " = " + str(round(amount/float_from,2)) + "EUR")
                return  str(amount) + currency_from + " = " + str(round(amount/float_from,2)) + "EUR"
        else:
            #Separated calls because otherwise results are returned in arbitrary order
            r_from = requests.get('https://api.exchangeratesapi.io/latest?symbols=' + currency_from)
            r_to = requests.get('https://api.exchangeratesapi.io/latest?symbols=' + currency_to)
            if r_from.status_code == 400 or r_to.status_code == 400:
                print("Sorry, I don't understand what you mean.")
                return "Sorry, I don't understand what you mean."
            else:
                parsed_from = json.loads(r_from.text)['rates']
                parsed_to = json.loads(r_to.text)['rates']
                float_from = float([x for x in parsed_from.values()][0])
                float_to = float([x for x in parsed_to.values()][0])
                print(str(amount) + currency_from + " = " + str(round(amount*(float_to/float_from),2)) + currency_to)
                return str(amount) + currency_from + " = " + str(round(amount*(float_to/float_from),2)) + currency_to
#Launching client
client = discord.Client()
#Logging
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
#On message
@client.event
async def on_message(message):
    if message.content.startswith('-c '):
        user_string = message.content.split("-c ",1)[1] 
        amount = re.split(r'(\d+)([.]\d+)?', user_string)
        if len(amount) >= 3:
            expression = re.split(r'(\d+)([.]\d+)?', user_string)[3]
            if amount[2] is None:
                amount = float(amount[1])
            else:
                amount = float(amount[1]+amount[2])
        else:
            expression = amount[0]
            amount = 1
        expression = expression.upper()
        expression = expression.replace(' ','')
        if 'TO' in expression:
            split_string = expression.split('TO')
            result = convert_to(amount, split_string[0],split_string[1])
            await message.channel.send(result) 
        else:
            result = convert(amount, expression)
            await message.channel.send(result)
#Loading token into client
with open('config.json', 'r') as config:
    data = config.read()
    obj = json.loads(data) 
client.run(obj['TOKEN'])

