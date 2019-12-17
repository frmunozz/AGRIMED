import tkinter as tk
import tkinter.ttk as ttk
import re
import logging
import datetime


class Model:
    def __init__(self, **kwargs):
        pass

    # all model actions goes here


def donothing():
    filewin = tk.Toplevel(root)
    button = tk.Button(filewin, text="Do nothing button")
    button.pack()


class MenuBar(tk.Menu):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.add_help(**kw)

    def do_nothing(self):
        filewin = tk.Toplevel(self.master)
        button = tk.Button(filewin, text="Do nothing")
        button.pack()

    def add_help(self, **kwargs):
        helpmenu = tk.Menu(self, tearoff=0)
        helpmenu.add_command(label="datos necesarios", command=kwargs.get("data_instructions", self.do_nothing))
        helpmenu.add_command(label="modelos utilizados", command=kwargs.get("model_instructions", self.do_nothing))
        helpmenu.add_command(label="Información", command=kwargs.get("about", self.do_nothing))
        self.add_cascade(label="Ayuda", menu=helpmenu)


class View(tk.Toplevel):
    def __init__(self, master, **kwargs):
        tk.Toplevel.__init__(self, master, **kwargs)
        self.chk = None
        self.chk_state = None
        self.prob_entry = None
        self.date_entry = None
        self.search_btn = None
        self.file_entry = None
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)
        self.set_window_size(**kwargs)
        self.main_title = self.set_title(**kwargs)
        self.file_block_title = self.file_block(**kwargs)
        self.configure_block_title = self.configure_block()
        self.start_button(**kwargs)

    # all visual goes here

    def file_block(self, **kwargs):
        # title
        lbl = tk.Label(self, text="Archivo de Datos", font=("Arial", 15))
        # lbl.place(relx=0.03, rely=0.15, anchor="w")
        lbl.pack(after=self.main_title, anchor="w", padx=5, pady=20)

        # title horizontal line
        sepp = ttk.Separator(self, orient=tk.HORIZONTAL)
        sepp.place(in_=lbl, relx=1, rely=0.5, width=230, anchor="nw")
        # sepp.pack(after=lbl, side="right", expand=True, fill="both")

        # entry text disabled
        self.file_entry = tk.Entry(self)
        self.file_entry.insert(0, "seleccione archivo de datos")
        self.file_entry.configure(state="disabled")
        self.file_entry.place(in_=lbl, x=5, y=70, width=270, height=24, anchor="w")

        # button for search file
        self.search_btn = tk.Button(self, text="Buscar", font=(14),
                                    command=kwargs.get("search_btn_command", donothing))
        self.search_btn.place(in_=self.file_entry, x=270, rely=0.5, width=100, height=24, anchor="w")

        return lbl

    def configure_block(self):

        # title
        lbl = tk.Label(self, text="Configuración", font=("Arial", 15))
        lbl.pack(after=self.file_block_title, anchor="w", padx=5, pady=80)

        # title horizontal line
        sepp = ttk.Separator(self, orient=tk.HORIZONTAL)
        sepp.place(in_=lbl, relx=1, rely=0.5, width=260, anchor="nw")

        # day of data
        lbl2 = tk.Label(self, text="Fecha de datos a usar:", font=(15))
        lbl2.place(in_=lbl, x=5, y=50, anchor="w")
        self.date_entry = tk.Entry(self)
        self.date_entry.place(in_=lbl2, relx=1, rely=0.5, anchor="w", width=100)
        lbl22 = tk.Label(self, text="(dd/mm/yyyy)", font=(15))
        lbl22.place(in_=self.date_entry, relx=1, rely=0.5, anchor="w")

        # hierarchical model option
        s = ttk.Style()
        s.configure('TCheckbutton', font=('Arial', '12'))
        self.chk_state = tk.BooleanVar()
        self.chk_state.set(True)
        self.chk = ttk.Checkbutton(self, text="Usar Clasificador binario como primer filtro",
                             var=self.chk_state, style="TCheckbutton")
        # print(type(chk.invoke()))
        self.chk.place(in_=lbl, x=5, y=90, anchor="w")

        # probability threshold
        lbl3 = tk.Label(self, text="Probabilidad aceptable:", font=('Arial', '11'))
        lbl3.place(in_=self.chk, x=10, rely=1)
        self.prob_entry = tk.Entry(self)
        self.prob_entry.place(in_=lbl3, relx=1, rely=0.5, anchor="w", width=100)
        self.prob_entry.insert(0, "0.5")
        lbl33 = tk.Label(self, text="(0.0 - 1.0)", font=("Arial", "11"))
        lbl33.place(in_=self.prob_entry, relx=1, rely=0.5, anchor="w")

        return lbl

    def start_button(self, **kwargs):
        # button
        btn = tk.Button(self, text="Iniciar", width=15, font=("Arial", "11"),
                        command=kwargs.get("start_button_command", donothing))
        btn.place(in_=self.configure_block_title, y=185, x=190, anchor="center")
        sepp1 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sepp1.place(in_=btn, x=-7, rely=0.5, width=115, anchor="e")
        sepp2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sepp2.place(in_=btn, x=260, rely=0.5, width=115, anchor="e")

    def set_title(self, **kwargs):
        lbl = tk.Label(self, text=kwargs.get("title_text", "Predictor de Heladas"),
                       font=("Arial Bold", 20))
        # lbl.place(relx=0.5, rely=0.05, anchor=kwargs.get("anchor", "center"))
        lbl.pack(anchor="center", ipady=20)
        return lbl

    def set_window_size(self, **kwargs):
        width = kwargs.get("width", 400)
        height = kwargs.get("height", 450)
        self.geometry("%sx%s" % (str(width), str(height)))
        self.resizable(0, 0)


class Controller:
    def __init__(self, root, **kwargs):
        self.model = Model(**kwargs)  # aqui va el modelo predictor
        self.view = View(root,
                         search_btn_command=self.set_file,
                         start_button_command=self.start_prediction)
        self.menubar = MenuBar(root)
        self.view.config(menu=self.menubar)

    # all actions goes here

    def do_nothing(self):
        filewin = tk.Toplevel(self.view.master)
        button = tk.Button(filewin, text="Do nothing")
        button.pack()

    def set_file(self):
        """ when a data file is added """
        pass

    def check_hierarchical_model(self):
        """ choose if we use a binary classifier first in a hierarchical way"""
        return self.view.chk_state.get()

    def check_prob_threshold(self):
        prob = self.view.prob_entry.get()
        try:
            prob = float(prob)
            if not 0.0 < prob < 1.0:
                logging.error("La probabilidad ingresada '%s' esta fuera del rango [0,1]" % str(prob))
        except ValueError:
            logging.error("La probabilidad ingresada '%s' no es un valor valido" % str(prob))
        finally:
            return prob

    def check_date(self):
        date = self.view.date_entry.get()
        ddtt = None
        try:
            ddtt = datetime.datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            logging.error("La fecha '%s' no cumple el formato" % date)
        finally:
            return ddtt

    def start_prediction(self):
        """ when the button for start prediction is pressed """
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Predictor Beta v1")
    root.withdraw()
    app = Controller(root)
    root.mainloop()