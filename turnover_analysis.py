import pandas as pd
import matplotlib.pyplot as plt


def cal_turnover(table):
    stock = pd.DataFrame(raw_port.groupby('Stock_Codes').count().index)
    #주의: 여기서 처음 들어오는 raw portfolio dataframe 들어가야 함!

    Stock_Codes = table.iloc[:, 0]
    Weights = table.iloc[:, 1]
    Stock_Codes_lead1 = table.iloc[:, 2]
    Weights_lead1 = table.iloc[:, 3]

    previouspf = pd.DataFrame({'Stock_Codes': Stock_Codes, 'previousWeights': Weights})
    nextpf = pd.DataFrame({'Stock_Codes': Stock_Codes_lead1, 'nextWeights': Weights_lead1})

    stock = pd.merge(stock, previouspf, how='outer')
    stock = pd.merge(stock, nextpf, how='outer')
    stock = stock.fillna(0)

    stock['net'] = stock['nextWeights'].sub(stock['previousWeights'])
    stock['plusnet'] = stock['net'].apply(lambda x: x if x > 0 else 0)
    stock['minusnet'] = stock['net'].apply(lambda x: -x if x < 0 else 0)

    turnover = min(stock['plusnet'].sum(), stock['minusnet'].sum())

    return turnover


def get_turnover(port):
    global raw_port
    raw_port = port.copy(deep=True)
    port['episode'] = port.index.map(lambda x: x // 240)
    port['Stock_Codes_lead1'] = port['Stock_Codes'].shift(-20)
    port['Weights_lead1'] = port['Weights'].shift(-20)

    turnover_result = port.groupby(['episode', 'Invest_Date'])[
        ['Stock_Codes', 'Weights', 'Stock_Codes_lead1', 'Weights_lead1']].apply(cal_turnover)
    return turnover_result



def turnover_analysis (port, monthly_flag=True, episode_mean_flag=True):
    result_df = get_turnover(port).reset_index()
    result_df = result_df[result_df.index % 12 != 11].reset_index(drop=True)
    result_df.columns = ['episode', 'Invest_Date', 'Turnover ratio']
    if monthly_flag == True:
        result_df.to_csv('./Portfolio_Turnover_Analysis_Monthly.csv')
        print('Portfolio turnover ratio monthly csv 파일로 저장 완료')
        result_df['Turnover ratio'].plot()
        plt.show()
    if episode_mean_flag == True:
        episode_mean_result = result_df.groupby('episode').mean()
        episode_mean_result.to_csv('./Portfolio_Turnover_Analysis_Episode_Mean.csv')
        print('Portfolio turnover ratio episode mean csv 파일로 저장 완료')
        episode_mean_result.plot()
        plt.show()

port = pd.read_csv('./train_log_port.csv')
turnover_analysis(port)