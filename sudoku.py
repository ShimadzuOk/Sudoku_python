from tkinter import *
from tkinter import messagebox
import requests,pathlib,time,json

template_dir = pathlib.Path(__file__).parent.joinpath("templates")
template_dir.mkdir(exist_ok=True,parents=True)
API_KEY = "YOUR API KEY GOES HERE"


class ControlFrame(Frame):
    def __init__(self, master):
        super().__init__(master = master,bd=1,relief=GROOVE)
        dificulties = ["easy","medium","hard"]

        self.master = master
        self.dif_var = StringVar(value="medium")
        self.width_var = IntVar(value=3)
        self.height_var = IntVar(value=3)

        self.get_btn = Button(self,text="Generate")
        self.dif_btns = [Radiobutton(
            self,
            text= dif,
            variable= self.dif_var,
            value= dif
        ) for dif in dificulties]
        w_lbl = Label(self,text="W:")
        h_lbl = Label(self,text="H:")
        self.w_entry = Spinbox(self,values=[i for i in range(2,5)],textvariable= self.width_var)
        self.h_entry = Spinbox(self,values=[i for i in range(2,5)],textvariable= self.height_var)
        self.list_b = Listbox(self,width=30,height=3)
        v_scroll = Scrollbar(self, orient=VERTICAL)
        self.load_btn = Button(self,text="Load")
        self.save_btn = Button(self,text="Save")
        self.del_btn = Button(self,text="Delete")

        [btn.grid(row=n,column=0,sticky=EW) for n,btn in enumerate(self.dif_btns)]
        w_lbl.grid(row=0,column=1,sticky=EW)
        h_lbl.grid(row=1,column=1,sticky=EW)
        self.w_entry.grid(row=0,column=2,sticky=EW)
        self.h_entry.grid(row=1,column=2,sticky=EW)
        self.get_btn.grid(row=2,column=1,columnspan=2,sticky=EW)
        self.list_b.grid(row=0,rowspan=2,column=3,columnspan=3,sticky=EW)
        [self.list_b.insert(END,i.name.strip(".json")) for i in template_dir.iterdir()]
        v_scroll.grid(row=0,rowspan=2,column=6)
        v_scroll.config(command=self.list_b.yview) 
        self.list_b.config(yscrollcommand=v_scroll.set)
        self.load_btn.grid(row=2,column=3,sticky=EW)
        self.save_btn.grid(row=2,column=4,sticky=EW)
        self.del_btn.grid(row=2,column=5,sticky=EW)

class SudokuFrame(Frame):
    def __init__(self, master,val):
        super().__init__(master = master)
        self.field_var = val
        self.lbl = Label(self,text=self.field_var,bg="lightgray",width=3,bd=1,relief=GROOVE)
        self.ent = Entry(self,justify=CENTER,width=3)
        # self.row = []
        # self.column = []
        # self.area = []

