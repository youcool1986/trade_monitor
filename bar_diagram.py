import trade_tools as t_tool
import trade_api as t_api
import non_trade_api as n_t_api
import pandas as pd
import math
import matplotlib.pyplot as plt

trade_api = t_api.Trade
trade_adjust = n_t_api.Trade_adjustments
trade_tools = t_tool.Trade_tool
order_type = trade_api.Order_type_class
# 定义列名
columns = ['Acc_name', 'coin_symbol', 'qty', 'side', 'reduce_only', 'price', 'order_type', 'order_status',
           'total_value', 'ppt_ety']


def trading_session_func(acc_name, accs_info):
    trade_session = trade_api(acc_name, accs_info['Api_key'], accs_info['Api_secret'])
    return trade_session


def empty_df_func():
    # 0.创建空的 DataFrame
    empty_df = pd.DataFrame(columns=columns)
    return empty_df


def wallet_info_func():
    total_position_val, total_equity = trade_session.wallet_balance()
    return total_position_val, total_equity


def order_details_func(order_type, coin_symbol):
    new_orders, flat_orders, SP_orders, SL_orders = order_type.type_of_orders_cancel_func(coin_symbol)
    orders_details_list = []
    for active_order in new_orders:
        orders_details = order_type.check_specific_orders_func(active_order)
        print(f"orders_details: {orders_details}")
        orders_details_list.append(orders_details)

    for active_order in flat_orders:
        orders_details = order_type.check_specific_orders_func(active_order)
        print(f"orders_details: {orders_details}")
        orders_details_list.append(orders_details)

    return orders_details_list

def cur_orders_func(acc_name, empty_df ):

    # 1.把 orders df 融到empty_df當中
    new_orders = trade_session.check_orders(coin_symbol)
    print("new_orders:", new_orders)  # 把list 變做df

    if new_orders == []:
        print("None")
    else:
        empty_df = pd.DataFrame([{
            'Acc_name': acc_name,
            'coin_symbol': order['symbol'],
            'qty': float(order['qty']),
            'side': order['side'],
            'reduce_only': order['reduceOnly'],
            'price': float(order['price']),
            'order_type': order['orderType'],
            'order_status': order['orderStatus'],
            'total_value': float(order['qty']) * float(order['price']),
            'ppt_ety': float(order['qty']) * float(order['price']) / total_equity
        } for order in new_orders])

    return empty_df


def df_position_val_func(empty_df):
    # 2.把 df_position_val 融到empty_df當中
    df_position_val = trading_session.get_position_value(coin_symbol)
    print("df_position_val:", df_position_val)

    if df_position_val.empty:
        print(f"no position holding, {df_position_val}")
    else:
        num_rows = df_position_val.shape[0]
        print("行数:", num_rows)
        df_position_val['ppt_ety'] = df_position_val['total_val'] / total_equity
        print(f"columns: {df_position_val.columns}")
        print(f"df_position_val: {df_position_val}")

        # 创建新行并添加到DataFrame中
        for row_index in range(num_rows):
            print("name:", df_position_val.iloc[row_index]["coins_symbol"])
            new_row = pd.Series([acc_name, df_position_val.iloc[row_index]["coins_symbol"], 0, "cur", 0, 0, 0, 0,
                                 df_position_val.iloc[row_index]['total_val'],
                                 df_position_val.iloc[row_index]['ppt_ety']], index=empty_df.columns)
            print(f"new_row: {new_row}")
            empty_df = pd.concat([empty_df, new_row.to_frame().T], ignore_index=True)
            print(empty_df)

    return empty_df


def expected_val_func(empty_df ,target_coins):
    # 3.把coin_symbol 及 expected_val 變作df ,再放入empty_df

    num_coins = len(target_coins)
    print(num_coins)  # 输出结果为 5

    for row in range(num_coins):
        coin_symbol = target_coins["coins" + str(row + 1)]["coin_symbol"]
        expected_val = target_coins["coins" + str(row + 1)]["expected_val"]
        print(coin_symbol, expected_val)

        row = pd.Series(['testnet2', coin_symbol, 0, "expected", 0, 0, 0, 0, 0, expected_val], index=empty_df.columns)
        if expected_val > 0:
            empty_df = pd.concat([empty_df, row.to_frame().T], ignore_index=True)

    return empty_df


