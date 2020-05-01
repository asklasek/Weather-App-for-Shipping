'''Alpha 1.1: Added multi-city selection'''

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

WFList=[]
def main():

    print("Enter a city and travel duration to see the required packaging")
    print('Press "Enter" to quit the app\n')

    run=True
    while run:
        
        # Create instance of WeatherFinder from input city and travel duration
        city=input("Destination: ")
        city=city.lower()
        if city=="":
            for x in range(4):
                print("Shutdown sequence"+("."*x))
                time.sleep(1)
            break

        days=input("Transit time (days): ")
        while days.isdigit()!=True:
            days=input("Please enter a digit.\n\nTransit time (days): ")
        days=int(days)

        WFList.append(WeatherFinder(city, days))

        # request API for weather at city
        WFList[-1].query5day()
        WFList[-1].setTemps()
        WFList[-1].setTimes()
        
        # determine packout to use from hour-temp correlation.
        pack=packout(WFList[-1].getTemps(), WFList[-1].getTimes(), WFList[-1].getDuration())
        
        # display graph of temps vs. hours
        graphTemps(WFList[-1].getTemps(), WFList[-1].getTimes(), pack, WFList[-1].getCity())

        '''# display packout.               <<< might need for exact duration analysis in future version
        tempData=WF.getTemps()
        timeData=WF.getTimes()
        print(tempData)
        print(timeData)
        print()
        print(pack)
        for x in range(len(tempData)):
            timeList=timeData[x].split(" ")
            hmsList=timeList[1].split(":")
            hm=hmsList[0]+":"+hmsList[1]
            ymdList=timeList[0].split("-")
            md=ymdList[1]+"/"+ymdList[2]
            print(md, hm, end=" - ")
            print(str(int(tempData[x]))+" F")

        "Display graph of temps/date"
        print()
        print(pack)'''
        print() # spacing between queries

''' graphTemps() takes a temperature list, time list, chosen pack, and destination city and displays a plot of the
temperatures over that time period along with the pack to be used. '''
def graphTemps(tempList, timeList, pack, city):

    city=city[0].upper()+city[1:]     # Format for uppercase first letter of city on the graph
    hourList=[]
    for x in range(len(timeList)):    # Using hours from time of query for alpha instead of actual date/time on graph
        hourList.append(x*3)

    '''# format timeList
    plotTimes=[]
    for item in timeList:
        plotTimes.append(item[5:16])''' # Code for specific date/time to be used in later versions.

    # plotting the points
    plt.cla()
    plt.plot(hourList, tempList)
    plt.xlabel('Hours')
    plt.ylabel('Degrees Fahrenheit')       
    plt.title("To: " + city + "\n" + pack) 
    plt.show()

''' packout() takes a temperature list, time list, and duration of shipment to output the correct packaging
to be used for the product. '''
def packout(tempList, timeList, duration):

    highTemp=tempList[0]     # Set low and high initial values
    lowTemp=tempList[0]

    if duration<=2:          # transit is 2 days or less
        for x in range(16):           # find low/high temps to determine Summer/Winter pack
            if tempList[x]>highTemp:
                highTemp=tempList[x]
            if tempList[x]<lowTemp:
                lowTemp=tempList[x]
        if lowTemp<55 and highTemp<55:      # winter pack, <55F
            return "Pack A - 36hr Winter"
        elif lowTemp<55 and highTemp>55:    # fall/spring pack, fluctuating temps
            return "Pack B - 36hr Fall/Spring"
        else:                               # summer pack, >55F 
            return "Pack C - 36hr Summer"

    else:                   # transit is 3 days of more
        for x in range(32):           # find low/high temps to determine Summer/Winter pack
            if tempList[x]>highTemp:
                highTemp=tempList[x]
            if tempList[x]<lowTemp:
                lowTemp=tempList[x]
        if lowTemp<55 and highTemp<55:      # winter pack, <55F
            return "Pack D - 72hr Winter"
        elif lowTemp<55 and highTemp>55:    # fall/spring pack, fluctuating temps
            return "Pack E - 72hr Fall/Spring"
        else:                               # summer pack, >55F
            return "Pack F - 72hr Summer"

''' The WeatherFinder Class initializes from a city and duration (int for days of duration)
    The api "open weather map" is queried to obtain the 5 day forcast with weather data in
    3 hour intervals. The current time is also recorded in case more precise times are needed
    for the program in the future. Limit on queries from free api key.'''
class WeatherFinder:

    ''' Class variables, change API key to your own API key from open weather map '''
    url__="https://community-open-weather-map.p.rapidapi.com/forecast"
    headers__={
    'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
    'x-rapidapi-key': "2dfcdf1e55msha3acb8811cf2a40p1d1f0ajsne92ae2fb20b8"
    }
    
    ''' Initialize instance, set city'''
    def __init__(self, city, duration):
        self.duration__=duration
        self.city__=city
        self.qDict__={"units":"imperial"}
        self.qDict__["q"]=self.getCity()+",us"
        # print(self.qDict__)   Useful for debugging
        self.weatherList__= []
        self.tempList__=[]
        self.timeList__=[]
        self.minTemp__=-100000
        self.maxTemp__=100000
        self.avgTemp__=123456
        now=datetime.now()
        date_time=now.strftime("%Y-%m-%d %H:%M:%S").split()
        self.currentTime__=date_time[1]    # hh:mm:ss.ms
        self.currentDate__=date_time[0]    # yyyy-mm-dd

    ''' set city'''
    def setCity(self, city):
        self.city__= city

    '''set current date/time'''
    def setDateTime(self):
        now=datetime.now()
        date_time=now.strftime("%Y-%m-%d %H:%M:%S").split()
        self.currentTime__=date_time[1]    # hh:mm:ss.ms
        self.currentDate__=date_time[0]    # yyyy-mm-dd

    ''' add temperatures from weatherList'''
    def setTemps(self):
        for item in self.weatherList__:
            self.tempList__.append(item["main"]["temp"])
       
    ''' add times from weatherList'''
    def setTimes(self):
        for item in self.weatherList__:
            self.timeList__.append(item['dt_txt'])
                   
    ''' add city to qDict'''
    def addCity(self):
        qDict__["q"]=self.getCity()+"%2Cus"
        
    ''' return city attribute'''
    def getCity(self):
        return self.city__

    ''' return weather list'''
    def getWeather(self):
        return self.weatherList__

    ''' return temp list'''
    def getTemps(self):
        return self.tempList__

    ''' return time list'''
    def getTimes(self):
        return self.timeList__

    ''' return time of query'''
    def getTime(self):
        return self.currentTime__

    ''' return date of query'''
    def getDate(self):
        return self.currentDate__

    ''' return days needed (int)'''
    def getDuration(self):
        return self.duration__

    ''' query 5-day weather forecast'''
    def query5day(self):
        response = requests.request("GET", self.url__, headers=self.headers__, params=self.qDict__)
        self.weatherList__=(json.loads(response.text)["list"])

if __name__=="__main__": main()
