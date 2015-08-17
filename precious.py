from Cocoa import *
from Foundation import NSObject
import json, signal, os, pprint, time
from datetime import datetime


class PreciousController(NSWindowController):
    hourLabel = objc.IBOutlet()
    dayLabel = objc.IBOutlet()
    dayButton = objc.IBOutlet()
    hourButton = objc.IBOutlet()
    hourProgress = objc.IBOutlet()
    dayProgress = objc.IBOutlet()
    hourField = objc.IBOutlet()
    dayField = objc.IBOutlet()
    hourSegment = objc.IBOutlet()

    # initializing the window
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        # default data values in the window
        self.productive = 1
        self.activity = None
        self.reflection = None

        # attempt to load current day/hour data
        self.loadData()
        # init the badge
        self.badge = NSApp.dockTile() 
        # stop animation of the progress indicators to hide them
        self.hourProgress.stopAnimation_(self)
        self.dayProgress.stopAnimation_(self)
        
        # set current datetime object and current timestamp
        self.curr_timestamp = time.time()
        self.reloadTime()
        
        # update displayed hour
        self.updateDisplayHour()
        self.updateDisplayDay()
    
    def reloadTime(self):
        self.curr_time = datetime.fromtimestamp(self.curr_timestamp)
        self.year = self.curr_time.year
        self.month = self.curr_time.month
        self.day = self.curr_time.day
        self.hour = int(self.curr_time.strftime('%H')) # need a 24 hour        
    
    # update the displayed date & hour in the interface
    def updateDisplayHour(self):
        self.hourLabel.setStringValue_(self.curr_time.strftime('%a %d %b, %I %p'))
        self.dayLabel.setStringValue_(self.curr_time.strftime('%a %d %b'))
        self.dayButton.setStringValue_(self.curr_time.strftime('%a %d %b'))
        if self.activity:
            self.hourField.setStringValue_(self.activity)
            self.hourLabel.setTextColor_(NSColor.blackColor())
        else:
            self.hourField.setStringValue_('')
            # if not self.productive and self.productive != 0:
            self.hourLabel.setTextColor_(NSColor.redColor())
        if self.productive or self.productive == 0:
            self.hourSegment.setSelected_forSegment_(1, self.productive)
        else:
            self.hourSegment.setSelected_forSegment_(1, 1)
    
    # update the displayed date in the interface
    def updateDisplayDay(self):
        self.hourLabel.setStringValue_(self.curr_time.strftime('%a %d %b, %I %p'))
        self.dayLabel.setStringValue_(self.curr_time.strftime('%a %d %b'))
        self.dayButton.setAttributedTitle_(self.curr_time.strftime('%a %d %b'))
        if self.reflection:
            self.dayField.setStringValue_(self.reflection)
            self.dayLabel.setTextColor_(NSColor.blackColor())
        else:
            self.dayField.setStringValue_('')
            self.dayLabel.setTextColor_(NSColor.redColor())
        
    # choice of how productive the hour has been
    @objc.IBAction
    def productive_(self, sender):
        self.productive = sender.selectedSegment()

    # load the previous hour data in the hour window
    @objc.IBAction
    def prevHour_(self, sender):
        # decrement time
        self.curr_timestamp -= 3600
        self.switchHour()
        print 'prev hour'

    # load the next hour data in the hour window
    @objc.IBAction
    def nextHour_(self, sender):
        # increment the time
        self.curr_timestamp += 3600
        self.switchHour()
        print 'next hour'
    
    def switchHour(self):
        # get the time data
        self.reloadTime()
        # load the data
        self.clearData()
        self.loadData(
            year = self.curr_time.year, 
            month = self.curr_time.month, 
            day = self.curr_time.day, 
            hour = self.curr_time.hour)
        # update the interface
        self.updateDisplayDay()
        self.updateDisplayHour()        
    
    # load the previous day data in the day window
    @objc.IBAction
    def prevDay_(self, sender):
        # decrement the time
        self.curr_timestamp -= 86400
        self.switchDay()
        print 'prev day'

    # load the next day data in the day window
    @objc.IBAction
    def nextDay_(self, sender):
        # increment the time
        self.curr_timestamp += 86400
        self.switchDay()
        print 'next day'
        
    # switch the day
    def switchDay(self):
        # get the time data
        self.reloadTime()
        # load the data
        self.clearData()
        self.loadData(
            year = self.curr_time.year, 
            month = self.curr_time.month, 
            day = self.curr_time.day,
            hour = self.curr_time.hour)
        # update the interface
        self.updateDisplayDay()
        self.updateDisplayHour()        

    # help: show the info about the program
    @objc.IBAction
    def help_(self, sender):
        pass
        # self.productive = 1
        # self.updateDisplay()
        # show help screen

    # sync: sync the last logged hours with the web database
    @objc.IBAction
    def sync_(self, sender):
        self.syncData()
    
    # submit the data
    @objc.IBAction
    def submitHour_(self, sender):
        # start the progress spin
        self.hourProgress.startAnimation_(self)
        
        # getting the text from text fields
        self.activity = self.hourField.stringValue()
        # self.reflection = self.dayField.stringValue()

        # log the hour
        self.logData(
            type = 'hour',
            productive = self.productive, 
            activity = self.activity, 
            year = self.curr_time.year, 
            month = self.curr_time.month, 
            day = self.curr_time.day, 
            hour = self.curr_time.hour)
        
        # remove the badge
        self.badge.setBadgeLabel_(None)
        # set the hour label colour to black
        self.hourLabel.setTextColor_(NSColor.blackColor())
        # set timer to relaunch the app in the end of next hour
        # self.setPyTimer()
        
        # go for the next hour
        # self.curr_timestamp += 3600
        # self.switchHour()
        
        # stop the progress spin
        self.hourProgress.stopAnimation_(self)

    # submit the data
    @objc.IBAction
    def submitDay_(self, sender):
        # start the progress spin
        self.dayProgress.startAnimation_(self)
        # getting the text from text field
        self.reflection = self.dayField.stringValue()
        
        self.logData(
            type = 'day',
            reflection = self.reflection,
            year = self.curr_time.year, 
            month = self.curr_time.month, 
            day = self.curr_time.day)
        
        # remove the badge
        # self.badge.setBadgeLabel_(None)
        # set the day label colour to black
        self.dayLabel.setTextColor_(NSColor.blackColor())
        # set timer to relaunch the app in the end of next hour
        # self.setPyTimer()
        # stop the progress spin
        self.dayProgress.stopAnimation_(self)
    
    # log hour or day
    def logData(self, type, productive = 1, activity = None, reflection = None, year = None, month = None, day = None, hour = None):
        # getting the system date and time if they are not set
        if not year or not month or not day or (not hour and hour != 0 and type != 'day'):
            today = datetime.now()
            year = today.year
            month = today.month
            day = today.day
            # hour = today.hour
            hour = int(today.strftime('%H')) # need a 24 hour
    
        # convert date and hour to strings
        year = str(year)
        month = str(month)
        day = str(day)
        hour = str(hour)

        try:
            # open the file to read data from
            fr = open('precious_mytime.js', 'r')
            # load and decode the JSON data
            json_data = json.load(fr)
            # close the file
            fr.close
        except IOError:
            # file does not exist yet - set json_data to an empty dictionary
            print 'File not found'
            json_data = {}
        
        # this accounts for the problem when year/month/day have not been set yet in the JSON file
        if year not in json_data:
            json_data[year] = {};
        if month not in json_data[year]:
            json_data[year][month] = {}
        if day not in json_data[year][month]:
            json_data[year][month][day] = {}
        
        # logging hour
        if type == 'hour':
            # if this hour is not in the JSON file yet
            if hour not in json_data[year][month][day]:
                json_data[year][month][day][hour] = {}
            # append the hour data to the appropriate decoded node of the json_data
            json_data[year][month][day][hour].update({
                'productive': productive,
                'activity': activity
            })
            # DEBUG print the hour data
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(json_data[year][month][day][hour])        
        # logging day
        elif type == 'day':
            # append the hour data to the appropriate decoded node of the json_data
            json_data[year][month][day].update({
                'reflection': reflection
            })
            # DEBUG print the day data
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(json_data[year][month][day])        

        # open the file to rewrite data
        fw = open('precious_mytime.js', 'w')
        # JSON dump of the data
        json.dump(json_data, fw)
        # close the file
        fw.close

    # set default data
    def clearData(self):
        self.activity = None
        self.reflection = None
        self.productive = 1
        
    # load hour or day data
    def loadData(self, year = None, month = None, day = None, hour = None):
        # getting the system date and time if they are not set
        if not year or not month or not day or (not hour and hour != 0):
            today = datetime.now()
            year = today.year
            month = today.month
            day = today.day
            hour = today.hour
    
        # convert date and hour to strings
        year = str(year)
        month = str(month)
        day = str(day)
        hour = str(hour)

        try:
            # open the file to read data from
            fr = open('precious_mytime.js', 'r')
            # load and decode the JSON data
            json_data = json.load(fr)
            # close the file
            fr.close
        except IOError:
            # file does not exist yet - set json_data to an empty dictionary
            print 'File not found'
            json_data = {}
        
        if year in json_data and month in json_data[year] and day in json_data[year][month]:
            if 'reflection' in json_data[year][month][day]:
                self.reflection = json_data[year][month][day]['reflection']
            if hour in json_data[year][month][day]:
                self.activity = json_data[year][month][day][hour]['activity']
                self.productive = json_data[year][month][day][hour]['productive']

    # load last hour logged
    # def getLast(self):
    #     try:
    #         # open the file to read data from
    #         fr = open('precious_mytime.js', 'r')
    #         # load and decode the JSON data
    #         json_data = json.load(fr)
    #         # close the file
    #         fr.close
    #         # init datetime and time modules
    #         hour_inc = 0
    #         reflection = None
    #         # activity = None
    #         # run a loop to find the latest activity or reflection from before
    #         while hour_inc < 86400 and not reflection:
    #             # get the date and time from earlier
    #             today = datetime.fromtimestamp(time.time()-hour_inc) # this hour, last hour, 2 hours earlier etc.
    #             year = str(today.year)
    #             month = str(today.month)
    #             day = str(today.day)
    #             # hour = str(today.hour)
    #             # 1 hour earlier
    #             hour_inc += 3600
    #
    #             # try to access data by the loaded year-month-day-hour keys
    #             try:
    #                 # self.activity = json_data[year][month][day][hour]['activity']
    #                 reflection = json_data[year][month][day]['reflection']
    #             except KeyError:
    #                 print 'Previous hour not found'
    #             self.reflection = reflection
        #
        # except IOError:
        #     # file does not exist yet
        #     print 'File not found'
    
    def endOfHour(self):
        print 'Called by timer!'
        # nc = NSNotificationCenter.defaultCenter()
        # nc.postNotificationName_object_userInfo_('love_note', None, {'path':'xyz'})
        # Bring app to top
        NSApp.activateIgnoringOtherApps_(True)
        # Set badge icon to the current hour
        today = datetime.now()
        self.badge.setBadgeLabel_(str(today.hour))
        self.debugText.setStringValue_(today.strftime('%I %p'))

    def setPyTimer(self):
        from threading import Timer
        # today = datetime.now() HERE WE NEED TO SET TIMER FOR APPROPRIATE TIME!
        Timer(3, self.endOfHour, ()).start()
        
    def syncData(self):
        import requests
        
        print 'Syncing start...'

        # request existing day data
        url = "http://127.0.0.1:8000/api/days?synced_before={0}&month=6".format(datetime.now())
        r = requests.get(url)
        days = r.json()
        
        print url
        existing_days = []
        for day in days:
            existing_days.append(day['day'])

        # request existing hour data
        url = "http://127.0.0.1:8000/api/hours?synced_before={0}&day=13".format(datetime.now())
        r = requests.get(url)
        hours = r.json()
        
        print url

        existing_hours = []
        for hour in hours:
            existing_hours.append(hour['hour'])     

        try:
            # open the file to read data from
            fr = open('precious_mytime.js', 'r')
            # load and decode the JSON data
            json_data = json.load(fr)
            # mydata = json.dumps(json_data)
            # r = requests.post(url, data=mydata)
            # print 'Syncing data posted...'
            # print r.text
            for year in json_data:
                for month in json_data[year]:
                    for day in json_data[year][month]:
                        # TODO: api post day to server
                        print 'day API post here...'
                        url = "http://127.0.0.1:8000/api/days/"
                        
                        day_data = {'author':1, 'day':day, 'year':year, 'month':month}
                        
                        if 'reflection' in json_data[year][month][day]:
                            day_data['day_text'] = json_data[year][month][day]['reflection']
                        
                        print url
                        # day_data = json.dumps(day_data)
                        # print day_data
                        r = requests.post(url, data=day_data)
                        print r.text

                        # request day ID
                        url = "http://127.0.0.1:8000/api/days/?day={0}&month={1}&year={2}".format(day,month,year)
                        print url
                        r = requests.get(url)
                        day_data = r.json()
                        day_data = day_data.pop()

                        for hour in json_data[year][month][day]:

                            if hour != 'reflection':
                        
                                # TODO: api post hour to server
                                # check if not reflection
                                print 'hour API post here...'
                                print hour

                                hour_data = {'author':1, 'day':day_data['id'], 'hour':hour}

                                if 'activity' in json_data[year][month][day][hour]:
                                    hour_data['hour_text'] = json_data[year][month][day][hour]['activity']
                                if 'productive' in json_data[year][month][day][hour]:
                                    hour_data['productive'] = json_data[year][month][day][hour]['productive']


                                url = "http://127.0.0.1:8000/api/hours/"
                        
                                print url
                                # day_data = json.dumps(day_data)
                                # print day_data
                                r = requests.post(url, data=hour_data)
                                print r.text
            
            # for hour in existing_hours:
            #     if
            #         hour['day__year'] in json_data and
            #         hour['day__month'] in json_data[hour['day__year']] and
            #         hour['day__day'] in json_data[hour['day__year']][hour['day__month']] and
            #         hour['hour'] in json_data[hour['day__year']][hour['day__month']]
            #
            #
            #
            # if year in json_data and month in json_data[year] and day in json_data[year][month]:
            #
            # for item in json_data:
            #     print item
            
            # close the file
            fr.close
        except IOError:
            # file does not exist yet - set json_data to an empty dictionary
            print 'File not found'
            json_data = {}
    
if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    
    # Initiate the contrller with a XIB
    viewController = PreciousController.alloc().initWithWindowNibName_("Precious")
    
    # Show the window
    viewController.showWindow_(viewController)
    # viewController.badge = app.dockTile()
    # viewController.badge.setBadgeLabel_('1')
    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)        

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()            