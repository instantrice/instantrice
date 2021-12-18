# credit to Bryan Oakley for the stackoverflow answer
# that was the starting point for this effort
# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# and credit to Rob Herman for teaching me how it works

import copy
import datetime
import json
import sys
import tkinter as tk
import ntplib
import configparser
#from inventory import drawinventory
import globals as g
import inventory as i

from datetime import datetime, timedelta, timezone
from os import path
from tkinter import filedialog as fd, ttk, font
from tkinter import *
from PIL import ImageTk,Image


# global vars
g.setglobals()

# creates g.chartemplate to validate save files and make new chars
g.runningdir = (path.dirname(path.abspath(sys.argv[0])))
with open(g.runningdir + "\charschema.json") as template_file:
    g.chartemplate = json.loads(template_file.read())

# gets item db
with open(g.runningdir + "\itemdb.json") as template_file:
    g.itemdb = json.loads(template_file.read())

# builds xp table
xpfile = open(g.runningdir + r"\xptable.txt", "r")
for line in xpfile:
    g.xptable.append(int(line))
xpfile.close()

# prefs.cfg handler
m = "default" # because confighandler can't handle files without section names
def createprefs(savepath, winposx, winposy, winsizex, winsizey):
    prefs[m] = {'lastsave' : g.lastsavefile,
        'lastchar' : lastchar,
        'windowpositionx' : winposx,
        'windowpositiony' : winposy,
        'windowsizex' : winsizex,
        'windowsizey' : winsizey}
    with open(g.runningdir + "\prefs.cfg", 'w') as configfile:
        prefs.write(configfile)
    configfile.close()

prefs = configparser.ConfigParser()
if path.exists(g.runningdir + "\prefs.cfg"):
    try:
        prefs.read(g.runningdir + "\prefs.cfg")
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

g.lastsavefile = prefs[m]['lastsave']

# global functions
def checktime():
    c = ntplib.NTPClient()
    response = c.request("us.pool.ntp.org", version=3)
    response.offset
    g.seed = datetime.fromtimestamp(response.tx_time, timezone.utc)

#validate schema
def validate():
    g.player
    # create two empty lists to hold save and template keys
    tmplschema = []
    playerschema = []
    
    # function to scrape the keys from the json
    def keyscrape(schema, list):
        list = []
        for key, value in schema.items():
            list.append(str(key))
            if isinstance(value, dict):
                keyscrape(value, list)

    # calling the function
    keyscrape(g.chartemplate, tmplschema)
    keyscrape(g.player, playerschema)

    def buildschema():
        tmpltoplevel = list(g.chartemplate)
        playertoplevel = list(g.player)

        try:
            # compare top levels, add any missing back to player
            for key in tmpltoplevel:
                if key not in playertoplevel:
                    tempdict = dict(g.chartemplate[key])
                    g.player[key] = tempdict
            
            # fix inventory from when it was a list
            if isinstance(g.player['inventory'], list) == True:
                g.player['inventory'] = g.chartemplate['inventory']
            else:
                print("list didn't eval as list")

            # now that top level is in place, go through any missing subkeys
            for key in tmpltoplevel:
                top = g.chartemplate[key]
                for subkey in top.keys():
                    if not subkey in g.player[key].keys():
                        g.player[key][subkey] = g.chartemplate[key][subkey]
            # update save file
            savechar(False)
            return True
        except:
            return False

    # check if save is valid
    if sorted(tmplschema) == sorted(playerschema):
        if isinstance(g.player['inventory'], list) == True:
            if buildschema() == True:
                return True
        else:
            return True
    else:
        buildschema()

def loadchar(self, savefile, onload, silent):
    #global g.activesavefile
    #global g.lastsavefile

    # load save file
    homedir = (path.expanduser( '~' ))
    savedir = (path.join( homedir, 'Documents\Saves'))
    
    if onload == True:
        try:
            savefile = g.lastsavefile
        except:
            print("savefile not set to savepath")
    else:
        if silent == True:
            savefile = g.activesavefile
        else:
            savefile = fd.askopenfilename(title="Load your Character", initialdir=savedir, filetypes=[("Steve's Wicked Idle Game Hero", "*.swig")])
            if savefile == '':
                savefile = g.lastsavefile
    try:
        g.activesavefile = savefile
        with open(g.activesavefile) as save_file:
            g.player = json.loads(save_file.read())
            lambda : i.itemBox.lazyinit(self)
            g.app.maingame.tabs.lazyinit()
    except:
        print("error in try block 181")
        pass
    
    try:
        if validate() == True:
            g.activesavefile = savefile
            playchar(self, onload)
        else:
            print("can't update save file")
    except:
        print("save file is None")
        pass

