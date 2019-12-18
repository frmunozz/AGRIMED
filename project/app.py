import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import scrolledtext
import logging
import datetime
import pandas as pd
from project.model import Predictor, DataHandler


class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, "> " + msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


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
        tk.Toplevel.__init__(self, master)
        self.chk = None
        self.chk_state = None
        self.prob_entry = None
        self.date_entry = None
        self.asnm_entry = None
        self.lat_entry = None
        self.search_btn = None
        self.file_entry = None
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)
        self.set_window_size(**kwargs)
        self.main_title = self.set_title(**kwargs)
        self.file_block_title = self.file_block(**kwargs)
        self.configure_block_title = self.configure_block()
        self.start_btn = self.start_button(**kwargs)
        self.st = self.scrolled_text()

    # all visual goes here

    def scrolled_text(self):
        st = scrolledtext.ScrolledText(self, state='disabled')
        st.configure(font="TkFixedFont")
        st.place(in_=self.start_btn, anchor="n", x=75, y=50, width=365, height=100)

        text_handler = TextHandler(st)

        logging.basicConfig(filename="predictor.log",
                            level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
        self.logger.addHandler(text_handler)
        self.logger.info(":>>>>>> Inicie el programa <<<<<<<<: <")

        return st

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
                                    command=kwargs.get("search_btn_command", None))
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

        # ASNM and latitude input
        lbl4 = tk.Label(self, text="Altura sobre el nivel del mar (metros):",  font=('Arial', '11'))
        lbl4.place(in_=self.chk, x=10, rely=2)
        self.asnm_entry = tk.Entry(self)
        self.asnm_entry.place(in_=lbl4, relx=1, rely=0.5, anchor="w", width=100)

        # latitude input
        lbl5 = tk.Label(self, text="Latitud de la estación (decimal):",  font=('Arial', '11'))
        lbl5.place(in_=self.chk, x=10, rely=3)
        self.lat_entry = tk.Entry(self)
        self.lat_entry.place(in_=lbl5, relx=1, rely=0.5, anchor="w", width=100)
        return lbl

    def start_button(self, **kwargs):
        # button
        btn = tk.Button(self, text="Iniciar", width=15, font=("Arial", "11"),
                        command=kwargs.get("start_button_command", None))
        btn.place(in_=self.configure_block_title, y=205, x=190, anchor="center")
        sepp1 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sepp1.place(in_=btn, x=-7, rely=0.5, width=115, anchor="e")
        sepp2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sepp2.place(in_=btn, x=260, rely=0.5, width=115, anchor="e")

        return btn

    def set_title(self, **kwargs):
        lbl = tk.Label(self, text=kwargs.get("title_text", "Predictor de Heladas"),
                       font=("Arial Bold", 20))
        # lbl.place(relx=0.5, rely=0.05, anchor=kwargs.get("anchor", "center"))
        lbl.pack(anchor="center", ipady=20)
        return lbl

    def set_window_size(self, **kwargs):
        width = kwargs.get("width", 400)
        height = kwargs.get("height", 580)
        self.geometry("%sx%s" % (str(width), str(height)))
        self.resizable(0, 0)


