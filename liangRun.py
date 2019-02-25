import sys
sys.path.insert(0, 'include')
import shift

# Loading the tickers
file = open("DowJonesTickers.pickle",'rb')
tickers = pickle.load(file)
print(tickers)