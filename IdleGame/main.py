# credit to Bryan Oakley for the stackoverflow answer
# that was the starting point for this effort
# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# and credit to Rob Herman for teaching me how it works

import copy
from ctypes import alignment
import datetime
import json
from re import L
import sys
import tkinter as tk
import ntplib
import configparser

from datetime import datetime, timedelta, timezone
from os import path
from tkinter import filedialog as fd, ttk, font
from tkinter import *

# global vars
global player
global activeskill
global chartemplate
global currentsavefile
global lastsavefile
global seed

player = None
lastsavefile = None
activesavefile = None
savefile = None
activeskill = None

# creates chartemplate to validate save files and make new chars
runningdir = (path.dirname(path.abspath(sys.argv[0])))
with open(runningdir + "\charschema.json") as template_file:
    chartemplate = json.loads(template_file.read())

# prefs.cfg handler
m = "default" # because confighandler can't handle files without section names
def createprefs(lastsavefile, winposx, winposy, winsizex, winsizey):
    print(lastchar)
    prefs[m] = {'lastsave' : lastsavefile,
        'lastchar' : lastchar,
        'windowpositionx' : winposx,
        'windowpositiony' : winposy,
        'windowsizex' : winsizex,
        'windowsizey' : winsizey}
    with open(runningdir + "\prefs.cfg", 'w') as configfile:
        prefs.write(configfile)
    configfile.close()

prefs = configparser.ConfigParser()
if path.exists(runningdir + "\prefs.cfg"):
    try:
        prefs.read(runningdir + "\prefs.cfg")
        savepath = prefs[m]['lastsave']
        lastchar = prefs[m]['lastchar']
        lastskill = prefs[m]['lastskill']
        winposx = prefs[m].getint(['windowpositionx'])
        winposy = prefs[m].getint(['windowpositiony'])
        winsizex = prefs[m].getint(['windowsizex'])
        winsizey = prefs[m].getint(['windowsizey'])
    except:
        pass

else:
    savepath = ""
    lastchar = ""
    winposx = ""
    winposy = ""
    winsizex = ""
    winsizey = ""
    createprefs(savepath, winposx, winposy, winsizex, winsizey)

lastsavefile = prefs[m]['lastsave']

# global functions
def checktime():
    global seed
    c = ntplib.NTPClient()
    response = c.request("us.pool.ntp.org", version=3)
    response.offset
    seed = datetime.fromtimestamp(response.tx_time, timezone.utc)

#validate schema
def validate():
    global player
    # create two empty lists to hold save and template keys
    tmplschema = []
    playerschema = []
    
    # function to scrape the keys from the json
    def keyscrape(schema, list):
        list = list
        for key, value in schema.items():
            list.append(str(key))
            if isinstance(value, dict):
                keyscrape(value, list)

    # calling the function
    keyscrape(chartemplate, tmplschema)
    keyscrape(player, playerschema)

    def buildschema():
        tmpltoplevel = list(chartemplate)
        playertoplevel = list(player)

        # compare top levels, add any missing back to player
        for key in tmpltoplevel:
            if key not in playertoplevel:
                tempdict = dict(chartemplate[key])
                player[key] = tempdict

        # now that top level is in place, go through any missing subkeys
        for key in tmpltoplevel:
            top = chartemplate[key]
            if isinstance(top, list) == False:
                for subkey in top.keys():
                        if not subkey in player[key].keys():
                            player[key][subkey] = chartemplate[key][subkey]

        # update save file
        savechar(False)

    # check if save is valid
    if sorted(tmplschema) == sorted(playerschema):
        return True
    else:
        buildschema()

def loadchar(self, savefile, onload, silent):
    global activesavefile
    global lastsavefile
    global player

    # load save file
    homedir = (path.expanduser( '~' ))
    savedir = (path.join( homedir, 'Documents\Saves'))
    
    if onload == True:
        try:
            print(f"using last save file of {lastsavefile}")
            savefile = lastsavefile
        except:
            print("savefile not set to savepath")
    else:
        if silent == True:
            savefile = activesavefile
            print(f"using active save of {savefile}")
        else:
            try:
                savefile = fd.askopenfilename(title="Load your Character", initialdir=savedir, filetypes=[("Steve's Wicked Idle Game Hero", "*.swig")])
            except:
                pass
    try:
        with open(savefile) as save_file:
            player = json.loads(save_file.read())
            print(f"player is now {player['info']['name']}")
    except:
        pass
    
    try:
        if validate() == True:
            print(f"savefile is {savefile}")
            activesavefile = savefile
            print("validation passed")
            print(f"player name is {player['info']['name']}")
            print(f"activesave is {activesavefile}")
            print(f"last save is {lastsavefile}")
            playchar(self, onload)
        else:
            print("can't update save file")
    except:
        pass

