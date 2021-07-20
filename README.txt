Server
-This takes http requests and adds them to a postgres database
-postgres database is needed for testing, the table the names need to match up with
 object attribute names in the json of the http requests
-requires node, express, and pg (postgres library)

Program
-Based on the configuration of the env file you can specify whether you want to backtest or trade on a strategy
if you want to backtest your strategy you'll need data to backtest on, the importer file is in charge of gathering data
using the api pertaining to the exchange (only supports binance as of now). When importing the program will make http calls to the
server which will in turn add the data requested from the exchange to the corresponding table within the databse.

-The main purpose of the program is to run a strategy consisting of stochastic RSI fastvalues, a MACD indicator as well as specific crypto trading indicators
 like the ADX indicator and Bollinger Bands for catching the strength of the trend

-If you would like to add your own strategies the program is very adaptable and has set functions that are meant to work across multiple exchanges
