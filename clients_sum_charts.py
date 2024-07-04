from pybit.unified_trading import HTTP
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# 读取Excel文件
excel_file_path = '../Base_trade/New_Api_Acc_name.xlsx'  # 请替换为实际的Excel文件路径
df = pd.read_excel(excel_file_path)


# 運行第一個程式的函數
def run_first_program(acc_name, api_key, api_secret):
    # 在這裡放入第一個程式的內容
    print("Api_key:",api_key, "Api_secret:",api_secret)

    try:

        session = HTTP(
            testnet=False,
            api_key=api_key,
            api_secret=api_secret,
        )

    except Exception as e:
        print(e)
        pass

    return(session)

# 運行第二個程式的函數
import pandas as pd

import pandas as pd


import pandas as pd

def reading_the_clients_positions(session, acc_names):
    print("acc_name:", acc_names)

    the_clients_positions = session.get_positions(
        category="linear",
        settleCoin="USDT"
    )
    print("the_clients_positions:", the_clients_positions)

    # 获取每个symbol的positionValue

    positions_list = the_clients_positions['result']['list']
    symbols_list = []
    position_values_list = []
    unrealised_pnls_list = []

    # 创建空的 DataFrame
    df = pd.DataFrame(columns=['Symbol', 'Position_Value', 'Unrealised_PnL','Real_Position_Value'])

    for i, item in enumerate(positions_list):
        symbol = item['symbol']
        try:
            # 嘗試轉換為浮點數（小數）
            position_value = float(item['positionValue'])
        except ValueError:
            try:
                # 如果無法轉換為浮點數，則嘗試轉換為整數
                position_value = int(item['positionValue'])
            except ValueError:
                # 如果無法轉換為整數，表示它不是有效的數字
                position_value = 0

        try:
            # 嘗試轉換為浮點數（小數）
            unrealised_pnls = float(item['unrealisedPnl'])
        except ValueError:
            try:
                # 如果無法轉換為浮點數，則嘗試轉換為整數
                unrealised_pnls = int(item['unrealisedPnl'])
            except ValueError:
                # 如果無法轉換為整數，表示它不是有效的數字
                unrealised_pnls = 0
        # 将symbol和positionValue添加到相应的列表中
        symbols_list.append(symbol)
        position_values_list.append(position_value)
        unrealised_pnls_list.append(unrealised_pnls)

    # 在循环结束后将数据附加到 DataFrame
    df = pd.concat([df, pd.DataFrame(
        {'Symbol': symbols_list, 'Position_Value': position_values_list, 'Unrealised_PnL': unrealised_pnls_list})],
                   ignore_index=True)
    df['Real_Position_Value'] = df['Position_Value'] + df['Unrealised_PnL']

    df = df.dropna()

    # 打印 DataFrame
    print(df)

    df2 = pd.DataFrame(columns=['Acc_Name', 'Total_Equity', 'Remain_USDT'])

    # pie chart data (coins_propotion)
    walletBalance = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="USDT", )
    print("walletBalance:", walletBalance)
    total_equity = float(walletBalance['result']['list'][0]['totalEquity'])
    print("Total Equity:", total_equity)

    Remain_USDT = float(walletBalance['result']['list'][0]['coin'][0]['walletBalance'])
    print("Remain_USDT:", Remain_USDT)

    # 将其他信息添加到 DataFrame
    df2 = pd.concat(
        [df2, pd.DataFrame({'Acc_Name': [acc_names], 'Total_Equity': [total_equity], 'Remain_USDT': [Remain_USDT]})],
        ignore_index=True)
    # df2 = df2.dropna()

    # 打印包含所有信息的最终 DataFrame
    print(df2)

    return df , df2




def shape_diagram_coins_pnl(symbols, position_values, unrealised_pnls):
    x = np.arange(len(symbols))  # 生成X轴位置
    width = 0.35  # 柱状图宽度

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, position_values, width, label='Position Values')
    rects2 = ax.bar(x + width/2, unrealised_pnls, width, label='Unrealised PnLs')

    ax.set_xticks(x)
    ax.set_xticklabels(symbols)
    ax.legend()

    ax.set_xlabel('Symbols')
    ax.set_ylabel('Values')
    ax.set_title('Position Values and Unrealised PnLs for Different Symbols')
    plt.xticks(rotation=45)  # 旋转X轴标签，使其更易读

    # 在每个柱形上添加文本标签
    for i, rect in enumerate(rects1):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=10)  # 设置文本标签的字体大小为10

    for i, rect in enumerate(rects2):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=10)  # 设置文本标签的字体大小为10

    plt.tight_layout()
    plt.show()