def playchar(self, onload):
    global lastchar
    savechar(False)
    lastchar = player['info']['name']
    if onload == False:
        StartPage.showcontinue(self)
    for skill in skillBox.allskills:
        skillBox.updatescore(skill)

def savechar(saveas):
    global player
    global activesavefile
    print(f"saving {activesavefile}")

    if saveas == None:
        app.destroy()

    if saveas == True:
        try:
            activesavefile = fd.asksaveasfilename(filetypes = [("Steve's Wicked Idle Game Hero", "*.swig")], defaultextension=".swig", initialfile=player['info']['name'] + ".swig")
            if activesavefile != None and activesavefile != '':
                with open(activesavefile, "w") as outfile:
                    json.dump(player, outfile)
                return True
        except:
            pass
    else:
        if activesavefile != None and activesavefile != '':
            with open(activesavefile, "w") as outfile:
                json.dump(player, outfile)



class mainWindow(tk.Tk):
    container = tk.Frame
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # set Title, define style defaults
        self.winfo_toplevel().title("Steve's Wicked Idle Game")
        self.iconbitmap(runningdir + '\windowicon.ico')
        self.geometry('1280x720')

        s = ttk.Style()
        s.theme_use('alt')
        s.configure('.', background='#888888')
        s.configure('TButton', width=50)
        s.configure("Horizontal.TProgressbar", background = "red", lightcolor="white", darkcolor="black")
        self.defaultFont = font.nametofont("TkDefaultFont")
        self.defaultFont.configure(family="DIN Alternate",
                                   size=12)

        # creating a "container" for the frames
        container = tk.Frame(self) 
        container.configure(width=1280, height=720)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        container.grid_propagate(0)
        #container.grid(sticky=NSEW)
        container.pack(fill=BOTH, expand=TRUE)
        
        # initializing frames to an empty array
        self.frames = {} 
        
        # iterating through a tuple of pages
        for F in (StartPage, NewChar, MainGame):
            frame = F(container, self)

            # initializing frame of that object via for loop
            self.frames[F] = frame
            frame.configure(background="#888888")
            frame.grid(row = 0, column = 0, sticky ="nsew")

        self.newcharpage = self.frames[NewChar]
        self.maingame = self.frames[MainGame]
            
        self.show_frame(StartPage)
  
    # to display the current frame passed as parameter
    def show_frame(self, cont):
        print(cont)
        frame = self.frames[cont]
        print(self.frames[cont])
        frame.tkraise()

    

class StartPage(tk.Frame):
    def __init__(self, parent, container):
        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # main label on start page
        label = ttk.Label(self, text ="Welcome to Steve's Idle Game!", font=25)
        label.grid(row = 0, column = 0, padx = 5, pady = 5, ipady=5)

        # new game button
        button1 = ttk.Button(self, text ="New Character",
            command = lambda : self.onclicknew())
        button1.grid(row = 2, column = 0, padx = 5, pady = 5, ipady=5)

        # load game button
        button2 = ttk.Button(self, text ="Load Character",
            command = lambda : loadchar(self, savefile, False, False))
        button2.grid(row = 3, column = 0, padx = 5, pady = 5, ipady=5)

        self.showcontinue()
    
    def onclicknew(self):
        global player
        global activeskill
        if activesavefile != "" and activesavefile != None:
            savechar(False)
        player = None
        activeskill = None
        for skill in skillBox.allskills:
            skill.ms.set(0)
        player = chartemplate
        print(f"player is now {player['info']['name']}")
        app.show_frame(NewChar)      
        

    # continue button to only show up if a last character is detected        
    def showcontinue(self):
        if lastchar != '' and lastchar != None:
            button1 = ttk.Button(self, text='Continue with ' + lastchar,
                command = lambda : self.onclickcontinue())
            button1.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5)
    
    def onclickcontinue(self):
        global lastsavefile
        global activesavefile
             
        print(f"last save is {lastsavefile}")
        loadchar(self, lastsavefile, False, True)
        lastsavefile = activesavefile
                
        app.show_frame(MainGame)  

