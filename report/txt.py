title = 'PV: '
variable = '10 kWp'
text = title + variable


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
        """
        self.file_name = file_name
        self.text = txt
        if file_name is not None:
            self.open()

    def open(self):
        """
        Create new file
        :return:
        """
        file = open(self.file_name + '.txt', 'w')
        file.write(self.text)


if __name__ == '__main__':
    disclaimer = TXTFile(file_name='disclaimer',
                         txt='This report was created automatically by MiGUEL using the data entered.')
    system_config = TXTFile(file_name='2_system_config.txt',
                            txt='This chapter includes all system components and the relevant parameters.\n' + text)
    economy = TXTFile(file_name='economy',
                      txt='This chapter contains a simplified economical calculation.')
    ecology = TXTFile(file_name='ecology',
                      txt='This chapter contains a simplified ecological calculation.')
