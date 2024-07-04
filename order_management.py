from pybit.unified_trading import HTTP
import pandas as pd
from trade_api import Trade
import matplotlib.pyplot as plt



"""
current_status : in bar_diagram.py (
required : not done 
input: Clients APIs 
output:holding pattern 
"""

file_path = "../Base_trade/New_Api_Acc_name.xlsx"
try:
    df = pd.read_excel(file_path)
except Exception as e:
    print(f"读取 Excel 文件时出错：{e}")
    exit()

# 将 Acc_Name 列设为索引，以便将其用作字典键
df.set_index("Acc_Name", inplace=True)

Accs = df.index.tolist()

# 准备一个字典来存储匹配结果
accs_info = {}

# 匹配 Accs 列表中的每个 Acc_Name，并获取其对应的 Api_key 和 Api_secret
for acc_name in Accs:
    try:
        api_key = df.loc[acc_name, "Api_key"]
        api_secret = df.loc[acc_name, "Api_secret"]
        accs_info[acc_name] = {"Api_key": api_key, "Api_secret": api_secret}
    except KeyError:
        print(f"无法找到 Acc_Name 为 {acc_name} 的信息。")

for acc_name, info in accs_info.items():
    # 初始化交易会话
    Trade_session = Trade(acc_name, info['Api_key'], info['Api_secret'])
    coin_symbol = "ALL"

    # 获取订单信息和总资产值
    orders_dict, df = Trade_session.check_orders(coin_symbol)
    total_position_val, total_equity = Trade_session.wallet_balance()
    print(f"{acc_name},total_equity:{int(total_equity)}")

    if df.empty:
        grouped_df = pd.DataFrame(columns=["Acc_name", "coin_symbol", "side", "qty", "price"])  # 创建一个空的 DataFrame
    # 根据 Acc_Name 和 coin_symbol 进行分组，并计算 qty 的总和
    else:
        grouped_df = df.groupby(["Acc_name", "coin_symbol", "side"]).agg({"qty": "sum", "price": "mean"}).reset_index()

    print(grouped_df)

    buy_orders_df = grouped_df[grouped_df["side"] == "Buy"]
    buy_order_qty = buy_orders_df["qty"]
    buy_order_price = buy_orders_df["price"]
    grouped_df["buy_order_value"] = buy_order_qty * buy_order_price

    sell_orders_df = grouped_df[grouped_df["side"] == "Sell"]
    sell_order_qty = sell_orders_df["qty"]
    sell_order_price = sell_orders_df["price"]
    grouped_df["sell_order_value"] = sell_order_qty * sell_order_price
    buy_coin_symbol_sum = buy_orders_df.groupby("coin_symbol")["qty"].sum()
    sell_coin_symbol_sum = sell_orders_df.groupby("coin_symbol")["qty"].sum()
    print("buy_coin_symbol_sum:",buy_coin_symbol_sum,type(buy_coin_symbol_sum))

    print(sell_coin_symbol_sum,type(sell_coin_symbol_sum))
    # Initialize dictionaries to store buy order values and total equities for each symbol
    buy_order_values = {}
    sell_order_values = {}
    total_equities = {}

    # Loop through each row in the grouped DataFrame
    for _, row in grouped_df.iterrows():
        acc_name = row["Acc_name"]
        coin_symbol = row["coin_symbol"]
        buy_order_value = row["buy_order_value"]

        # Skip NaN values
        if pd.isnull(buy_order_value):
            continue

        if coin_symbol not in buy_order_values:
            buy_order_values[coin_symbol] = 0
        buy_order_values[coin_symbol] += buy_order_value

        if coin_symbol not in total_equities:
            total_equities[coin_symbol] = total_equity

    # Convert dictionaries to lists for plotting
    symbols = list(buy_order_values.keys())
    buy_order_values_list = list(buy_order_values.values())
    total_equities_list = [total_equities.get(symbol, 0) for symbol in symbols]

    # Plot the buy order value vs total equity data
    plt.figure(figsize=(8, 8))
    labels = symbols + ["Total Equity"]
    sizes = buy_order_values_list + [sum(total_equities_list)]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # 使饼图保持圆形
    plt.title(f"({acc_name})Buy Order Value vs Total Equity")
    plt.show()

    # Calculate total equity including both buy and sell orders
    total_equities_list = [total_equities.get(symbol, 0) for symbol in symbols]
    total_equities_list.append(sum(total_equities_list))

    # Loop through each row in the grouped DataFrame to calculate sell order values
    for _, row in grouped_df.iterrows():
        acc_name = row["Acc_name"]
        coin_symbol = row["coin_symbol"]
        sell_order_value = row["sell_order_value"]

        # Skip NaN values
        if pd.isnull(sell_order_value):
            continue

        if coin_symbol not in sell_order_values:
            sell_order_values[coin_symbol] = 0
        sell_order_values[coin_symbol] += sell_order_value

    # Convert dictionaries to lists for plotting
    sell_order_values_list = list(sell_order_values.values())

    # Plot the sell order value vs total equity data
    plt.figure(figsize=(8, 8))
    labels = list(sell_order_values.keys()) + ["Total Equity"]
    sizes = sell_order_values_list + [sum(total_equities_list)]
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # 使饼图保持圆形
    plt.title(f"({acc_name})Sell Order Value vs Total Equity")
    plt.show()

    buy_orders_df = grouped_df[grouped_df["side"] == "Buy"]
    buy_coin_symbol_sum = buy_orders_df["qty"].sum()

    sell_orders_df = grouped_df[grouped_df["side"] == "Sell"]
    sell_coin_symbol_sum = sell_orders_df["qty"].sum()