class Game(Tk):
    def __init__(self):
        super().__init__()
        self.ctrl_fr = ControlFrame(self)
        self.sudoku = Frame(self,bg="lightgray")
        self.loaded = None
        self.solution = []
        self.cells = []

        self.ctrl_fr.pack()
        self.sudoku.pack(expand=True,fill=BOTH)
        self.ctrl_fr.get_btn.configure(command=self.get_sudoku)
        self.ctrl_fr.load_btn.configure(command=lambda:self.construct(self.ctrl_fr.list_b.selection_get()))
        self.ctrl_fr.save_btn.configure(command=self.save)
        self.ctrl_fr.del_btn.configure(command=self.delete)
        self.val_btn = Button(self,text="Check",command=self.validate)
        self.val_btn.pack(fill=X)

    def get_sudoku(self):
        time_now = f"{time.localtime()[1]}.{time.localtime()[2]} {time.localtime()[3]}h{time.localtime()[4]}m{time.localtime()[5]}sec"
        dif = self.ctrl_fr.dif_var.get()
        width = self.ctrl_fr.width_var.get()
        height = self.ctrl_fr.height_var.get()
        URL = f"https://api.api-ninjas.com/v1/sudokugenerate?difficulty={dif}&width={width}&height={height}"
        with open(template_dir.joinpath(f"{dif}, {width}x{height}({time_now}).json"),"w") as f:
            game_data = dict(requests.get(URL,headers={"X-Api-Key": API_KEY}).json())
            game_data["difficulty"] = dif
            game_data["width"] = width
            game_data["height"] = height
            json.dump(game_data,f,indent=4)
            self.ctrl_fr.list_b.insert(END,f"{dif}, {width}x{height}({time_now})")

    def yellow(self,event):
        if event.widget.cget("bg") != "yellow" : event.widget.configure(bg = "yellow",state = "readonly")
        else: event.widget.configure(bg = "white",state = "normal")

    def construct(self,name):
        self.solution = []
        self.loaded = name
        [i.grid_forget() for i in self.sudoku.grid_slaves()]
        if self.cells:
            [self.sudoku.rowconfigure(i,weight=0) for i in range(len(self.cells))]
            [self.sudoku.columnconfigure(i,weight=0) for i in range(len(self.cells[0]))]
            self.cells = []
        with open(template_dir.joinpath(f"{self.loaded}.json")) as f:
            game_field = json.load(f)
            self.solution = game_field["solution"]
            game_grid = game_field["puzzle"]
            width = game_field ["width"]
            height = game_field ["height"]


        for r, row in enumerate(game_grid):
            widget_row = []
            self.rowconfigure(r,weight=1)

            for c, value in enumerate(row):
                if r == 0: self.columnconfigure(c,weight=1)

                padx = (10 if c % width == 0 else 1, 1)
                pady = (10 if r % height == 0 else 1, 1)

                cell = SudokuFrame(self.sudoku,value)

                if value is not None and isinstance(value,int):
                    cell.lbl.configure(text=value)
                    cell.lbl.pack(expand = True,fill = BOTH)
                elif isinstance(value,str):
                    cell.ent.insert(0,value)
                    cell.ent.pack(expand = True,fill = BOTH)
                    cell.ent.bind("<Button-3>",func= self.yellow)
                else:
                    cell.ent.pack(expand = True,fill = BOTH)
                    cell.ent.bind("<Button-3>",func= self.yellow)
                    
                cell.grid(row=r, column=c, padx=padx, pady=pady,sticky=NSEW)
                widget_row.append(cell)

            self.cells.append(widget_row)
        
        # #cell row and column
        # for r in self.cells:
        #     for n,cell in enumerate(r):
        #         cell.row = [r]
        #         for row in self.cells:
        #             cell.column.append(row[n])

    def save(self):
        with open(template_dir.joinpath(f"{self.loaded}.json")) as f: file_data = json.load(f)
        solution = file_data["solution"]
        dif = file_data["difficulty"]
        w = file_data["width"]
        h = file_data["height"]

        puzzle = [[cell.field_var if cell.field_var != None else cell.ent.get() for cell in row] for row in self.cells]
        time_now = f"{time.localtime()[1]}.{time.localtime()[2]} {time.localtime()[3]}h{time.localtime()[4]}m{time.localtime()[5]}sec"

        with open(template_dir.joinpath(f"{dif}, {w}x{h}({time_now}).json"),W) as f: 
            save_data = {
                "puzzle": puzzle,
                "solution" : solution,
                "difficulty" : dif,
                "width" : w,
                "height" : h
            }
            json.dump(save_data,f,indent=4)

        self.ctrl_fr.list_b.insert(END,f"{dif}, {w}x{h}({time_now})")

    def delete(self):
        selected = self.ctrl_fr.list_b.selection_get()
        selected_ind = self.ctrl_fr.list_b.curselection()
        if messagebox.askyesno(title="Delete",message=f"Delete file {selected}.json? Action might be irreversibale."):
            template_dir.joinpath(f"{selected}.json").unlink()
            self.ctrl_fr.list_b.delete(selected_ind)
        else: pass

    def validate(self):
        field = [[cell.ent.get() if cell.ent.get() != '' else cell.field_var if cell.field_var != None else "" for cell in row] for row in self.cells]
        
        for r,row in enumerate(self.cells):
            for c,cell in enumerate(row):
                if cell.ent.get() == "": continue
                if cell.ent.get() == str(self.solution[r][c]):
                    cell.ent.config(bg = "green")
                else:
                    cell.ent.config(bg = "red")
                    
        if [[str(cell) for cell in row] for row in self.solution]  == [[str(cell) for cell in row] for row in field]: 
            self.val_btn.configure(bg="#7aec4e",text="WIN!Load another game.")

root = Game()

root.mainloop()
time.localtime()