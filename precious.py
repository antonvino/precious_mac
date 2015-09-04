from Cocoa import *
from Foundation import NSObject
import json, signal, os, pprint, time
from datetime import datetime, timedelta

SITE_URL = 'http://127.0.0.1:8000/'

class PreciousUser():

    def __init__(self):
        self.token = None

    def authenticate(self, email, password):
        print 'authenticating...'
        import requests

        # construct auth data using the fields
        auth_data = {
            'username': email,
            'password': password
        }

        # get token for the user
        url = SITE_URL + 'api/token-auth/'
        print url
        print auth_data
        r = requests.post(url, data=auth_data)
        token = r.json()
        if 'token' in token:
            self.token = token['token']
            self.email = auth_data['username']
        else:
            raise ValueError('E-mail or password do not match')

    def create(self, email, username, password):
        print 'creating an account...'
        import requests

        # construct auth data using the fields
        auth_data = {
            'email': email,
            'username': username,
            'password': password
        }

        # get token for the user
        url = SITE_URL + 'api/sign-up/'
        print url
        print auth_data
        r = requests.post(url, data=auth_data)
        print r.text

        response = r.json()
        if 'id' not in response:
            # Django sends errors for each field
            if 'email' not in response:
                response['email'] = ['']
            if 'username' not in response:
                response['username'] = ['']
            raise ValueError(response['email'][0], response['username'][0])
        # token = r.json()
        # if 'token' in token:
        #     self.token = token['token']
        #     self.email = auth_data['username']


