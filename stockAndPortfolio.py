import pandas as pd

class Stock:
    def __init__(self, name):
        self.name = name
        self.histData = pd.DataFrame()

    def dataUpdate(self, info):
        pass

    def showData(self, num):
        pass


class Portfolio:
    def __init__(self, name):
        self.name = name
        self.items = dict()

    def addItem(self, stock):
        pass