def calculate_df_data_func(empty_df):
    if empty_df.empty:
        grouped_df = pd.DataFrame(columns=columns)  # 创建一个空的 DataFrame
    else:
        # 确保 price 和 qty 列为数值类型
        empty_df['price'] = pd.to_numeric(empty_df['price'], errors='coerce')
        empty_df['qty'] = pd.to_numeric(empty_df['qty'], errors='coerce')

        # 计算 side = "sell" 的加权平均值
        sell_df = empty_df[(empty_df['side'] == 'Sell') & (empty_df["reduce_only"] == True)]
        if sell_df.empty:
            print("no_sell_order")
        else:
            print(f"sell_df: {sell_df}")
            sell_weighted_sum_p = (sell_df['price'] * sell_df['qty']).sum()  # 加权后的值的总和
            sell_qty_sum = sell_df['qty'].sum()  # qty 的总和
            sell_weighted_aver_p = sell_weighted_sum_p / sell_qty_sum  # 加权平均值
            print("加權平均值（sell）:", sell_weighted_aver_p)

        # 计算 side = "buy" 的加权平均值
        buy_df = empty_df[empty_df['side'] == 'Buy']  # 筛选出 side = "buy" 的行
        if buy_df.empty:
            print("no_buy_order")
        else:
            print(f"buy_df: {buy_df}")
            buy_weighted_sum_p = (buy_df['price'] * buy_df['qty']).sum()  # 加权后的值的总和
            buy_qty_sum = buy_df['qty'].sum()  # qty 的总和
            buy_weighted_aver_p = buy_weighted_sum_p / buy_qty_sum  # 加权平均值
            print("加權平均值（buy）:", buy_weighted_aver_p)

        # 修改加权平均值计算部分
        grouped_df = empty_df.groupby(["Acc_name", "coin_symbol", "side"]).apply(lambda x: pd.Series({
            "qty": x["qty"].sum(),
            "price": (x["price"] * x["qty"]).sum() / x["qty"].sum() if x["qty"].sum() != 0 else 0,
            "total_value": x["total_value"].sum(),
            "ppt_ety": x["ppt_ety"].sum()
        })).reset_index()

    # 计算买入和卖出的总值
    grouped_df['total_value'] = grouped_df['qty'] * grouped_df['price']
    print(f"grouped_df: {grouped_df}")

    return grouped_df


def grouped_df_func(grouped_df):
    grouped = grouped_df.groupby(['coin_symbol', 'side']).apply(lambda x: pd.Series({
        "ppt_ety": x["ppt_ety"].sum()
    })).reset_index()
    return grouped


def plot_bar_df(grouped):
    # 过滤 ppt_ety 列中的非数值数据
    df_grouped = grouped[grouped['ppt_ety'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]

    # 使用 pivot_table 进行数据透视
    pivot_df = df_grouped.pivot_table(index='coin_symbol', columns='side', values='ppt_ety', aggfunc='mean')

    # 绘制堆叠条形图
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['blue', 'orange', 'green']  # Buy, cur, expected 对应的颜色
    bars = pivot_df.plot(kind='bar', stacked=False, ax=ax, color=colors)

    plt.title('PPT_ETY by Coin Symbol and Side')
    plt.xlabel('Coin Symbol')
    plt.ylabel('PPT_ETY')
    plt.xticks(rotation=0)
    plt.legend(title='Side')

    # 在每个柱形上方添加数值标签
    for bar in bars.containers:
        for rect in bar:
            height = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                height,  # 调整数值标签位置
                f'{height:.2f}',  # 格式化显示数值
                ha='center', va='bottom', color='black'  # 水平居中，垂直居上
            )

    plt.show()


if __name__ == "__main__":
    acc_name = "testnet2"
    accs_info = {
        "Api_key": "Spm9ezsVIdKTpVuFc1",
        "Api_secret": "24jbLNUNsc2tpLUHarItASOvcMvEmeYuRORp"
    }

    target_coins = {
        "coins1": {"coin_symbol": "DOGEUSDT", "expected_val": 0.3},
        "coins2": {"coin_symbol": "GMTUSDT", "expected_val": 0.3},
        "coins3": {"coin_symbol": "", "expected_val": 0},
        "coins4": {"coin_symbol": "", "expected_val": 0},
        "coins5": {"coin_symbol": "", "expected_val": 0}
    }

    trading_session = trading_session_func(acc_name, accs_info)
    coin_symbol = "ALL"
    trade_session = trading_session_func(acc_name, accs_info)

    empty_df = empty_df_func()
    print(f"empty_df: {empty_df}")

    total_position_val, total_equity = wallet_info_func()
    print(f"{acc_name} total_equity: {int(total_equity)}")

    empty_df = cur_orders_func(acc_name ,empty_df)
    print(f"empty_df:{empty_df}")
    empty_df = df_position_val_func(empty_df)
    print(f"empty_df:{empty_df}")
    empty_df = expected_val_func(empty_df,target_coins)
    print(f"empty_df:{empty_df}")
    grouped_df = calculate_df_data_func(empty_df)
    print(f"grouped_df:{grouped_df}")
    grouped = grouped_df_func(grouped_df)
    print(f"grouped:{grouped}")
    plot_bar_df(grouped)