def playchar(self, onload):
    global lastchar
    savechar(False)
    lastchar = g.player['info']['name']
    if onload == False:
        StartPage.showcontinue(self)
    for skill in skillBox.allskills:
        skillBox.updatescore(skill)

def savechar(saveas):
    print(f"saving {g.activesavefile}")

    if saveas == None:
        g.app.destroy()

    if saveas == True:
        try:
            g.activesavefile = fd.asksaveasfilename(filetypes = [("Steve's Wicked Idle Game Hero", "*.swig")], defaultextension=".swig", initialfile=g.player['info']['name'] + ".swig")
            if g.activesavefile != None and g.activesavefile != '':
                with open(g.activesavefile, "w") as outfile:
                    json.dump(g.player, outfile)
                return True
        except:
            pass
    else:
        if g.activesavefile == None:
            print(f"save and activesave are none, last save: {g.lastsavefile}")
            g.activesavefile = g.lastsavefile
        if g.activesavefile != None and g.activesavefile != '':
            print(f"activesave was valid, saving {g.activesavefile}")
            with open(g.activesavefile, "w") as outfile:
                json.dump(g.player, outfile)
            return True
        else:
            print(f"active save is set to {g.activesavefile}")
            return True



class mainWindow(tk.Tk):
    container = tk.Frame
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # set Title, define style defaults
        self.winfo_toplevel().title("Steve's Wicked Idle Game")
        self.iconbitmap(g.runningdir + '\windowicon.ico')
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

        savefile = None
        # load game button
        button2 = ttk.Button(self, text ="Load Character",
            command = lambda : loadchar(self, savefile, False, False))
        button2.grid(row = 3, column = 0, padx = 5, pady = 5, ipady=5)

        self.showcontinue()
    
    def onclicknew(self):
        #global g.player
        #global g.activeskill
        if g.activesavefile != "" and g.activesavefile != None:
            savechar(False)
        g.player = None
        g.activeskill = None
        for skill in skillBox.allskills:
            skill.ms.set(0)
        g.player = g.chartemplate
        print(f"player is now {g.player['info']['name']}")
        g.app.show_frame(NewChar)      
        

    # continue button to only show up if a last character is detected        
    def showcontinue(self):
        if lastchar != '' and lastchar != None:
            button1 = ttk.Button(self, text='Continue with ' + lastchar,
                command = lambda : self.onclickcontinue())
            button1.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5)
    
    def onclickcontinue(self):
        #global g.lastsavefile             
        print(f"last save is {g.lastsavefile}")
        if lastchar == g.player['info']['name']:
            g.app.show_frame(MainGame)
        else:
            loadchar(self, g.lastsavefile, False, True)
            g.lastsavefile = g.activesavefile

        g.app.show_frame(MainGame)  

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
        button2 = ttk.Button(self, text ="Main Menu", 
            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 2, column = 0, padx = 5, pady = 5, ipady=5)

    def validatenew(self): 
        totalscore = 0

        for key in g.player['attributes']:
            totalscore += g.player['attributes'][key]

        if totalscore == 250:
            g.player['info']['name'] = self.interface.charnameentry.get()
            if savechar(True) == True:
                g.lastsavefile = g.activesavefile
                g.app.show_frame(MainGame)
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
        multbutton.configure(textvar=self.multilabel, width = 30, command = lambda : g.app.newcharpage.interface.changemult())

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
        g.app.newcharpage.interface.multilabel.set("Multiplier is " + self.strmulti)

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

        # settings for attrBox frame
        self.configure(background='#888888')
        self.columnconfigure

        #global g.player
        attrkey = g.chartemplate['attributes']
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
            if g.app.newcharpage.interface.freepoints.get() >= parent.newcharmulti:
                if self.attrscore + parent.newcharmulti < 101:
                    self.attrscore += parent.newcharmulti
                    self.showscore.set(self.attrscore)
                    g.player['attributes'][self.attrvar] += parent.newcharmulti
                    newCharInterface.freepointscount(g.app.newcharpage.interface)
                    
                else:
                    tk.messagebox.showwarning(title=None, message="You can't increase an attribute past 100!")
            else:
                tk.messagebox.showwarning(title=None, message="You don't have enough free points!")
        else:
            if self.attrscore - parent.newcharmulti > 0:
                self.attrscore -= parent.newcharmulti
                self.showscore.set(self.attrscore)
                g.player['attributes'][self.attrvar] -= parent.newcharmulti
                newCharInterface.freepointscount(g.app.newcharpage.interface)
            else:
                tk.messagebox.showwarning(title=None, message="You can't reduce an attribute below 1!")

