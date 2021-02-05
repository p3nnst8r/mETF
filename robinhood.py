import robin_stocks as r

f = open("rh.key", "r")
rh_username = f.readline()
rh_password = f.readline()
f.close()

login = r.login(rh_username, rh_password)

positions_data = r.get_all_open_crypto_orders()

# response = r.order_buy_crypto_by_quantity('DOGE', 100)

response = r.order_sell_crypto_by_quantity('DOGE', 100)
print(response)