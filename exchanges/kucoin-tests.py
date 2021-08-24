from kucoin_futures.client import Trade
from kucoin_futures.client import Market
import json
from datetime import datetime, timedelta


client = Trade(key='611aec82e895f30006a85d47', secret='0ffb74e4-a1b9-4938-bce6-cde4dd7a15cd', passphrase='Gameboy23', is_sandbox=False, url='')
market_data = Market(url='https://api-futures.kucoin.com')
positions = client.get_all_position()
end_time = datetime.now().timestamp() * 1000
start_time_pre = datetime.now() - timedelta(minutes=30)
start_time = start_time_pre.timestamp() * 1000
print('Start: %s', start_time)
print('End: %s', end_time)
#historical_kline_data = market_data.get_kline_data('ETHUSDTM', 1, begin_t=int(start_time), end_t=int(end_time))
#for item in historical_kline_data:
#    print(item[0])
#print(historical_kline_data[0])

fills = client.get_order_list(symbol='ADAUSDTM')
for item in fills['items']:
    timestamp = int(item['createdAt']) / 1000
    dt_obj = datetime.fromtimestamp(timestamp)
    print(f'ID: {item["id"]}\nSymbol: {item["symbol"]}\nValue: {str(float(item["value"])/5)}\nDateTime Posted: {dt_obj}\nSize: {str(item["size"])}\nIsActive: {str(item["isActive"])}')
print('DETAILS: ',client.get_order_details('611c7073ea52b50006bf7768'))   
#print(fills)
for item in positions:
    print(json.dumps(item, indent=2))
    print(str(item['unrealisedPnl']) + '::' + str(item['symbol']))
#position = client.get_position_details('ADAUSDTM')
#print(position['unrealisedPnl'])