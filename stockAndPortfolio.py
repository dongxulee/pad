import pandas as pd

# This is just for now
columnsNames = ['bidPrice', 'bidSize', 'askPrice', 'askSize', 'lastPrice']

class Stock:
    def __init__(self, name):
        self.name = name
        self.histData = pd.DataFrame(columns=columnsNames)

    def dataAdd(self, info):
        df = pd.DataFrame([info], columns=columnsNames)
        self.histData = self.histData.append(df, ignore_index=True)

    def showData(self, num=5):
        print(self.histData.tail(num))
        
    def historicalData(self, num=10):
        return self.histData.tail(num)