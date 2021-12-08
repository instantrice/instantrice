import copy
import datetime
import json
import sys
import tkinter as tk

from datetime import datetime, timedelta, timezone
from os import path
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk

import ntplib
import pandas

# global vars
global player
global activeskill
global chartemplate
global savefile
global seed

runningdir = (path.dirname(path.abspath(sys.argv[0])))
with open(runningdir + "\charschema.json") as template_file:
    chartemplate = json.loads(template_file.read())

lastchar = "Davenport"
activeskill = None

# global functions
def checktime():
    global seed
    c = ntplib.NTPClient()
    response = c.request("us.pool.ntp.org", version=3)
    response.offset
    seed = datetime.fromtimestamp(response.tx_time, timezone.utc)

#validate schema
def validate(playersave):
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
    keyscrape(playersave, playerschema)

    # check if save is valid
    if(tmplschema == playerschema):
        print("it's a match!")
    else:
        print("file did not pass save file validation")

def loadchar():
    #load save file
    global savefile
    global player

    homedir = (path.expanduser( '~' ))
    savedir = (path.join( homedir, 'Documents\Saves'))
    savefile = fd.askopenfilename(title="Load your Character", initialdir=savedir, filetypes=[("Steve's Wicked Idle Game Hero", "*.hero")])
       
    with open(savefile) as save_file:
        player = json.loads(save_file.read())

    validate(player)

#def playchar(player):
    #logic to build the active character here

class Player(json.JSONDecoder):
    def __init__(self):
        global savefile
        global player
        



class mainWindow(tk.Tk):
    
    # init for mainWindow class
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # set Title, define style defaults
        self.winfo_toplevel().title("Steve's Wicked Idle Game")

        s = ttk.Style()
        s.theme_use('alt')
        s.configure('.', background='#888888')
        s.configure('TButton', width=50)
        s.configure("Horizontal.TProgressbar", background = "red", lightcolor="white", darkcolor="black")

        # creating a "container" for the frames
        container = tk.Frame(self) 
        container.configure(width=1280, height=720)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        container.grid_propagate(0)
        
        container.grid(sticky=NSEW)
        
        # initializing frames to an empty array
        self.frames = {} 
        
        # iterating through a tuple of pages
        for F in (StartPage, NewChar, LoadChar, MainGame):
            frame = F(container, self)
  
            # initializing frame of that object from
            # startpage, NewChar, page2 respectively with
            # for loop
            self.frames[F] = frame
            frame.configure(background="#888888")
            frame.grid(row = 0, column = 0, sticky ="nsew")            
            
        self.show_frame(StartPage)
  
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # main label on start page
        label = ttk.Label(self, text ="Welcome to Steve's Idle Game!", font=25)
        label.grid(row = 0, column = 0, padx = 5, pady = 5, ipady=5)

        # continue button  
        button1 = ttk.Button(self, text='Continue with ' + lastchar,
        command = lambda : controller.show_frame(MainGame))
        button1.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5)
        
        # new game button
        button2 = ttk.Button(self, text ="New Character",
            command = lambda : controller.show_frame(NewChar))
        button2.grid(row = 2, column = 0, padx = 5, pady = 5, ipady=5)

        # load game button
        button2 = ttk.Button(self, text ="Load Character",
            command = lambda : controller.show_frame(LoadChar))
        button2.grid(row = 3, column = 0, padx = 5, pady = 5, ipady=5)
       
  
# second window frame NewChar
class NewChar(tk.Frame):
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        label = ttk.Label(self, text ="Character Creation", background="#888888")
        label.grid(row = 0, column = 0, padx = 5, pady = 5, ipady=5)
  
        # button to show frame 1 with text
        button1 = ttk.Button(self, text ="Let's go!",
            command = lambda : controller.show_frame(MainGame))
        button1.grid(row = 1, column = 0, padx = 5, pady = 5, ipady=5)        
  
        # button to show frame 2 with text
        button2 = ttk.Button(self, text ="Back", 
            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 2, column = 0, padx = 5, pady = 5, ipady=5)