class MainGame(tk.Frame):
    def __init__(self, parent, controller): #controller does nothing, but python bitches if undefined
        tk.Frame.__init__(self, parent)
        self.tabs = self.mainTabs(self)
        self.tabs.pack(fill=BOTH, expand=TRUE)

    class mainTabs(ttk.Notebook):
        def __init__(self, parent):
            ttk.Notebook.__init__(self, parent)
        
            self.tab1 = ttk.Frame(self)
            self.tab2 = ttk.Frame(self)

            self.add(self.tab1, text = "test tab")
            self.add(self.tab2, text = "production tab")

            self.tab1.columnconfigure(0, weight=1)
            self.tab1.columnconfigure(1, weight=1, pad=5)
            self.tab1.columnconfigure(2, weight=1, pad=5)
            self.tab1.columnconfigure(3, weight=1)
            self.tab1.rowconfigure(99, weight=1)

            self.tab2.columnconfigure(0, weight = 1)
            self.tab2.rowconfigure(0, weight = 1)


            #fucktkinter = tk.Label(self.tab2, text = "I bet this works")
            #fucktkinter.grid(row = 0, column = 0)   


        def lazyinit(self):
            i.itemBox.lazyinit(self)
            self.drawinventory()
            print(i.itemBox.playerinv)
        
        def drawinventory(self):
            x = 0
            y = 0
            for k in g.player['inventory'].keys():

                b = i.itemBox(self.tab2, k)

                if y < 4:
                    b.grid(row = x, column = y)
                    y += 1
                    print(f"itembox {b} should be at column {y} row {x}")
                else:
                    y = 0
                    x += 1
                    b.grid(row = x, column = y)
                    print(f"itembox {b} should be at column {y} row {x}")

        

            swordrate = 3000
            sword = skillBox(self.tab1, "Swords!", "offense", "swordlevel", swordrate)
            sword.grid (row = 1, column = 1, sticky=W)
            
            bowrate = 3000
            bow = skillBox(self.tab1, "Bows!", "offense", "bowlevel", bowrate)
            bow.grid (row = 2, column = 1, sticky=W)

            bluntrate = 3000
            blunt = skillBox(self.tab1, "Bludgeoning!", "offense", "bluntlevel", bluntrate)
            blunt.grid (row = 3, column = 1, sticky=W)
            
            kniferate = 3000
            knife = skillBox(self.tab1, "Knives!", "offense", "knifelevel", kniferate)
            knife.grid (row = 4, column = 1, sticky=W)

            spearrate = 3000
            spear = skillBox(self.tab1, "Spears!", "offense", "spearlevel", spearrate)
            spear.grid (row = 5, column = 1, sticky=W)

            
            
            
            
            
            
            
            
            
            
            
            
            conjurationrate = 3000
            conjuration = skillBox(self.tab1, "Conjuration!", "magic", "conjlevel", conjurationrate)
            conjuration.grid (row = 1, column = 2, sticky=E)



            addtoinv = ttk.Button(self.tab1, text="add item", command = lambda : self.invframe.additem('3', 1, True))
            addtoinv.grid(row = 98, column = 1)

            # button to go back to start page
            button2 = ttk.Button(self.tab1, text ="Main Menu",
                command = lambda : g.app.show_frame(StartPage))
            button2.grid(row = 99, column = 1, columnspan=2, padx = 5, pady = 5, ipady=5, sticky=S)



