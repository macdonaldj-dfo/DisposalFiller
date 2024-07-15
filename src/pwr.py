from pypdf import PdfReader, PdfWriter
from var import max2pdf
import datetime
import os

class PWR:

    path_y = r"\src\form_y.pdf"
    path_n = r"\src\form_n.pdf"

    def __init__(self):
        self.dir = os.getcwd()
        self.py = self.dir + PWR.path_y
        self.pn = self.dir + PWR.path_n
        self.reader = None
        self.writer = None

    def convert_dict(self, values):
        """
        Convert dictionary values from element xpath to pdf box names
        """
        new_dict = dict()

        for key, value in values.items():
            if key == "State":
                term = max2pdf.get(value)
                new_dict[term] = '/Yes'
            elif key == "HazardFree":
                term = max2pdf.get(key)
                new_dict[term] = 'Yes'
            else:
                term = max2pdf.get(key)
                new_dict[term] = value

        new_dict['Date'] = self.get_date()

        return new_dict

    @staticmethod
    def get_date():
        date = datetime.datetime.now()
        return date.strftime("%w-%b-%Y")

    def init(self, y=True):
        """
        Initialize the reader and writer
        """
        self.reader = PdfReader(self.py if y else self.pn)
        self.writer = PdfWriter()

        self.writer.append(self.reader)

    def write_values(self, values):
        """
        Write the data to a pdf
        """
        self.init(values.get("HazardFree"))

        fields = self.convert_dict(values)

        self.writer.update_page_form_field_values(
            self.writer.pages[0],
            fields,
            auto_regenerate=False,
         )

        name = str.upper(values.get("Asset Num")) + " Disposal Form.pdf"

        # Original PDF has owner encryption to preserve structure/formatting and it must be reapplied
        self.writer.encrypt(
            user_password="",
            owner_password="ccg",
            permissions_flag=4294966212,
            algorithm="AES-128"
        )
        with open(self.dir + "\\" + name, "wb") as output:
            self.writer.write(output)

        return True

    @staticmethod
    def show_files():
        os.startfile(os.getcwd())