class LoadChar(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        label = ttk.Label(self, text ="Load your Character", background="#888888")
        label.grid(row = 0, column = 0, padx = 5, pady = 5, ipady=5)

        # button to load and play
        button1 = ttk.Button(self, text = "Load Character",
            command = lambda : loadchar())
        button1.grid(row = 1, column = 0, padx = 5, pady = 5, ipady = 5)

        # button to go back
        button2 = ttk.Button(self, text ="Back",
            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 2, column = 0, padx = 5, pady = 5, ipady=5)

class MainGame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #self.grid_propagate(0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, pad=5)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        swordscore = 0
        swordrate = 3000
        sword = Skillbox(self, "Swords!", swordscore, swordrate)
        sword.grid (row = 1, column = 1, sticky=W)

        bowscore = 0
        bowrate = 3000
        bow = Skillbox(self, "Bows!", bowscore, bowrate)
        bow.grid (row = 2, column = 1, sticky=W)
        
        conjurationscore = 0
        conjurationrate = 3000
        conjuration = Skillbox(self, "Conjuration!", conjurationscore, conjurationrate)
        conjuration.grid (row = 3, column = 1, sticky=W)

        # button to go back to start page
        button2 = ttk.Button(self, text ="Go Back",
            command = lambda : controller.show_frame(StartPage))
        button2.grid(row = 4, column = 0, padx = 5, pady = 5, ipady=5, sticky=S)

class Skillbox(tk.Frame):
    def __init__(self, parent, skillname, score, rate):
        tk.Frame.__init__(self, parent)
        self.skillname = skillname
        self.ms = tk.IntVar()

        # functions
        def increment():
            showscore.set(showscore.get() + 1)

        def runbar(skill, start):
            global activeskill
            self = skill

            while activeskill == self:
                r = timedelta(milliseconds=rate)
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
                    self.bar.update_idletasks()
                    mainWindow.update(self)
                # ignore TclError that happens when exiting because tkinter fuckery
                except(TclError):
                    pass
                    exit()

                if now >= updatetime:
                    # once timer completes, update skillscore for skillbox                       
                    if mspassed >= rate:
                        increment()
                    start = datetime.now()

        def startstop(skill):
            global activeskill
            self.skillname = skill.skillname
        
            if activeskill is None: # if nothing running, run selected skill
                activeskill = copy.copy(self)
                start = datetime.now()
                runbar(activeskill, start)

            elif activeskill.skillname != self.skillname: # check if something else is running
                activeskill.ms.set(0)
                activeskill = None
                activeskill = copy.copy(self)
                start = datetime.now()
                runbar(activeskill, start)

            elif activeskill.skillname == self.skillname:  # if skill already running, stop it
                self.ms.set(0)
                activeskill = None

        # vars
        self.skillname = skillname
        self.score = score
        showscore = tk.IntVar()
        showscore.set(self.score)
        self.rate = rate
        
        # settings for skillbox frame
        self.configure(background='#888888')

        # widgets
        self.bar = ttk.Progressbar(self, length=300, maximum=self.rate, mode='determinate', variable=self.ms)
        self.scorelabel = tk.Label(self, textvariable=showscore, background="#888888") 
        self.button = ttk.Button(self)
        self.button.configure(text="Start/Stop", command = lambda : startstop(self))
        self.label = tk.Label(self, text=skillname, background="#888888")
        #self.mslabel = tk.Label(self, textvariable=self.ms, background="#888888")

        # widget layout in frame
        self.bar.grid(row = 1, column = 1)
        self.scorelabel.grid(row = 1, column = 2)
        #self.mslabel.grid(row = 1, column = 3)
        self.button.grid(row = 2, column = 1, padx = 5, pady = 5, ipady=5)
        self.label.grid(row= 2, column = 2)

loadchar

app = mainWindow()
app.mainloop()
