import tkinter
from tkinter.font import Font
from tkinter import ttk, messagebox
from mf import MF
from var import Result, __version__
from pwr import PWR
import re


class App:

    label_font = ("Helvetica", 10, "bold")

    def __init__(self, debug=False):

        self.root = tkinter.Tk()
        self.root.title(f"Asset Disposal Form Filler v{__version__}")
        self.root.geometry("1250x750")
        self.root.resizable(0, 0)
        self.text_font = Font(self.root, name="Helvetica", size=12)

        self.input_frame = tkinter.Frame(self.root, padx=15, pady=5, relief="solid", borderwidth=1)
        self.input_frame.pack(fill="x")

        self.result_frame = tkinter.Frame(self.root, padx=5, pady=5, bg="lightgray")
        self.result_frame.pack(fill="both", expand=True)

        self.root.option_add("*Font", self.text_font)

        # ----------Input Area------------------

        self.control_frame = tkinter.Frame(self.input_frame)
        self.control_frame.pack(side="left")

        self.input_label = tkinter.Label(self.control_frame, text="Asset Input")
        self.input_label.grid(sticky="w", row=0, column=0)

        self.input_box = tkinter.Text(self.control_frame, width=45, height=3, wrap="word", font=self.text_font)
        self.input_box.grid(sticky="ew", row=1, column=0, columnspan=3, rowspan=2)

        self.search_button = tkinter.Button(self.control_frame, command=self.search, text="Search")
        self.search_button.grid(row=3, column=2, sticky="e")

        self.save_btn = tkinter.Button(self.control_frame, command=self.print_data, text="Save PDFs")
        self.save_btn.grid(row=3, column=1)

        self.clear_btn = tkinter.Button(self.control_frame, command=self.clear_entries, text="Clear")
        self.clear_btn.grid(row=3, column=0, sticky="w")

        self.demo_btn = tkinter.Button(self.control_frame, command=self.test, text="Demo Data")
        self.toggle_error = tkinter.Button(self.control_frame, command=self.toggle, text="Add Error")

        if debug:
            self.demo_btn.grid(row=1, column=6, padx=15)
            self.toggle_error.grid(row=2, column=6, padx=15)

        # --------------Login Area---------------

        self.login_frame = tkinter.Frame(self.input_frame)
        self.login_frame.pack(side="right")

        self.login_label = tkinter.Label(self.login_frame, text="Maximo Login", font=App.label_font)
        self.login_label.grid(row=0, column=1, pady=5, sticky="e")

        self.user_label = tkinter.Label(self.login_frame, text="Username", font=App.label_font)
        self.user_text = tkinter.Entry(self.login_frame)
        self.user_text.grid(row=1, column=1, pady=5)
        self.user_label.grid(row=1, column=0)

        self.pass_label = tkinter.Label(self.login_frame, text="Password", font=App.label_font)
        self.pass_text = tkinter.Entry(self.login_frame, show="*")
        self.pass_text.grid(row=2, column=1)
        self.pass_label.grid(row=2, column=0)

        ttk.Separator(self.input_frame, orient="vertical").pack(fill="y", anchor="center", side="right", padx=15)

        # --------------Instructions------------

        self.instr_frame = tkinter.Frame(self.input_frame)
        self.instr_frame.pack(side="right", anchor="ne")

        self.instr_label = tkinter.Label(self.instr_frame, text="Instructions:", font=App.label_font)
        self.instr_text = tkinter.Label(self.instr_frame, justify="left", text="Fill in maximo login details. "
                                                                               "These will not be saved.\n"
                                                               "Enter asset numbers with spaces or commas.\n"
                                                               "Hit search and wait. Program may appear frozen.\n"
                                                               "Edit any details and hit Save PDFs.")

        self.instr_label.grid(row=0, column=7, sticky="w")
        self.instr_text.grid(row=1, column=7, sticky="w")

        ttk.Separator(self.input_frame, orient="vertical").pack(fill="y", anchor="center", side="right", padx=15)

        # --------------Scroll bar-------------

        self.canv = tkinter.Canvas(self.result_frame, width=200, bg="lightgray")
        self.canv.pack(side="left", fill="both", expand=True)
        self.sb = tkinter.Scrollbar(self.result_frame, orient="vertical")
        self.sb.pack(side="right", fill="y")

        self.canv.configure(yscrollcommand=self.sb.set)
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)
        self.sb.configure(command=self.canv.yview)

        # ---------------Result Area-------------

        self.attr_list = dict()

        self.canv_frame = tkinter.Frame(self.canv, bg="lightgray", padx=5)
        self.frame_id = self.canv.create_window((0, 0), window=self.canv_frame, anchor="nw")
        self.canv_frame.bind(
            '<Configure>', lambda e: self.canv.configure(scrollregion=self.canv.bbox("all"))
        )

        # ------------Error Area----------------

        self.err_list = dict()

        self.err_frame = tkinter.Frame(self.canv_frame,  bg="lightgray", padx=5, pady=5)
        self.err_frame.pack(fill="x", anchor="nw", expand=True)

        self.root.mainloop()

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def print_data(self):

        if len(self.attr_list) == 0:
            tkinter.messagebox.showinfo("No Data", "There are no entries to save")
            return

        printer = PWR()
        for item in self.attr_list.values():
            print(item.get_data())
            printer.write_values(item.get_data())

        printer.show_files()

    def get_text_input(self):
        inp = self.input_box.get("1.0", "end-1c")
        input_list = re.findall(r"[aA][sS]\d{6}(?:\b)", inp)

        return input_list

    def search(self):

        # AS717327

        if not self.check_login():
            tkinter.messagebox.showinfo("Login", "Please fill in maximo login details")
            return

        search_terms = self.get_search_terms()

        if len(search_terms) == 0:
            tkinter.messagebox.showerror("No Terms", "No valid search terms found")
            return

        mf = MF()

        if not mf.login(self.user_text.get(), self.pass_text.get()):
            tkinter.messagebox.showerror("Login Failure", "Could not log in. Check your username and password")
            return



        for term in search_terms:

            res = mf.get_asset_data(term)

            if type(res) is Result:
                self.create_new_entry(res)
            else:
                self.create_new_error(term, res)

    def check_login(self):

        if len(self.user_text.get()) == 0 or len(self.pass_text.get()) == 0:
            return False

        return True

    def get_search_terms(self):

        term_list = list()

        for i in self.get_text_input():
            if i not in term_list:
                term_list.append(i)
            else:
                print(f"{i} is aa duplicate entry")

        return term_list

    def create_new_entry(self, res):

        if self.attr_list.get(res.AssetNumber):
            return

        print(f"Got result for: {res.AssetNumber}")

        i = InfoPane(self.canv_frame, res)
        i.pack(pady=5)
        self.root.update_idletasks()
        self.attr_list[res.AssetNumber] = i

    def clear_entries(self):
        for item in self.attr_list.values():
            item.close()

        for item in self.err_list.values():
            item.close()

        self.attr_list.clear()
        self.err_list.clear()

    def test(self):
        for i in test_data:
            self.create_new_entry(Result(i))

        print(self.root.winfo_width())

    def create_new_error(self, assetnum, res):

        e = ErrorDisplay(self.err_frame, assetnum, res)
        e.pack()
        self.root.update_idletasks()
        self.err_list[assetnum] = e

    def toggle(self):

        te1 = ErrorDisplay(self.err_frame, "as123456", "Could not fetch result")
        te2 = ErrorDisplay(self.err_frame, "as123457", "Could not fetch result")

        te1.pack()
        te2.pack()