class Controller:
    def __init__(self, root, **kwargs):
        dirpath = os.path.dirname(os.path.abspath(__file__))
        dirpath = dirpath.replace("\\", "/")
        self.model = Predictor(bc_model_path=dirpath + "/classifier/model/",
                               lstm_model_path=dirpath + "/lstm/modelo/")
        self.view = View(root,
                         search_btn_command=self.set_file,
                         start_button_command=self.start_prediction)
        self.menubar = MenuBar(root)
        self.view.config(menu=self.menubar)
        self.file = ""

    # all actions goes here

    def do_nothing(self):
        filewin = tk.Toplevel(self.view.master)
        button = tk.Button(filewin, text="Do nothing")
        button.pack()

    def set_file(self):
        """ when a data file is added """
        self.file = filedialog.askopenfilename()
        self.view.file_entry.configure(state="normal")
        self.view.file_entry.delete(0, 'end')
        self.view.file_entry.insert(0, self.file)
        self.view.file_entry.configure(state="readonly")

    def check_hierarchical_model(self):
        """ choose if we use a binary classifier first in a hierarchical way"""
        hier = self.view.chk_state.get()
        state = "ON" if hier else "OFF"
        self.view.logger.info("> Clasificador binario: %s" % state)
        return hier

    def check_prob_threshold(self):
        prob = self.view.prob_entry.get()
        try:
            prob = float(prob)
            if not 0.0 < prob < 1.0:
                logging.error(">> La probabilidad ingresada '%s' esta fuera del rango [0,1]" % str(prob))
            else:
                logging.info("> probabilidad de helada aceptable: %s" % str(prob))
        except ValueError:
            logging.error(">> La probabilidad ingresada '%s' no es un valor valido" % str(prob))
        finally:
            return prob

    def check_asnm_lat(self):
        asnm = self.view.asnm_entry.get()
        lat = self.view.lat_entry.get()
        try:
            asnm = int(asnm)
            lat = float(lat)
        except ValueError:
            self.view.logger.error("datos asnm: '%s' o lat: '%s' no validos" % (str(asnm), str(lat)))
        return asnm, lat

    def check_date(self):
        date = self.view.date_entry.get()
        ddtt = None
        try:
            ddtt = datetime.datetime.strptime(date, '%d/%m/%Y')
            logging.info("> Fecha de datos: %s" % date)
        except ValueError:
            logging.error(">> La fecha '%s' no cumple el formato" % date)
        finally:
            return ddtt

    def start_prediction(self):
        """ when the button for start prediction is pressed """
        self.view.logger.info(":>>>>>> Programa Iniciado <<<<<<<<: <")
        # load file
        self.view.logger.info("Cargando archivo ... ")
        df = self.open_file()
        if 40 in self.view.logger._cache and self.view.logger._cache[40]:
            self.end_program()
            return

        # check configuration
        self.view.logger.info("Revisando Configuracion ...")
        ddtt = self.check_date()
        hier = self.check_hierarchical_model()
        if hier:
            prob = self.check_prob_threshold()
            asnm, lat = self.check_asnm_lat()
        else:
            prob = 1
            asnm, lat = 0, 0
        if 40 in self.view.logger._cache and self.view.logger._cache[40]:
            self.end_program()
            return

        # get data
        self.view.logger.info("Obteniendo Datos ...")
        df = self.open_file()
        if 40 in self.view.logger._cache and self.view.logger._cache[40]:
            self.end_program()
            return
        df_handler = DataHandler(df)
        # input_ = df_handler.prepare_for_classifier(ddtt, asnm, lat, logger=self.view.logger)
        if 40 in self.view.logger._cache and self.view.logger._cache[40]:
            self.end_program()
            return

        # start prediction
        self.view.logger.info("Iniciando Prediccion ...")
        # is_frost, pred_probs = self.model.predict_classifier(input_, threshold=prob)
        if 40 in self.view.logger._cache and self.view.logger._cache[40]:
            self.end_program()
            return

        # give final result (answer yes or no to frost and time/temp of minimum)
        self.view.logger.info("Resultados: ")
        # self.view.logger.info("            es helada: %s" % str(is_frost))
        # self.view.logger.info("            con probabilidad: %s" % str(pred_probs[1]))
        self.end_program()

    def end_program(self):
        self.view.logger.info("Programa terminado <\n------------------------------------------")

    def open_file(self):
        # open file with pandas
        df = None
        try:
            if self.file.split(".")[-1] == "csv":
                df = pd.read_csv(self.file)
            else:
                df = pd.read_excel(self.file)
        except:
            logging.error("Archivo '%s' no cumple con el formato pedido" % self.file)
        return df


def run():
    root = tk.Tk()
    root.title("Predictor Beta v1")
    root.withdraw()
    app = Controller(root)
    root.mainloop()


if __name__ == "__main__":
    run()