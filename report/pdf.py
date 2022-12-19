from fpdf import FPDF


class PDF(FPDF):
    """
    Class to create final report
    """
    def __init__(self, title: str = None):
        self.title = title
        super().__init__()

    def header(self):
        """
        Create pdf header
        :return: None
        """
        self.set_font(family='Arial', style='B', size=12)
        self.cell(w=0, txt=self.title, align='L')
        self.ln(10)

    def chapter_title(self, num, label):
        """
        Create chapter title
        :param num: int
            chapter number
        :param label: str
            chapter title
        :return: None
        """
        self.set_font('Arial', 'B', 10)
        self.cell(w=0, h=6, txt='Chapter %d : %s' % (num, label), align='L')
        self.ln(10)

    def chapter_body(self, name, size: int = 10):
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
        self.set_font(family='Arial', style='', size=size)
        self.multi_cell(w=0, h=5, txt=txt)

    def footer(self):
        """
        Create pdf footer
        :return:
        """
        self.set_y(-15)
        self.set_font(family='Arial', size=8)
        self.cell(0, 10, txt=str(self.page_no()), align='R')

    def print_chapter(self, num: list = None, title: list = None, file: list = None):
        """
        :param num: list
            chapter number
        :param title: list
            chapter title
        :param file: list
            chapter text file
        :return: None
        """
        self.add_page()
        for i in range(len(num)):
            self.chapter_title(num=num[i], label=title[i])
            self.chapter_body(name=file[i])

    def create_table(self, file, table, padding):
        """

        :param file: pdf object
            pdf file
        :param table: list
            table with header and values
        :param padding:
        :return: None
        """
        epw = file.w - 2 * file.l_margin
        col_width = epw / len(table[1][0])
        file.cell(w=epw, h=0.0, txt=table[0][0], align='C', ln=1)
        file.set_font(family='Arial', style='', size=8)
        # file.ln(0.5)
        th = file.font_size
        for row in table[1]:
            for value in row:
                # Enter data in columns
                file.cell(w=col_width, h=padding * th, txt=str(value), border=1, align='C')
            file.ln(padding * th)