joined_df = pd.DataFrame(columns=['Symbol', 'Position_Value', 'Unrealised_PnL','Real_Position_Value'])
joined_df2 = pd.DataFrame(columns=['Acc_Name', 'Total_Equity', 'Remain_USDT'])

# 對於每個輸入的 Acc_Name，運行兩個不同的程式
for index, row in df.iterrows():
    acc_name = row['Acc_Name']
    api_key = row['Api_key']
    api_secret = row['Api_secret']

    # 運行第一個程式
    run_first_program(acc_name,api_key, api_secret)
    session = run_first_program(acc_name , api_key, api_secret)

    # 運行第二個程式
    reading_the_clients_positions(session, acc_name)
    df, df2 = reading_the_clients_positions(session, acc_name)
    joined_df = pd.concat([joined_df, df], ignore_index=True)
    joined_df2 = pd.concat([joined_df2, df2], ignore_index=True)

print("joined_df:",joined_df)
combine_joined_df = joined_df.groupby('Symbol').sum().reset_index()
print("combine_joined_df:",combine_joined_df)

print("joined_df2:",joined_df2)
total_equity_sum = joined_df2['Total_Equity'].sum()

remain_usdt_sum = joined_df2['Remain_USDT'].sum()
print("total_equity_sum:",total_equity_sum)

def current_real_leverage(combine_joined_df, total_equity_sum):
    # 计算每个Symbol的positions_leverage
    combine_joined_df['positions_leverage'] = combine_joined_df['Position_Value'] / total_equity_sum

    # 计算总的real_position_values_sum
    position_values_sum = combine_joined_df['Position_Value'].sum()

    # 计算总体杠杆水平
    real_total_equity_sum = total_equity_sum / total_equity_sum
    current_leverage = position_values_sum/total_equity_sum

    # 生成捧型图
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(combine_joined_df['Symbol'], real_total_equity_sum, label='real_total_equity_sum')
    ax.bar(combine_joined_df['Symbol'], combine_joined_df['positions_leverage'], label='positions_leverage')
    ax.bar("current_leverage", current_leverage, label='current_leverage')
    ax.axhline(y=real_total_equity_sum, color='r', linestyle='--', label='total_equity_leverage')

    # 在柱形内部的中间位置添加小数点后两位的文本标签
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{:.2f}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3個點的垂直偏移
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=14)  # 設置文本標籤的字體大小為14

    autolabel(ax.patches)

    ax.legend()
    ax.set_ylabel('Leverage')
    ax.set_title('Symbol Leverage vs Total Equity')
    plt.xticks(rotation=90)  # 旋转X轴标签，使其更易读

    plt.tight_layout()
    plt.show()

def pie_chart_coins_propotion(combine_joined_df, total_equity_sum):

    symbols = combine_joined_df['Symbol']
    real_position_values = combine_joined_df['Real_Position_Value']

    # 计算总的real_position_values_sum
    print("real_position_values:", real_position_values)
    # 繪製pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(real_position_values, labels=symbols, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # 使得圓餅圖是圓的，而不是橢圓形的
    plt.title('Pie Chart')
    plt.show()

def shape_diagram_coins_pnl(combine_joined_df, total_equity_sum):

    symbols = combine_joined_df['Symbol']
    position_values = combine_joined_df['Position_Value']
    unrealised_pnls = combine_joined_df['Unrealised_PnL']
    x = np.arange(len(symbols))  # 生成X轴位置
    width = 0.35  # 柱状图宽度

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width / 2, position_values, width, label='Position Values')
    rects2 = ax.bar(x + width / 2, unrealised_pnls, width, label='Unrealised PnLs')

    ax.set_xticks(x)
    ax.set_xticklabels(symbols)
    ax.legend()

    ax.set_xlabel('Symbols')
    ax.set_ylabel('Values')
    ax.set_title('Position Values and Unrealised PnLs for Different Symbols')
    plt.xticks(rotation=45)  # 旋转X轴标签，使其更易读

    # 在每个柱形上添加文本标签
    for i, rect in enumerate(rects1):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=10)  # 设置文本标签的字体大小为10

    for i, rect in enumerate(rects2):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=10)  # 设置文本标签的字体大小为10

    plt.tight_layout()
    plt.show()



#運行第三個程式
current_real_leverage(combine_joined_df, total_equity_sum)#

# 運行第四個程式
pie_chart_coins_propotion(combine_joined_df, total_equity_sum)


# # 運行第五個程式
shape_diagram_coins_pnl(combine_joined_df, total_equity_sum)







