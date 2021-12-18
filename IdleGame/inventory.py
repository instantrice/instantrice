import tkinter as tk
from tkinter import IntVar, ttk
from tkinter.constants import *
import globals as g
from PIL import ImageTk,Image

#g.items = {}

class item(dict):
    def __init__(self, idnum):
        self[idnum] = g.itemdb[idnum]

    def lazyinit(self):
        stripdict = {}
        for i in g.player['inventory']:
            mynewitem = item(i)
            mynewitem[i]['quantity'] = g.player['inventory'][i]
            stripdict[i] = mynewitem
        itemBox.playerinv = dict(element for value in stripdict.values() for element in value.items())

class itemBox(tk.Frame):
    playerinv = {}
    def __init__(self, parent, idnum):
        tk.Frame.__init__(self, parent)
        self.idnum = g.itemdb[idnum]
        self.playerinv = g.player['inventory']
        self.itemcount = IntVar()
        self.itemcount.set(g.player['inventory'][idnum])
        self.filename = itemBox.playerinv[idnum]['image']
        self.imgfile = Image.open(g.runningdir + '\\resources\\images\\' + self.filename).resize((96, 96))
        self.img = ImageTk.PhotoImage(self.imgfile)
        self.label = tk.Label(image = self.img, background = "red", relief = GROOVE, textvar = self.itemcount, compound = TOP, font=("DIN Alternate",14), justify='right')
        self.label.image = self.img
        print(self.label.image)
        print(self.itemcount.get())
        
        def selectitem(self):
            print('valid')
            self.label.configure(background="#CCCCCC", relief="sunken")
        self.label.bind('<Button-1>', selectitem)

    def lazyinit(self):
        stripdict = {}
        print(f"player inventory is {g.player['inventory']}")
        for i in g.player['inventory']:
            mynewitem = item(i)
            mynewitem[i]['quantity'] = g.player['inventory'][i]
            stripdict[i] = mynewitem
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
                #playerInv.items[idnum] = g.itemdb[idnum]
        self.lazyinit(self)
    
        
        
        

    