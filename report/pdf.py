import sys
from fpdf import FPDF


class PDF(FPDF):
    """
    Class to create final report
    """

    def __init__(self, title: str = None):
        self.title = title
        super().__init__()
        self.create_title_page()
        self.set_margins(left=25,
                         top=25,
                         right=25)

    def create_title_page(self):
        """
        Create title page
        :return: None
        """
        self.add_page()
        self.image(name=sys.path[1] + '/documentation/MiGUEL_logo.png', y=85, x=0, w=150)
        self.set_font('Arial', 'B', 16)
        self.multi_cell(w=0,
                        h=128,
                        txt='',
                        align='L')
        self.multi_cell(w=0,
                        h=10,
                        txt='Report: ' + self.title,
                        align='LB')
        self.set_font('Arial', 'B', 10)
        self.multi_cell(w=0,
                        h=5,
                        txt='Author: Paul Bohn (Technische Hochschule Köln)',
                        align='LB')
        self.image(name=sys.path[1] + '/documentation/th-koeln.png',
                   y=160,
                   x=11,
                   h=15)
        self.image(name=sys.path[1] + '/documentation/EnerSHelF_logo.png',
                   y=158,
                   x=60,
                   h=18)

    def chapter_title(self, label: str, size: int = 12):
        """
        Create chapter title
        :param label: str
            chapter title
        :param size: int
            font size
        :return: None
        """
        self.set_font('Arial', 'B', size)
        self.cell(w=0,
                  h=6,
                  txt=label,
                  align='L')
        self.ln(10)

    def chapter_body(self, name: str, size: int = 10):
        """
        Create chapter text
        :param size: int
            font size
        :param name: str
            path to txt-file
        :return: None
        """
        # Read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        self.set_font(family='Arial',
                      style='',
                      size=size)
        self.multi_cell(w=0,
                        h=5,
                        txt=txt)

    def footer(self):
        """
        Create pdf footer
        :return: None
        """
        self.set_y(-15)
        self.set_font(family='Arial',
                      size=8)
        self.cell(0,
                  10,
                  txt=str(self.page_no()),
                  align='R')

    def print_chapter(self, chapter_type: list = None, title: list = None, file: list = None, size: int = 12):
        """
        :param chapter_type: bool
            main chapter
        :param size: int
            font size
        :param title: list
            chapter title
        :param file: list
            chapter text file
        :return: None
        """
        for i in range(len(title)):
            if chapter_type[i] is True:
                self.add_page()
            self.chapter_title(label=title[i],
                               size=size)
            self.chapter_body(name=file[i])

    def create_table(self, file, table, padding, sep=True):
        """
        :param sep: bool
            1000 separator
        :param file: pdf object
            pdf file
        :param table: list
            table with header and values
        :param padding: int
            padding of table cells
        :return: None
        """
        epw = file.w - 2 * file.l_margin
        col_width = epw / len(table[1][0])
        file.cell(w=epw,
                  h=0.0,
                  txt=table[0][0],
                  align='C',
                  ln=1)
        file.set_font(family='Arial',
                      style='',
                      size=7.5)
        th = file.font_size
        for row in table[1]:
            for value in row:
                if isinstance(value, (int, float)):
                    alignment = 'R'
                    if sep:
                        value = '{:,}'.format(value)
                    else:
                        value = str(value)
                elif value is None:
                    value = 'None'
                    alignment = 'L'
                else:
                    alignment = 'L'
                    value = str(value)
                # Enter data in columns
                file.cell(w=col_width,
                          h=padding * th,
                          txt=value,
                          border=1,
                          align=alignment)
            file.ln(padding * th)
