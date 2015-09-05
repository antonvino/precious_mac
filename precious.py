from Cocoa import *
from Foundation import NSObject
import json, os, signal, time
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
        response = r.json()
        if 'token' in response:
            self.token = response['token']
            self.email = auth_data['username']
        else:
            print '[Auth error] {0}'.format(r.text)
            error = 'E-mail or password do not match.'
            if 'non_field_errors' in response:
                error = response['non_field_errors'][0]
            raise ValueError(error)

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

        self.email = response['email']
        # token = r.json()
        # if 'token' in token:
        #     self.token = token['token']
        #     self.email = auth_data['username']


class PreciousData():

    def __init__(self):
        pass

    def load(self, year = None, month = None, day = None, hour = None):
        """
        Loads the data from JSON file according to given date

        :return: A tuple: reflection, activity, productive
        """

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
            print '[Data:Error] File not found'
            json_data = {}

        reflection = None
        activity = None
        productive = None
        if year in json_data and month in json_data[year] and day in json_data[year][month]:
            if 'reflection' in json_data[year][month][day]:
                reflection = json_data[year][month][day]['reflection']
            if hour in json_data[year][month][day]:
                activity = json_data[year][month][day][hour]['activity']
                productive = json_data[year][month][day][hour]['productive']

        return reflection, activity, productive

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

    def save(self, type, productive = 1, activity = None, reflection = None, year = None, month = None, day = None, hour = None):
        """
        Saves the data for Hour or Day in a JSON file

        :param type: `day` or `hour`
        :param productive: 1/2/3 as in low/med/high
        :param activity: text about activity
        :param reflection: reflection of the day

        other parameters are self-explanatory and should be numbers
        """

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
            print '[Data:Error] Could not open the file precious_mytime.js'
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
        # logging day
        elif type == 'day':
            # append the hour data to the appropriate decoded node of the json_data
            json_data[year][month][day].update({
                'reflection': reflection
            })
        try:
            # open the file to rewrite data
            fw = open('precious_mytime.js', 'w')
            # JSON dump of the data
            json.dump(json_data, fw)
            print '[Data] {0} saved'.format(type)
            # close the file
            fw.close
        except IOError:
            print '[Data:Error] Could not open the file precious_mytime.js'

    def sync(self):
        """
        Syncs the data with Web API of Precious Web
        Using Python Requests
        Requires user instance to be authenticated (i.e. to have a valid token)

        TODO: Sync only the recent data otherwise it's too slow to sync the whole file
        """

        assert(user.token is not None)

        import requests

        print '[Data] Syncing start...'

        headers = {'Authorization': 'Token {0}'.format(user.token)}

        url = SITE_URL + 'api/users?email={0}'.format(user.email)
        print '[API] Authorized user {0}'.format(url)
        r = requests.get(url, headers=headers)
        users = r.json()
        user_data = users.pop()

        url = SITE_URL + 'api/users/{0}'.format(user_data['id'])
        print '[API] Authorized user detailed {0}'.format(url)
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
        print '[API] {0}'.format(url)
        recent_days = []
        for day in days:
            recent_days.append(day['day'])
        # print repr(recent_days)

        # request recently logged hours data
        url = SITE_URL + 'api/hours?synced_after={0}&author={1}'.format(dt, user.id)
        r = requests.get(url, headers=headers)
        hours = r.json()
        print url
        recent_hours = []
        for hour in hours:
            recent_hours.append(hour['hour'])
        # print repr(recent_hours)

        # open the file to read data from
        fr = open('precious_mytime.js', 'r')
        # load and decode the JSON data
        json_data = json.load(fr)

        for year in json_data:
            for month in json_data[year]:
                for day in json_data[year][month]:

                    print '[API] Day POST'

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

                            print '[API] Hour POST'

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

    def windowDidLoad(self):
        """
        Initializing the main window controller
        Setting default field values and resetting everything
        """

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
        """
        Reads help text from a faq.txt local file and puts it in the help form
        TODO: Webview of the HTML page instead?
        """
        try:
            # open the file to read data
            fw = open('faq.txt', 'r')
            # update help text
            self.helpText.setStringValue_(fw.read())
            # close the file
            fw.close
        except IOError:
            print '[File] File faq.txt was not found.'
    
    def reloadTime(self):
        """
        Takes current timestamp and updates the date/time data
        """
        self.curr_time = datetime.fromtimestamp(self.curr_timestamp)
        self.year = self.curr_time.year
        self.month = self.curr_time.month
        self.day = self.curr_time.day
        self.hour = int(self.curr_time.strftime('%H')) # need a 24 hour        

    def updateDisplayHour(self):
        """
        Updates the displayed date & hour in the interface
        """
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

    def updateDisplayDay(self):
        """
        Updates the displayed date in the interface
        """
        self.hourLabel.setStringValue_(self.curr_time.strftime('%a %d %b, %I %p'))
        self.dayLabel.setStringValue_(self.curr_time.strftime('%a %d %b'))
        self.dayButton.setAttributedTitle_(self.curr_time.strftime('%a %d %b'))
        if self.reflection:
            self.dayField.setStringValue_(self.reflection)
            self.dayLabel.setTextColor_(NSColor.blackColor())
        else:
            self.dayField.setStringValue_('')
            self.dayLabel.setTextColor_(NSColor.redColor())

    def switchDate(self):
        """
        Loads the hour & day data and calls display update
        """
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

    def clearData(self):
        """
        Sets default data for Day & Hour fields
        """
        self.activity = None
        self.reflection = None
        self.productive = 1

    def loadData(self, year = None, month = None, day = None, hour = None):
        """
        Loads data for Day & Hour fields
        """
        self.reflection, self.activity, self.productive = precious_data.load(year, month, day, hour)

    ####
    # Timed things

    def endOfHour(self):
        print '[Timer] Called by timer!'
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

    ####
    # Interface elements actions

    @objc.IBAction
    def productive_(self, sender):
        """
        Operates the SelectedSegment choice of how productive the hour has been
        """
        self.productive = sender.selectedSegment()

    @objc.IBAction
    def prevHour_(self, sender):
        """
        Loads the previous hour data in the hour window
        """
        # decrement time
        self.curr_timestamp -= 3600
        self.switchDate()
        print '[Action] prev hour'

    @objc.IBAction
    def nextHour_(self, sender):
        """
        Loads the next hour data in the hour window
        """
        # increment the time
        self.curr_timestamp += 3600
        self.switchDate()
        print '[Action] next hour'

    @objc.IBAction
    def prevDay_(self, sender):
        """
        Loads the previous day data in the day window
        """
        # decrement the time
        self.curr_timestamp -= 86400
        self.switchDate()
        print '[Action] prev day'

    @objc.IBAction
    def nextDay_(self, sender):
        """
        Loads the next day data in the day window
        """
        # increment the time
        self.curr_timestamp += 86400
        self.switchDate()
        print '[Action] next day'

    # submit the data
    @objc.IBAction
    def submitHour_(self, sender):
        """
        Submits the hour log
        Removes the app icon badge
        Makes the hour label black
        Starts and stops the spinny thing
        """

        # start the progress spin
        self.hourProgress.startAnimation_(self)
        
        # getting the text from text fields
        self.activity = self.hourField.stringValue()
        # self.reflection = self.dayField.stringValue()

        # log the hour
        precious_data.save(
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
        """
        Submits the day log
        Makes the day label black
        Starts and stops the spinny thing
        """

        # start the progress spin
        self.dayProgress.startAnimation_(self)
        # getting the text from text field
        self.reflection = self.dayField.stringValue()
        
        precious_data.save(
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

    @objc.IBAction
    def authenticate_(self, sender):
        """
        Authenticates user
        Syncs the Hour & Day data with the web API if authenticated
        Shows errors or success message
        Starts and stops the spinny thing
        """

        # play intro sound
        # sound = NSSound.soundNamed_('Frog')
        # sound.play()
        # start the spin
        self.syncProgress.startAnimation_(self)
        # hide the stats and result
        self.syncError.setHidden_(True)
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
            print '[Action:Error] Halt auth flow'
            print e
            self.syncError.setTextColor_(NSColor.redColor())
            self.syncError.setStringValue_(str(e))
            self.syncError.setHidden_(False)
            # stop the spin
            self.syncProgress.stopAnimation_(self)

        # if authenticated - sync data
        if user.token is not None and auth_success:
            try:
                precious_data.sync()
                # success!
                self.syncError.setTextColor_(NSColor.blackColor())
                self.syncError.setStringValue_('All synced.')
                self.syncError.setHidden_(False)
                # play success sound
                sound = NSSound.soundNamed_('Pop')
                sound.play()
                # self.statsButton.setEnabled_(True)
                self.statsButton.setHidden_(False)
                # stop the spin
                self.syncProgress.stopAnimation_(self)
            except Exception, e:
                print '[Action:Error] Could not sync: {0}'.format(e)
                self.syncError.setTextColor_(NSColor.redColor())
                self.syncError.setStringValue_('Could not sync.')
                self.syncError.setHidden_(False)
                # stop the spin
                self.syncProgress.stopAnimation_(self)

    @objc.IBAction
    def signUp_(self, sender):
        """
        Registers user
        Shows errors or success message
        Starts and stops the spinny thing
        Opens the sync window on success
        """

        # start the spin
        self.signUpProgress.startAnimation_(self)

        email = self.signUpEmailField.stringValue()
        username = self.signUpUsernameField.stringValue()
        password = self.signUpPasswordField.stringValue()

        self.signUpEmailError.setHidden_(True)
        self.signUpUsernameError.setHidden_(True)
        self.signUpError.setHidden_(True)

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
            # tell that user needs to confirm his e-mail
            print '[Action] User registered'
            self.signUpError.setStringValue_('Done! A confirmation request has been sent to your e-mail.')
            self.signUpError.setTextColor_(NSColor.blackColor())
            self.signUpError.setHidden_(False)
            # minimize the window and show login
            # self.signUpWindow.close()
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
                self.signUpEmailError.setHidden_(False)
            # username error
            if e[1]:
                # self.signUpUsernameField.setTextColor_(NSColor.redColor())
                self.signUpUsernameError.setStringValue_(str(e[1]))
                self.signUpUsernameError.setHidden_(False)
            # general error conclusion
            print '[Action:Error] Could not create a new account.'
            self.signUpError.setStringValue_('Could not create an account.')
            self.signUpError.setTextColor_(NSColor.redColor())
            self.signUpError.setHidden_(False)
            # stop the spin
            self.signUpProgress.stopAnimation_(self)

    @objc.IBAction
    def openStats_(self, sender):
        """
        Opens stats web page in a browser
        Assumes the user is logged in on the web app
        """
        print '[WEB] Opening stats...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_(SITE_URL))

    @objc.IBAction
    def openWebApp_(self, sender):
        """
        Opens precious_web app main page
        """
        print '[WEB] Opening web app...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_('http://www.antonvino.com/precious/'))

    @objc.IBAction
    def openPasswordReset_(self, sender):
        """
        Opens reset password page in web app
        Called when user forgot password from the login window
        """
        print '[WEB] Opening web app password reset...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_(SITE_URL + 'accounts/password-reset/'))

    @objc.IBAction
    def openPortfolio_(self, sender):
        """
        Opens author's portfolio in a browser
        """
        print '[WEB] Opening portfolio...'
        sharedWorkspace = NSWorkspace.sharedWorkspace()
        sharedWorkspace.openURL_(NSURL.URLWithString_('http://www.antonvino.com'))

if __name__ == "__main__":

    app = NSApplication.sharedApplication()
    
    # Initiate the controller with a XIB
    viewController = PreciousController.alloc().initWithWindowNibName_("Precious")

    user = PreciousUser()
    precious_data = PreciousData()

    # Show the window
    viewController.showWindow_(viewController)
    # viewController.badge = app.dockTile()
    # viewController.badge.setBadgeLabel_('1')

    # Bring app to top
    NSApp.activateIgnoringOtherApps_(True)        

    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()            