
class TXTFile:
    """
    Class to create txt-files for reports
    """
    def __init__(self, file_name: str = None, txt: str = None):
        """
        :param file_name: str
            file name
        :param txt: str
            file text
        :return: None
        """
        self.file_name = file_name
        self.text = txt
        if file_name is not None:
            self.open()

    def open(self):
        """
        Create new file
        :return: None
        """
        file = open(self.file_name + '.txt', 'w')
        file.write(self.text)