class PreciousController(NSWindowController):
    # Hour window
    hourLabel = objc.IBOutlet()
    hourField = objc.IBOutlet()
    hourButton = objc.IBOutlet()
    hourProgress = objc.IBOutlet()
    hourSegment = objc.IBOutlet()

    # Day window
    dayLabel = objc.IBOutlet()
    dayField = objc.IBOutlet()
    dayButton = objc.IBOutlet()
    dayProgress = objc.IBOutlet()

    # Sign up window
    signUpWindow = objc.IBOutlet()
    signUpEmailField = objc.IBOutlet()
    signUpUsernameField = objc.IBOutlet()
    signUpPasswordField = objc.IBOutlet()
    signUpProgress = objc.IBOutlet()
    signUpButton = objc.IBOutlet()
    signUpEmailError = objc.IBOutlet()
    signUpUsernameError = objc.IBOutlet()
    signUpError = objc.IBOutlet()

    # sync window
    syncWindow = objc.IBOutlet()
    usernameField = objc.IBOutlet()
    passwordField = objc.IBOutlet()
    syncProgress = objc.IBOutlet()
    syncButton = objc.IBOutlet()
    syncError = objc.IBOutlet()
    statsButton = objc.IBOutlet()

    # Miscellaneous items
    helpText = objc.IBOutlet()

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

        # init the help text
        self.setHelpText()


    def setHelpText(self):
        try:
            # open the file to read data
            fw = open('readme.txt', 'r')
            # update help text
            self.helpText.setStringValue_(fw.read())
            # close the file
            fw.close
        except IOError:
            print 'File readme.txt was not found'
    
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
        assert(user.token is not None)

        import requests
        
        print 'Syncing start...'

        headers = {'Authorization': 'Token {0}'.format(user.token)}

        url = SITE_URL + 'api/users?email={0}'.format(user.email)
        print '[Authorized user] {0}'.format(url)
        r = requests.get(url, headers=headers)
        users = r.json()
        user_data = users.pop()

        url = SITE_URL + 'api/users/{0}'.format(user_data['id'])
        print '[Authorized user detailed] {0}'.format(url)
        r = requests.get(url, headers=headers)
        user_data = r.json()
        user.username = user_data['username']
        user.email = user_data['email']
        user.id = user_data['id']

        # 3 days ago datetime
        dt = datetime.now() - timedelta(days=3)

        # request recently logged days
        url = SITE_URL + 'api/days?synced_after={0}&author={1}'.format(dt, user.id)
        r = requests.get(url, headers=headers)
        days = r.json()
        print url
        recent_days = []
        for day in days:
            recent_days.append(day['day'])
        print repr(recent_days)

        # request recently logged hours data
        url = SITE_URL + 'api/hours?synced_after={0}&author={1}'.format(dt, user.id)
        r = requests.get(url, headers=headers)
        hours = r.json()
        print url
        recent_hours = []
        for hour in hours:
            recent_hours.append(hour['hour'])
        print repr(recent_hours)

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

                    print '[Day API POST]'

                    # construct the day data dict
                    day_data = {'author':user.id, 'day':day, 'year':year, 'month':month}
                    if 'reflection' in json_data[year][month][day]:
                        day_data['day_text'] = json_data[year][month][day]['reflection']

                    this_day = {}
                    # if day has not been logged in the last 3 days - try to add a new one
                    if day not in recent_days:
                        url = SITE_URL + 'api/days/'
                        print url
                        # POST new day
                        r = requests.post(url, data=day_data, headers=headers)


                    # otherwise update the existing one
                    else:
                        url = SITE_URL + 'api/days/?day={0}&month={1}&year={2}&author={3}'.format(day,month,year,user.id)
                        print url
                        r = requests.get(url, header=headers)
                        this_day = r.json()
                        this_day = this_day.pop()
                        # the PUT url
                        url = SITE_URL + 'api/days/{0}'.format(this_day['id'])
                        print url
                        # PUT (update) the day
                        r = requests.put(url, data=day_data, headers=headers)

                    # Request result debug
                    print r.text

                    # request day ID
                    # TODO refactor into one function with above
                    if 'id' not in this_day:
                        url = SITE_URL + 'api/days/?day={0}&month={1}&year={2}&author={3}'.format(day,month,year,user.id)
                        print url
                        r = requests.get(url, headers=headers)
                        this_day = r.json()
                        this_day = this_day.pop()

                    for hour in json_data[year][month][day]:

                        if hour != 'reflection':

                            print '[Hour API POST]'

                            hour_data = {'author':user.id, 'day':this_day['id'], 'hour':hour}

                            if 'activity' in json_data[year][month][day][hour]:
                                hour_data['hour_text'] = json_data[year][month][day][hour]['activity']
                            if 'productive' in json_data[year][month][day][hour]:
                                hour_data['productive'] = json_data[year][month][day][hour]['productive']

                            url = SITE_URL + 'api/hours/'

                            print url
                            # day_data = json.dumps(day_data)
                            # print day_data
                            r = requests.post(url, data=hour_data, headers=headers)
                            print r.text

        # close the file
        fr.close
        # except IOError:
        #     # file does not exist yet - set json_data to an empty dictionary
        #     print 'File not found'
        #     json_data = {}

    ######
    # AUTH

    @objc.IBAction
    def authenticate_(self, sender):
        # play intro sound
        # sound = NSSound.soundNamed_('Frog')
        # sound.play()
        # start the spin
        self.syncProgress.startAnimation_(self)
        # hide the stats and result
        self.syncError.setStringValue_('')
        # self.statsButton.setEnabled_(False)
        self.statsButton.setHidden_(True)

        email = self.usernameField.stringValue()
        password = self.passwordField.stringValue()

        auth_success = False
        print email
        try:
            user.authenticate(
                email=email,
                password=password)
            auth_success = True

        except ValueError, e:
            print 'Could not authorize'
            print e
            self.syncError.setTextColor_(NSColor.redColor())
            self.syncError.setStringValue_(str(e))
            # stop the spin
            self.syncProgress.stopAnimation_(self)

        # if authenticated - sync data
        if user.token is not None and auth_success:
            try:
                self.syncData()
                # success!
                self.syncError.setTextColor_(NSColor.blackColor())
                self.syncError.setStringValue_('All synced.')
                # play success sound
                sound = NSSound.soundNamed_('Pop')
                sound.play()
                # self.statsButton.setEnabled_(True)
                self.statsButton.setHidden_(False)
                # stop the spin
                self.syncProgress.stopAnimation_(self)
            except Exception, e:
                print 'Could not sync: {0}'.format(e)
                self.syncError.setTextColor_(NSColor.redColor())
                self.syncError.setStringValue_('Could not sync')
                # stop the spin
                self.syncProgress.stopAnimation_(self)


    @objc.IBAction
    def signUp_(self, sender):
        # start the spin
        self.signUpProgress.startAnimation_(self)

        email = self.signUpEmailField.stringValue()
        username = self.signUpUsernameField.stringValue()
        password = self.signUpPasswordField.stringValue()

        self.signUpEmailError.setStringValue_('')
        self.signUpUsernameError.setStringValue_('')
        self.signUpError.setStringValue_('')

        print email
        try:
            user.create(
                email=email,
                username=username,
                password=password
            )
            # auth after
            # self.user.authenticate(
            #     email=email,
            #     password=password
            # )
            # self.user.email = email
            # self.user.password = password


            # stop the spin
            self.signUpProgress.stopAnimation_(self)
            # minimize the window and show login
            self.signUpWindow.close()
            self.syncWindow.makeKeyAndOrderFront_(self)
            # fill in the email field
            self.usernameField.setStringValue_(email)
            # self.passwordField.setStringValue(password)

        except ValueError, e:
            print e
            # email error
            if e[0]:
                # self.signUpEmailField.setTextColor_(NSColor.redColor())
                self.signUpEmailError.setStringValue_(str(e[0]))
            # username error
            if e[1]:
                # self.signUpUsernameField.setTextColor_(NSColor.redColor())
                self.signUpUsernameError.setStringValue_(str(e[1]))
            # general error conclusion
            print 'Could not create a new account'
            self.signUpError.setStringValue_('Could not create an account')
            # stop the spin
            self.signUpProgress.stopAnimation_(self)


    @objc.IBAction
    def openStats_(self, sender):
        print 'Opening stats...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_(SITE_URL))

    @objc.IBAction
    def openPortfolio_(self, sender):
        print 'Opening portfolio...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_('http://www.antonvino.com'))

    @objc.IBAction
    def openWebApp_(self, sender):
        print 'Opening web app...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_('http://www.antonvino.com/precious/'))


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    
    # Initiate the controller with a XIB
    viewController = PreciousController.alloc().initWithWindowNibName_("Precious")

    user = PreciousUser()

    # Show the window
    viewController.showWindow_(viewController)
    # viewController.badge = app.dockTile()
    # viewController.badge.setBadgeLabel_('1')
    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)        

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()            