class InfoPane(tkinter.Frame):

    def __init__(self, root, data: Result):
        super().__init__(root)
        self.config(borderwidth=2, relief="sunken")
        self.text_frame = tkinter.Frame(self, padx=5, pady=5)
        self.desc_frame = tkinter.Frame(self, padx=5, pady=5)
        self.separator = ttk.Separator(self, orient="vertical")

        self.text_frame.grid(column=0, row=0, sticky="w")
        self.desc_frame.grid(column=2, row=0, sticky="sen")
        self.separator.grid(column=1, row=0, sticky="ns")

        self.attributes = list()

        # ---------Check Boxes/dropdowns ----------------------

        self.con_frame = tkinter.Frame(self.desc_frame)
        self.data_hzrd = tkinter.BooleanVar(self, value=True)
        self.btn_hzrd = tkinter.Checkbutton(
            self.desc_frame, text="Hazardous Mat. Free?", variable=self.data_hzrd, font=App.label_font)

        self.combo_label = tkinter.Label(self.con_frame, text="Asset Condition", font=App.label_font)
        self.combo_btn = ttk.Combobox(self.con_frame, state="readonly", width=15,
                                     values=("Operational", "Parts Only", "Unknown", "Repair Required", "Scrap Only"))

        self.btn_hzrd.grid(sticky="e", row=5, column=2, pady=10)
        self.con_frame.grid(sticky="w", row=5, column=0, pady=10)
        self.combo_btn.current(0)
        self.combo_label.grid(sticky="w", row=0, column=0)
        self.combo_btn.grid(sticky="w", row=0, column=1, padx=5)

        # ------------------Description Window-----------------

        self.desc_label = tkinter.Label(self.desc_frame, text="Condition Details", font=App.label_font)
        self.desc_box = tkinter.Text(self.desc_frame, height=7)

        self.desc_label.grid(row=0, column=0, sticky="w")
        self.desc_box.grid(row=1, column=0, columnspan=3, pady=3)

        # ------------- Attributes ---------------

        self.attributes.append(Attribute(self.text_frame, "Asset Num", 20, data.AssetNumber))
        self.attributes[-1].grid(column=0, row=0, sticky="w")

        self.attributes.append(Attribute(self.text_frame, "Location", 20, data.Location))
        self.attributes[-1].grid(column=1, row=0, sticky="e")

        self.attributes.append(Attribute(self.text_frame, "Description", 50, data.Name))
        self.attributes[-1].grid(column=0, row=1, sticky="w", columnspan=2)

        self.attributes.append(Attribute(self.text_frame, "Manufacturer", 20, data.Manufacturer))
        self.attributes[-1].grid(column=1, row=2, sticky="e")

        self.attributes.append(Attribute(self.text_frame, "Serial Num", 20, data.SerialNumber))
        self.attributes[-1].grid(column=0, row=2, sticky="w")

        self.attributes.append(Attribute(self.text_frame, "Model Num", 20, data.PartNumber))
        self.attributes[-1].grid(column=0, row=3, sticky="w")

    def get_data(self):

        data = {attr.title: attr.data.get() for attr in self.attributes}
        data["State"] = self.combo_btn.get()
        data["HazardFree"] = self.data_hzrd.get()
        data["Details"] = self.desc_box.get("1.0", "end-1c")

        return data

    def close(self):
        for item in self.attributes:
            item.close()

        self.desc_box.destroy()
        self.desc_label.destroy()
        self.combo_btn.destroy()
        self.btn_hzrd.destroy()
        self.combo_label.destroy()
        self.desc_frame.destroy()
        self.con_frame.destroy()
        self.text_frame.destroy()
        self.destroy()