class skillBox(tk.Frame):
    # creates an empty list to store all skillBox instances
    allskills = []
    def __init__(self, parent, displayname, cat, score, rate):
        tk.Frame.__init__(self, parent)
        # adds created instance to allskills list
        self.allskills.append(self)

        self.columnconfigure(0, weight = 3)
        self.columnconfigure(1, weight = 1)

        #global g.player
        self.rate = rate
        self.displayname = displayname
        self.ms = tk.IntVar()
        self.cat = cat
        self.score = score
        self.showscore = tk.IntVar()
        self.xpvar = self.score.replace("level", "xp")
        self.currentxp = 0
        self.nextlevel = 0

        self.showxp = tk.StringVar()
        self.showxp.set(str(self.currentxp) + " / " + str(self.nextlevel))


        # settings for skillBox frame
        self.configure(background='#888888')
            
        # widgets
        self.bar = ttk.Progressbar(self, length=400, maximum=self.rate, mode='determinate', variable=self.ms)
        self.scorelabel = ttk.Label(self, textvar=self.showscore) 
        self.button = ttk.Button(self)
        self.button.configure(text="Start/Stop", command = lambda : self.startstop(), width = 20)
        self.label =ttk.Label(self, text=displayname, width=15)
        self.xplabel = ttk.Label(self, textvar = self.showxp)
        # debug label for ms counter, uncomment below and in widget layout section
        #self.mslabel =ttk.Label(self, textvariable=self.ms)

        # widget layout in frame
        self.bar.grid(row = 0, column = 0, columnspan = 2, pady = 5, ipady=5)
        self.scorelabel.grid(row = 0, column = 2, sticky=W, padx=20)
        #self.mslabel.grid(row = 1, column = 3)
        self.xplabel.grid(row = 1, column = 1, pady = 5)
        self.button.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5, sticky=W)
        self.label.grid(row= 1, column = 2, pady = 5)

    def updatescore(self):
        self.showscore.set(g.player[self.cat][self.score])
        self.currentxp = g.player[self.cat][self.xpvar]
        self.nextlevel = g.xptable[g.player[self.cat][self.score]]
        if self.currentxp >= self.nextlevel:
            g.player[self.cat][self.score] = g.player[self.cat][self.score] +1
            self.nextlevel = g.xptable[g.player[self.cat][self.score]]
        self.showxp.set(str(self.currentxp) + " / " + str(self.nextlevel))

    def increment(self, cat, score):
        print(g.player[self.cat][self.score])
        xpvar = score.replace("level", "xp")
        g.player[cat][xpvar] = g.player[cat][xpvar] + 1
        self.updatescore()
        #self.showscore.set(player[self.cat][self.score] + 1)
        #player[cat][score] = self.showscore.get()

    def runbar(self, skill, start):
        #global g.activeskill
        self = skill

        while g.activeskill == self:
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
            except:
                pass
                exit()

            if now >= updatetime:
                # once timer completes, update skillscore for skillBox                       
                if mspassed >= self.rate:
                    self.increment(self.cat, self.score)
                start = datetime.now()

    def startstop(self):
        #global g.activeskill
        self.skillname = self.score
    
        if g.activeskill is None: # if nothing running, run selected skill
            g.activeskill = copy.copy(self)
            start = datetime.now()
            self.runbar(g.activeskill, start)

        elif g.activeskill.skillname != self.skillname: # check if something else is running
            g.activeskill.ms.set(0)
            g.activeskill = None
            g.activeskill = copy.copy(self)
            start = datetime.now()
            self.runbar(g.activeskill, start)

        elif g.activeskill.skillname == self.skillname:  # if skill already running, stop it
            self.ms.set(0)
            g.activeskill = None

g.app = mainWindow()

if g.lastsavefile != None and g.lastsavefile != "":
    loadchar(g.app, g.lastsavefile, True, True)

def closingtime():
    if g.player != None and g.player != g.chartemplate:
        print(g.activesavefile)
        
        # silently saves file on exit
        savechar(False)
        # saves prefs.cfg settings
        savepath = g.activesavefile
        winsizex = g.app.winfo_width()
        winsizey = g.app.winfo_height()
        winposx = g.app.winfo_x()
        winposy = g.app.winfo_y()
        createprefs(savepath, winposx, winposy, winsizex, winsizey)        
    g.app.destroy()

g.app.protocol("WM_DELETE_WINDOW", closingtime)
g.app.mainloop()