# second window frame NewChar
class NewChar(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.interface = newCharInterface(self)
        self.interface.grid(row = 0, column = 0, stick = NSEW)
  
        # main game
        button1 = ttk.Button(self, text ="Let's go!",
            command = lambda : self.validatenew())
        button1.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5)
  
        # back to main menu
        button2 = ttk.Button(self, text ="Back", 
            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 2, column = 0, padx = 5, pady = 5, ipady=5)

    def validatenew(self): 
        global player
        global lastsavefile
        totalscore = 0

        for key in player['attributes']:
            totalscore += player['attributes'][key]

        if totalscore == 250:
            player['info']['name'] = self.interface.charnameentry.get()
            if savechar(True) == True:
                lastsavefile = activesavefile
                app.show_frame(MainGame)
        else:
            tk.messagebox.showwarning(title="You're Not Ready!", message="You haven't spent all your points yet!")

class newCharInterface(tk.Frame): 
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.newcharmulti = 1

        self.configure(background="#888888")
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 2)
        self.grid_columnconfigure(2, weight = 1)
        self.grid_columnconfigure(3, weight = 2)
        self.grid_columnconfigure(4, weight = 1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)

        strbox = attrBox(self, "strlevel", "Strength")
        dexbox = attrBox(self, "dexlevel", "Dexterity")
        intbox = attrBox(self, "intlevel", "Intelligence")
        endbox = attrBox(self, "endlevel", "Endurance")
        agibox = attrBox(self, "agilevel", "Agility")
        spdbox = attrBox(self, "spdlevel", "Speed")
        chabox = attrBox(self, "chalevel", "Charisma")
        lucbox = attrBox(self, "luclevel", "Luck")
        wilbox = attrBox(self, "willevel", "Will")
        fthbox = attrBox(self, "fthlevel", "Faith")

        self.freepoints = tk.IntVar()
        self.freepoints.set(150)
        self.strfreepoints = str(self.freepoints.get())
        self.strvarfreepoints = tk.StringVar()
        self.strvarfreepoints.set(self.strfreepoints + " free points left")

        self.strmulti = str(self.newcharmulti)
        self.multilabel = tk.StringVar()
        self.multilabel.set("Multiplier is " + self.strmulti)

        multbutton = ttk.Button(self)
        multbutton.configure(textvar=self.multilabel, width = 30, command = lambda : app.newcharpage.interface.changemult())

        freepointlabel = ttk.Label(self, textvar = self.strvarfreepoints, font=("DIN Alternate",14))
        charnameprompt = ttk.Label(self, text = "Enter your hero's name!", font=("DIN Alternate",14))
        self.charnameentry = ttk.Entry(self, width = 30, font=("DIN Alternate",14), exportselection=False)

        multbutton.grid(row = 2, column = 2, ipady=5)
        freepointlabel.grid(row = 4, column = 2)
        charnameprompt.grid(row = 0, column = 2, sticky = S)
        self.charnameentry.grid(row = 1, column = 2, sticky = N, ipady=5)

        strbox.grid(row = 0, column = 1)    
        dexbox.grid(row = 0, column = 3)
        intbox.grid(row = 1, column = 1)
        endbox.grid(row = 1, column = 3)
        agibox.grid(row = 2, column = 1)
        spdbox.grid(row = 2, column = 3)
        chabox.grid(row = 3, column = 1)
        lucbox.grid(row = 3, column = 3)
        wilbox.grid(row = 4, column = 1)
        fthbox.grid(row = 4, column = 3)

    def freepointscount(self):
        pointsspent = 0
        for attr in attrBox.attrlist:
            pointsspent += attr.attrscore
        pointsleft = 250 - pointsspent
        intpointsleft = pointsleft
        if pointsleft >= 0:
            self.freepoints.set(intpointsleft)
            self.strfreepoints = str(self.freepoints.get())
            self.strvarfreepoints.set(self.strfreepoints + " free points left")
            

    def changemult(self):
        if self.newcharmulti == 1:
            self.newcharmulti = 5
            
        elif self.newcharmulti == 5:
            self.newcharmulti = 10

        elif self.newcharmulti == 10:
            self.newcharmulti = 1

        self.strmulti = str(self.newcharmulti)
        app.newcharpage.interface.multilabel.set("Multiplier is " + self.strmulti)

        for box in attrBox.attrlist:
            box.minus.set("- " + self.strmulti)
            box.plus.set("+ " + self.strmulti)


