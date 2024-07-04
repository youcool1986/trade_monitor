from pybit.unified_trading import HTTP
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取 Excel 文件
try:
    first_df = pd.read_excel('Api_Acc_name2.xlsx')
except Exception as e:
    print(f"读取 Excel 文件时出现错误：{e}")

# 获取用户输入的 Acc_Name 列表
user_inputs = []
acc_name_data = first_df['Acc_Name'].tolist()
print(acc_name_data)
while True:

    user_input = input("请输入 Acc_Name (输入空格结束): ")
    if user_input == "":
        break
    else:
        user_inputs.append(user_input)

# 如果用户输入为 ALL，则自动检查 Excel 表中的所有 Acc_Name
if 'ALL' in user_inputs:
    user_inputs = first_df['Acc_Name'].tolist()

# 从第一个 Excel 表中提取 Api_key 和 Api_secret
try:
    first_excel_data = first_df[first_df['Acc_Name'].isin(user_inputs)][['Acc_Name', 'Api_key', 'Api_secret']]
except KeyError:
    print("Excel 表中缺少必要的列")

# 运行第一个程序的函数
def run_first_program(Api_key, Api_secret):
    print("Api_key:", Api_key, "Api_secret:", Api_secret)
    try:
        session = HTTP(
            testnet=False,
            api_key=Api_key,
            api_secret=Api_secret,
        )
    except Exception as e:
        print(e)
        pass
    return session

# 运行第二个程序的函数
def reading_the_clients_positions(session):
    the_clients_positions = session.get_positions(
        category="linear",
        settleCoin="USDT"
    )
    print("the_clients_positions:", the_clients_positions)

    positions_list = the_clients_positions['result']['list']
    symbols = []
    position_values = []
    unrealised_pnls = []

    for position in positions_list:
        symbol = position['symbol']
        position_value = float(position['positionValue'])
        unrealised_pnl = float(position['unrealisedPnl'])

        symbols.append(symbol)
        position_values.append(position_value)
        unrealised_pnls.append(unrealised_pnl)

    walletBalance = session.get_wallet_balance(
                     accountType="UNIFIED",
                     coin="USDT",)
    print("walletBalance:", walletBalance)
    total_equity = float(walletBalance['result']['list'][0]['totalEquity'])
    print("Total Equity:", total_equity)

    Remain_USDT = float(walletBalance['result']['list'][0]['coin'][0]['walletBalance'])
    print("Remain_USDT:", Remain_USDT)

    print("symbols, position_values, unrealised_pnls , Remain_USDT:", symbols, position_values, unrealised_pnls , Remain_USDT)
    return symbols, position_values, unrealised_pnls , Remain_USDT , total_equity , the_clients_positions

# 计算实际杠杆的函数
def current_real_leverage(total_equity, the_clients_positions):
    print("the_clients_positions:", the_clients_positions)

    symbols = []
    positions = []
    symbol_position_dict = {}

    for i, item in enumerate(the_clients_positions['result']['list']):
        symbol = item['symbol']
        position_value = float(item['positionValue'])

        symbols.append(symbol)
        positions.append(position_value)

        new_variable_name = f"{symbol}_position_value"
        symbol_position_dict[new_variable_name] = position_value

    print("Symbols:", symbols)
    print("Position Values:", positions)

    real_leverage_coin = {}

    for key, value in symbol_position_dict.items():
        real_leverage_coin[key] = value / total_equity

    for key, value in real_leverage_coin.items():
        print(f"{key}: {value}")

    total_coins_real_position = sum(positions)
    print("total_coins_real_position:", total_coins_real_position)

    current_real_leverage = total_coins_real_position / total_equity
    total_equity_leverage = total_equity / total_equity

    print("current_real_leverage:", current_real_leverage)

    current_real_leverage_list = ["current_real_leverage"]
    x = np.arange(len(current_real_leverage_list))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width / 2, [current_real_leverage], width, label='current_real_leverage')
    rects2 = ax.bar(x + width / 2, [total_equity_leverage], width, label='total_equity')

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{:.2f}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=14)

    autolabel(rects1)
    autolabel(rects2)

    x_positions = np.arange(len(symbols))

    for i, symbol in enumerate(symbols):
        rect = ax.bar(x_positions[i] - width / 2, [real_leverage_coin[f"{symbol}_position_value"]], width, label=symbol)
        autolabel(rect)

    plt.yticks(fontsize=18)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(symbols)
    ax.legend()

    ax.set_ylabel('Values')
    ax.set_title(f"{Acc_Name} Current Real Leverage vs Total Equity Leverage")

    plt.tight_layout()
    plt.show()

# 绘制持仓比例饼图的函数
def pie_chart_coins_propotion(symbols, position_values, unrealised_pnls):
    real_position_values = [x + y for x, y in zip(position_values, unrealised_pnls)]
    print("real_position_values:",real_position_values)
    plt.figure(figsize=(6, 6))
    plt.pie(real_position_values, labels=symbols, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title(f"{Acc_Name} Pie Chart")
    plt.show()

# 绘制持仓比例柱状图的函数
def shape_diagram_coins_pnl(symbols, position_values, unrealised_pnls):
    x = np.arange(len(symbols))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, position_values, width, label='Position Values')
    rects2 = ax.bar(x + width/2, unrealised_pnls, width, label='Unrealised PnLs')

    ax.set_xticks(x)
    ax.set_xticklabels(symbols)
    ax.legend()

    ax.set_xlabel('Symbols')
    ax.set_ylabel('Values')
    ax.set_title(f"{Acc_Name} Position Values and Unrealised PnLs for Different Symbols")
    plt.xticks(rotation=45)

    for i, rect in enumerate(rects1):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=10)

    for i, rect in enumerate(rects2):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.show()

# 对于每个输入的 Acc_Name，运行不同的程序
for index, row in first_excel_data.iterrows():
    Acc_Name = row['Acc_Name']
    Api_key = row['Api_key']
    Api_secret = row['Api_secret']

    # 运行第一个程序
    session = run_first_program(Api_key, Api_secret)

    # 运行第二个程序
    symbols, position_values, unrealised_pnls, Remain_USDT, total_equity, the_clients_positions = reading_the_clients_positions(session)

    # 运行第三个程序
    current_real_leverage(total_equity, the_clients_positions)

    # 运行第四个程序
    pie_chart_coins_propotion(symbols, position_values, unrealised_pnls)

    # 运行第五个程序
    shape_diagram_coins_pnl(symbols, position_values, unrealised_pnls)
