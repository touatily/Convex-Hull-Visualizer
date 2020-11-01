import tkinter as tk
from tkinter import ttk
import convexHull as ch
import math
import json
from tkinter import filedialog
from tkinter import messagebox as mb
import csv


class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        try:
            self.wm_state("zoomed")
        except:
            pad=3
            self.geometry("{0}x{1}+0+0".format( self.winfo_screenwidth()-pad,
                                                self.winfo_screenheight()-pad))
        self.title("Convex Hull problem visualizer")
        
        self.algos_details = json.load(open("doc.json", "r"))

        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w, h))
        self.resizable(False, False)

        self.plan = tk.Frame(self, bg="grey")
        self.plan.pack(fill="both", padx=20, pady=20, expand=True)

        self.plan.grid_columnconfigure(0, weight=1)
        
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.load, accelerator="Ctrl+O")
        filemenu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=filemenu)
        
        self.config(menu=menubar)
        
        
        # canvas configuration
        self.canvas = tk.Canvas(self.plan, bg = "white",
                                height=h-90, bd=2, highlightbackground="black")
        
        self.canvas.grid(row = 0, column = 0, sticky="NEWS", ipadx=0, ipady=0)
        
        self.canvas.bind("<Button-1>", self.addPoint)
        self.canvas.bind("<Control-1>", self.deletePoint)
        self.canvas.bind("<Control-B1-Motion>", self.deletePoint)
        self.canvas.bind("<Shift-1>", self.pickPoint)
        self.canvas.bind("<Shift-B1-Motion>", self.movePoint)
        self.canvas.bind("<ButtonRelease-1>", self.unpickPoint)
        
        self.bind_all("<Control-x>", self.deleteAll)
        self.bind_all("<Control-s>", self.save)
        self.bind_all("<Control-o>", self.load)
        self.bind_all("<Control-x>", self.exit)
        
        # control buttons
        
        self.plan2 = tk.Frame(self.plan)
        self.plan2.grid(row=0, column=1, sticky="SN")
        
        list_algos = ["Gift wrapping", "Graham scan", "Quickhull", "Monotone chain"]
        self.list_algos = ttk.Combobox(self.plan2, values=list_algos, state="readonly")
        self.list_algos.pack(ipadx=15, padx=10, ipady=5, pady=5)
        
        self.list_algos.bind("<<ComboboxSelected>>", self.selectAlgo)
        
        
        self.speed = tk.Scale(self.plan2, from_=1, to=100, orient=tk.HORIZONTAL,
                width=10, label="Speed", length=100)
        self.speed.pack(ipadx=15, padx=10)
        
        self.simulateBtn = tk.Button(self.plan2, text="Simulate", command=self.simulate)
        self.simulateBtn.pack(ipadx=15, padx=10, ipady=5, pady=5)
        
        self.complexity_lbl = tk.Label(self.plan2, text="Complexité")
        self.complexity_lbl.pack(ipadx=15, padx=10)
        
        self.complexity = tk.StringVar()
        self.complexity.set("-")
        self.complexity_val = tk.Label(self.plan2, textvariable=self.complexity,
                    anchor="w", justify="left", wraplength=130)
        self.complexity_val.pack(ipadx=15, padx=10)  
        
        self.description_lbl = tk.Label(self.plan2, text="Description")
        self.description_lbl.pack(ipadx=15, padx=10) 
          
        self.description = tk.StringVar()
        self.description.set("-")  
        self.description_val = tk.Label(self.plan2, textvariable=self.description, 
                    anchor="w", justify="left", wraplength=130)
        self.description_val.pack(ipadx=15, padx=10)  
        
    
    def save(self, event=None):
        S = [(int(self.canvas.coords(e)[0]+3), int(self.canvas.coords(e)[1]+3))
                for e in self.canvas.find_withtag("point")]
        
        ftypes = [('CSV files', '.csv')]
        fname = filedialog.asksaveasfilename(filetypes=ftypes, defaultextension=".csv",
                                             title="Save as CSV file", initialdir = "./saves/")

        if not fname:
            return
        with open(fname, "w", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerows(S)
        mb.showinfo('Action completed', 'The configuration has been successfully saved!')
        
    def load(self, event=None):
        fname = filedialog.askopenfilename(filetypes=[('CSV files', '.csv')], defaultextension=".csv",
            title="Save configuration as CSV file", initialdir = "./saves/")
        if not fname:
            return
        self.canvas.delete("all")
        with open(fname, "r") as f:
            reader = csv.reader(f, delimiter=",")
            l = list(reader)
            fileContent = [[int(ee) for ee in e] for e in l]
        
        for e in l:
            x = int(e[0])
            y = int(e[1])
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue", tag=f"point {str(x)}_{str(y)}")
        
        
    def addPoint(self, event=None):
        x = event.x
        y = event.y
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue", tag=f"point {str(x)}_{str(y)}")
        
    def deletePoint(self, event=None):
        x = event.x
        y = event.y
        for i in range(x-5, x+6):
            for j in range(y-5, y+6):
                self.canvas.delete(f"{str(i)}_{str(j)}")
                
    def movePoint(self, event=None):
        if self.pickedPoint:
            x0, y0, x1, y1 = self.canvas.coords(self.pickedPoint)
            self.canvas.move(self.pickedPoint, event.x-x0-3, event.y-y0-3)
            self.canvas.itemconfig(self.pickedPoint, tag=f"point {event.x}_{event.y}")
        
    def pickPoint(self, event=None):
        x, y = event.x, event.y
        l = [(self.canvas.coords(i),i) for i in self.canvas.find_withtag("point")]
        if l:
            ll = [(math.sqrt((e[0][0]+3-x)**2 + (e[0][1]+3-y)**2), e[1]) for e in l]
            p = min(ll, key=lambda x: x[0])
            if p[0] < 5:
                self.pickedPoint = p[1]
                
    def unpickPoint(self, event=None):
        self.pickedPoint = None

    def deleteAll(self, event=None):
        self.canvas.delete("point")
        
    def selectAlgo(self, event=None):
        if self.list_algos.current() == -1:
            self.complexity.set("-")
            self.description.set("-")
        elif self.list_algos.current() > 7: return
        else:
            self.complexity.set(self.algos_details[self.list_algos.current()]["complexity"])
            self.description.set(self.algos_details[self.list_algos.current()]["description"])
        
    def simulate(self, event=None):
        if self.list_algos.current() == 0:
            ch.ConvexHullSolver.algoGiftwrapping(self.canvas, self.speed)
        elif self.list_algos.current() == 1:
            ch.ConvexHullSolver.algoGrahamScan(self.canvas, self.speed)
        elif self.list_algos.current() == 2:
            ch.ConvexHullSolver.algoQuickhull(self.canvas, self.speed)
        elif self.list_algos.current() == 3:
            ch.ConvexHullSolver.algoMonotoneChain(self.canvas, self.speed)
        else:
            pass



    def exit(self, e=None):
        self.destroy()