class attrBox(tk.Frame):
    attrlist = []
    def __init__(self, parent, attrvar, label):
        tk.Frame.__init__(self, parent)
        # adds created instance to attributes list
        self.attrlist.append(self)

        self.strmulti = str(parent.newcharmulti)
        self.minus = tk.StringVar()
        self.plus = tk.StringVar()
        self.minus.set("- " + self.strmulti)
        self.plus.set("+ " + self.strmulti)

        # settings for skillBox frame
        self.configure(background='#888888')
        self.columnconfigure

        global player
        attrkey = chartemplate['attributes']
        self.attrvar = attrvar
        self.attrscore = attrkey[attrvar]
        self.showscore = tk.IntVar()
        self.showscore.set(self.attrscore)
        self.label = label

        self.decrease = ttk.Button(self)
        self.decrease.configure(textvar = self.minus, command = lambda : self.changevalue(parent, False), width = 5)
        self.increase = ttk.Button(self)
        self.increase.configure(textvar = self.plus, command = lambda : self.changevalue(parent, True), width = 5)
        self.attrlabel = ttk.Label(self, text = self.label, font=("DIN Alternate",16))
        self.score = ttk.Label(self, textvariable=self.showscore, font=("DIN Alternate",20))

        self.decrease.grid(row = 0, column = 0, sticky = W)
        self.score.grid(row = 0, column = 1, ipady=10, padx=5, sticky = S)
        self.increase.grid(row = 0, column = 2, sticky = E)
        self.attrlabel.grid(row = 1, column = 0, columnspan=3, sticky = N)

    def changevalue(self, parent, increment):
        
        if increment == True:
            if app.newcharpage.interface.freepoints.get() >= parent.newcharmulti:
                if self.attrscore + parent.newcharmulti < 101:
                    self.attrscore += parent.newcharmulti
                    self.showscore.set(self.attrscore)
                    player['attributes'][self.attrvar] += parent.newcharmulti
                    newCharInterface.freepointscount(app.newcharpage.interface)
                    
                else:
                    tk.messagebox.showwarning(title=None, message="You can't increase an attribute past 100!")
            else:
                tk.messagebox.showwarning(title=None, message="You don't have enough free points!")
        else:
            if self.attrscore - parent.newcharmulti > 0:
                self.attrscore -= parent.newcharmulti
                self.showscore.set(self.attrscore)
                player['attributes'][self.attrvar] -= parent.newcharmulti
                newCharInterface.freepointscount(app.newcharpage.interface)
            else:
                tk.messagebox.showwarning(title=None, message="You can't reduce an attribute below 1!")

class MainGame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, pad=5)
        self.columnconfigure(2, weight=1, pad=5)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(99, weight=1)

        swordrate = 3000
        sword = skillBox(self, "Swords!", "offense", "swordlevel", swordrate)
        sword.grid (row = 1, column = 1, sticky=W)
		
        bowrate = 3000
        bow = skillBox(self, "Bows!", "offense", "bowlevel", bowrate)
        bow.grid (row = 2, column = 1, sticky=W)

        bluntrate = 3000
        blunt = skillBox(self, "Bludgeoning!", "offense", "bluntlevel", bluntrate)
        blunt.grid (row = 3, column = 1, sticky=W)
        
        kniferate = 3000
        knife = skillBox(self, "Knives!", "offense", "knifelevel", kniferate)
        knife.grid (row = 4, column = 1, sticky=W)

        spearrate = 3000
        spear = skillBox(self, "Spears!", "offense", "spearlevel", spearrate)
        spear.grid (row = 5, column = 1, sticky=W)

        
        
        
        
        
        
        
        
        
        
        
        
        conjurationrate = 3000
        conjuration = skillBox(self, "Conjuration!", "magic", "conjlevel", conjurationrate)
        conjuration.grid (row = 1, column = 2, sticky=E)






        # button to go back to start page
        button2 = ttk.Button(self, text ="Go Back",
            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 99, column = 1, columnspan=2, padx = 5, pady = 5, ipady=5, sticky=S)       

    def addskills(self):
        skillBox.updatescore(self)
        
