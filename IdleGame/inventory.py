import tkinter as tk
from tkinter import Event, IntVar, ttk
from tkinter.constants import *
import globals as g
from PIL import ImageTk,Image

groupselect = 0

class item(dict):
    def __init__(self, idnum):
        self[idnum] = g.itemdb[idnum]

class itemBox(tk.Label):
    playerinv = {}
    allboxes = []
    def __init__(self, parent, idnum):
        tk.Label.__init__(self, parent)
        self.idnum = g.itemdb[idnum]
        self.itemcount = IntVar()
        self.itemcount.set(g.player['inventory'][idnum])
        self.filename = itemBox.playerinv[idnum]['image']
        self.imgfile = Image.open(g.runningdir + '\\resources\\images\\' + self.filename).resize((96, 96))
        self.img = ImageTk.PhotoImage(self.imgfile)
        self.image = self.img
        self.configure(image = self.img, background = "#888888", relief = GROOVE, textvar = self.itemcount, compound = TOP, font=("DIN Alternate",14), justify='right')
        
        self.selected = 0
        itemBox.allboxes.append(self)

        def multiselect(Event):
            if self.selected == 0:
                Event.widget.configure(background="#CCCCCC", relief="sunken")
                self.selected = 1
            else:
                Event.widget.configure(background="#888888", relief="groove")
                self.selected = 0

        def singleselect(Event):
            if self.selected == 0:
                for i in itemBox.allboxes:
                    i.selected = 0
                    i.configure(background="#888888", relief="groove")
                Event.widget.configure(background="#CCCCCC", relief="sunken")
                self.selected = 1
            else:
                Event.widget.configure(background="#888888", relief="groove")
                self.selected = 0
        
        def selector(Event):
            if groupselect == 0:
                singleselect(Event)
            else:
                multiselect(Event)

        self.bind('<Button-1>', selector)

    def lazyinit(self):
        stripdict = {}
        print(f"player inventory is {g.player['inventory']}")
        for k in g.player['inventory']:
            mynewitem = item(k)
            mynewitem[k]['quantity'] = g.player['inventory'][k]
            stripdict[k] = mynewitem
        itemBox.playerinv = dict(element for value in stripdict.values() for element in value.items())
        print(f"playerinv is {itemBox.playerinv}")
        
def additem(self, idnum, amount, add):
        print(item.items)
        if idnum in g.player['inventory'].items:
            if add == True:
                g.player['inventory'][idnum] += amount
            elif g.player['inventory'][idnum] - amount < 0:
                print("not enough items in inventory")
            else:    
                g.player['inventory'][idnum] -= amount
                g.player['inventory'].pop(idnum)
        else:
            if add == True:
                g.player['inventory'][idnum] = amount
        self.lazyinit(self)
    
class Equipment(tk.Label):
    def __init__(self, parent, idnum):
        tk.Label.__init__(self, parent)
        if idnum == 0:
            idnum = "0"
        self.idnum = g.itemdb[idnum]
        

    

class EquipmentFrame(tk.Frame):
    equipped = {}
    head = tk.Label(background="red", height = 64, width= 64)
    neck = tk.Label(background="red", height = 32, width= 32)
    mh = tk.Label(background="red", height = 64, width= 64)
    torso = tk.Label(background="red", height = 64, width= 64)
    oh = tk.Label(background="red", height = 64, width= 64)
    hands = tk.Label(background="red", height = 64, width= 64)
    legs = tk.Label(background="red", height = 64, width= 64)
    ring1 = tk.Label(background="red", height = 32, width= 32)
    ring2 = tk.Label(background="red", height = 32, width= 32)
    feet = tk.Label(background="red", height = 64, width= 64)

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.rowconfigure(0, weight = 2)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 2)
        self.rowconfigure(3, weight = 2)
        self.rowconfigure(4, weight = 2)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        
        

    def lazyinit(self):
        equipdict = {}
        for k in g.player['equipment'].values():
            if isinstance(k, int):
                print("found an int")
                k = str(k)
            mynewitem = item(k)
            #mynewitem[k]['quantity'] = g.player['inventory'][k]
            equipdict[k] = mynewitem
        EquipmentFrame.equipped = dict(element for value in equipdict.values() for element in value.items())

        

        self.head.grid(row = 0, column = 1)
        self.neck.grid(row = 1, column = 1)
        self.mh.grid(row = 2, column = 0)
        self.torso.grid(row = 2, column = 1)
        self.oh.grid(row = 2, column = 2)
        self.hands.grid(row = 3, column = 0)
        self.legs.grid(row = 3, column = 1)
        self.ring1.grid(row = 3, column = 2)
        self.ring2.grid(row = 3, column = 2)
        self.feet.grid(row = 4, column = 1)
        