class Attribute(tkinter.Frame):

    def __init__(self, root, title, width, data):
        tkinter.Frame.__init__(self, root)
        self.config(padx=2, pady=3)
        self.title = title
        self.data = tkinter.StringVar(self, data)
        self.label = tkinter.Label(self, text=title, font=App.label_font)
        self.text_bar = tkinter.Entry(self, name="test", width=width, textvariable=self.data)
        self.label.grid(column=0, row=0, sticky="w")
        self.text_bar.grid(column=0, row=1, sticky="w")

    def close(self):
        self.text_bar.destroy()
        self.label.destroy()
        self.destroy()


class ErrorDisplay(tkinter.Frame):

    def __init__(self, root, assetnum, error):
        tkinter.Frame.__init__(self, root)
        self.label = tkinter.Label(self, text=assetnum, font=App.label_font)
        self.err_label = tkinter.Label(self, text=error)

        self.label.grid(column=0, row=0, sticky="ew")
        self.err_label.grid(column=1, row=0, sticky="ew")

    def close(self):
        self.label.destroy()
        self.err_label.destroy()
        self.destroy()


test_data = [{
    'Name': 'AIS SHORE STATION, SAAB',
    'LocalInfo': 'W2012265  Halifax / Shannon Hill  MHALIFMC-AIS',
    'Manufacturer': 'SAAB AB',
    'PartNumber': '7001-000-801',
    'SerialNumber': '100514',
    'Location': 'MHALIFMC-AIS',
    'AssetNumber': 'AS717327',
},
    {
    'Name': 'AIS SHORE STATION, SAAB',
    'LocalInfo': 'W2012257 Cape Blomidon MCBLOMID-AIS',
    'Manufacturer': 'SAAB AB',
    'PartNumber': '7001-000-801',
    'SerialNumber': '100515',
    'Location': 'MCBLOMID-AIS',
    'AssetNumber': 'AS717328',
}]

if __name__ == "__main__":
    App()