class skillBox(tk.Frame):
    # creates an empty list to store all skillBox instances
    allskills = []
    def __init__(self, parent, displayname, cat, score, rate):
        tk.Frame.__init__(self, parent)
        # adds created instance to allskills list
        self.allskills.append(self)

        self.columnconfigure(0, weight = 3)
        self.columnconfigure(1, weight = 1)

        global player
        self.rate = rate
        self.displayname = displayname
        self.ms = tk.IntVar()
        self.cat = cat
        self.score = score        
        self.showscore = tk.IntVar()

        # settings for skillBox frame
        self.configure(background='#888888')
            
        # widgets
        self.bar = ttk.Progressbar(self, length=300, maximum=self.rate, mode='determinate', variable=self.ms)
        self.scorelabel = ttk.Label(self, textvariable=self.showscore) 
        self.button = ttk.Button(self)
        self.button.configure(text="Start/Stop", command = lambda : self.startstop())
        self.label =ttk.Label(self, text=displayname, width=15)
        # debug label for ms counter, uncomment below and in widget layout section
        #self.mslabel =ttk.Label(self, textvariable=self.ms)

        # widget layout in frame
        self.bar.grid(row = 0, column = 0)
        self.scorelabel.grid(row = 0, column = 1, sticky=SW, padx=20)
        #self.mslabel.grid(row = 1, column = 3)
        self.button.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5)
        self.label.grid(row= 1, column = 1, sticky=N)

    def updatescore(self):
        self.showscore.set(player[self.cat][self.score])

    def increment(self, cat, score):
        print(player[self.cat][self.score])
        self.showscore.set(player[self.cat][self.score] + 1)
        player[cat][score] = self.showscore.get()
        print (player[cat][score])

    def runbar(self, skill, start):
        global activeskill
        self = skill

        while activeskill == self:
            r = timedelta(milliseconds=self.rate)
            updatetime = start + r
            now = datetime.now()

            # math here
            timepassed = now - start
            totalsecs = int(timepassed.seconds)
            totalmis =  int(timepassed.microseconds)
            totalms = float(totalmis/1000000)
            secondspassed = float(totalsecs + totalms)
            mspassed = int(secondspassed*1000)
            
            # update bar with math
            try:
                self.ms.set(mspassed)
                mainWindow.update(self)

            # ignore TclError that happens when exiting because tkinter fuckery
            except(TclError):
                pass
                exit()

            if now >= updatetime:
                # once timer completes, update skillscore for skillBox                       
                if mspassed >= self.rate:
                    self.increment(self.cat, self.score)
                start = datetime.now()

    def startstop(self):
        global activeskill
        self.skillname = self.score
    
        if activeskill is None: # if nothing running, run selected skill
            activeskill = copy.copy(self)
            start = datetime.now()
            self.runbar(activeskill, start)

        elif activeskill.skillname != self.skillname: # check if something else is running
            activeskill.ms.set(0)
            activeskill = None
            activeskill = copy.copy(self)
            start = datetime.now()
            self.runbar(activeskill, start)

        elif activeskill.skillname == self.skillname:  # if skill already running, stop it
            self.ms.set(0)
            activeskill = None

app = mainWindow()
if lastsavefile != None and lastsavefile != "":
    loadchar(app, lastsavefile, True, True)

def closingtime():
    if player != None and player != chartemplate:
        # silently saves file on exit
        savechar(False)
        # saves prefs.cfg settings
        savepath = activesavefile
        winsizex = app.winfo_width()
        winsizey = app.winfo_height()
        winposx = app.winfo_x()
        winposy = app.winfo_y()
        createprefs(savepath, winposx, winposy, winsizex, winsizey)        
    app.destroy()

app.protocol("WM_DELETE_WINDOW", closingtime)
app.mainloop()