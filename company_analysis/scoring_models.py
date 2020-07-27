import types
from datetime import datetime, timedelta
from pprint import pprint
import company_analysis.financial_statements_entries as financials
import company_analysis.financial_metrics as metrics
import company_analysis.accounting_ratios as ratios
import numpy as np
import pandas as pd

'''
Default Prediction Models
'''


def piotroski_f_score(stock, date=datetime.now(), annual=True, ttm=True, diluted_shares=True,
                      average_assets=False):
    piotroski_dictio = {'Profitability': {},
                        'Financial Leverage, Liquidity, and Source of Funds': {},
                        'Operating Efficiency': {},
                        'Piotroski F-Score': {' ': {' ': {0}}}
                        }

    # Return on Assets (1 point if it is positive in the current year, 0 otherwise)
    return_on_assets_current_year = ratios.return_on_assets(stock=stock, date=date, annual=False, ttm=ttm,
                                                            average_assets=average_assets)
    piotroski_dictio['Profitability']['Return on Assets'] = {
        'Return on Assets Current Year': '{:.3f}'.format(return_on_assets_current_year),
        'ROA Positive in the Current Year ?': return_on_assets_current_year > 0}

    # Operating Cash Flow (1 point if it is positive in the current year, 0 otherwise)
    operating_cash_flow_current_year = financials.cash_flow_operating_activities(stock=stock, date=date, annual=annual,
                                                                                 ttm=ttm)
    piotroski_dictio['Profitability']['Operating Cash Flow'] = {
        'Operating Cash Flow Current Year': '{:.2f}'.format(operating_cash_flow_current_year),
        'OCF Positive in the Current Year ?': operating_cash_flow_current_year > 0}

    # Change in Return of Assets (ROA) (1 point if ROA is higher in the current year compared to the previous one,
    # 0 otherwise)
    return_on_assets_previous_year = ratios.return_on_assets(stock=stock, date=date,
                                                             lookback_period=timedelta(days=365), annual=annual,
                                                             ttm=ttm, average_assets=average_assets)
    piotroski_dictio['Profitability']['Change in Return of Assets'] = {
        'Return on Assets Current Year': '{:.3f}'.format(return_on_assets_current_year),
        'Return on Assets Previous Year': '{:.3f}'.format(return_on_assets_previous_year),
        'ROA Current Year > ROA Previous Year ?': return_on_assets_current_year > return_on_assets_previous_year}

    # Accruals (1 point if Operating Cash Flow/Total Assets is higher than ROA in the current year, 0 otherwise)
    total_assets_current_year = financials.total_assets(stock=stock, date=date, annual=annual, ttm=ttm)
    accruals = operating_cash_flow_current_year / total_assets_current_year
    piotroski_dictio['Profitability']['Accruals'] = {
        'Operating Cash Flow Current Year': '{}'.format(operating_cash_flow_current_year),
        'Total Assets Current Year': '{}'.format(total_assets_current_year),
        'Accruals Current Year': '{:.3f}'.format(accruals),
        'ROA Current Year': '{:.3f}'.format(return_on_assets_current_year),
        'Accruals Current Year > ROA Current Year ?': accruals > return_on_assets_current_year}

    # Change in Leverage (long-term) ratio (1 point if the ratio is lower this year compared to the previous one,
    # 0 otherwise)
    debt_to_assets_current_year = ratios.debt_to_assets(stock=stock, date=date, annual=annual, ttm=ttm)
    debt_to_assets_previous_year = ratios.debt_to_assets(stock=stock, date=date, lookback_period=timedelta(days=365),
                                                         annual=annual, ttm=ttm)
    piotroski_dictio['Financial Leverage, Liquidity, and Source of Funds'][
        'Change in Leverage Ratio'] = {'Debt to Assets Current Year': '{:.3f}'.format(debt_to_assets_current_year),
                                       'Debt to Assets Previous Year': '{:.3f}'.format(debt_to_assets_current_year),
                                       'D/A Current Year < D/A Previous Year ?': debt_to_assets_current_year < debt_to_assets_previous_year}

    # Change in Current ratio (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    current_ratio_current_year = ratios.current_ratio(stock=stock, date=date, annual=annual, ttm=ttm)
    current_ratio_previous_year = ratios.current_ratio(stock=stock, date=date, lookback_period=timedelta(days=365),
                                                       annual=annual, ttm=ttm)
    piotroski_dictio['Financial Leverage, Liquidity, and Source of Funds'][
        'Change in Current Ratio'] = {'Current Ratio Current Year': '{:.3f}'.format(current_ratio_current_year),
                                      'Current Ratio Previous Year': '{:.3f}'.format(current_ratio_previous_year),
                                      'CR Current Year > CR Previous Year ?': current_ratio_current_year > current_ratio_previous_year}

    shares_current_year = financials.total_shares_outstanding(stock=stock, date=date, diluted=diluted_shares,
                                                              annual=False, ttm=False)
    shares_previous_year = financials.total_shares_outstanding(stock=stock, date=date, lookback_period=timedelta(days=365),
                                                               diluted=diluted_shares, annual=False, ttm=False)
    # Change in the number of shares (1 point if no new shares were issued during the last year)
    piotroski_dictio['Financial Leverage, Liquidity, and Source of Funds'][
        'Change in Number of Shares'] = {'Shares Outstanding Current Year': shares_current_year,
                                         'Shares Outstanding Previous Year': shares_previous_year,
                                         'No New Shares Issued ?': shares_current_year <= shares_previous_year}

    # Change in Gross Margin (1 point if it is higher in the current year compared to the previous one, 0 otherwise)
    gross_margin_current_year = ratios.gross_margin(stock=stock, date=date, annual=annual, ttm=ttm)
    gross_margin_previous_year = ratios.gross_margin(stock=stock, date=date, lookback_period=timedelta(days=365),
                                                     annual=annual, ttm=ttm)

    piotroski_dictio['Operating Efficiency']['Gross Margin'] = {
        'Gross Margin Current Year': '{:.3f}'.format(gross_margin_current_year),
        'Gross Margin Previous Year': '{:.3f}'.format(gross_margin_previous_year),
        'GM Current Year > GM Previous Year ?': gross_margin_current_year > gross_margin_previous_year}

    # Change in Asset Turnover ratio (1 point if it is higher in the current year compared to the previous one,
    # 0 otherwise)
    asset_turnover_current_year = ratios.asset_turnover_ratio(stock=stock, date=date, annual=annual, ttm=ttm,
                                                              average_assets=average_assets)
    asset_turnover_previous_year = ratios.asset_turnover_ratio(stock=stock, date=date,
                                                               lookback_period=timedelta(days=365), annual=annual,
                                                               ttm=ttm, average_assets=average_assets)
    piotroski_dictio['Operating Efficiency']['Asset Turnover Ratio'] = {
        'Asset Turnover Ratio Current Year': '{:.3f}'.format(asset_turnover_current_year),
        'Asset Turnover Ratio Previous Year': '{:.3f}'.format(asset_turnover_previous_year),
        'ATO Current Year > ATO Previous Year ?': asset_turnover_current_year > asset_turnover_previous_year}

    # piotroski_dictio['Piotroski F-Score'][' '][' '] = sum([vvv for key, value in piotroski_dictio.items()
    #                                                        for kk, vv in value.items()
    #                                                        for kkk, vvv in vv.items()
    #                                                        if isinstance(vvv, np.bool_)])
    number_of_trues = 0
    for k, v in piotroski_dictio.items():
        for kk, vv in v.items():
            for kkk, vvv in vv.items():
                if isinstance(vvv, np.bool_) and vvv:
                    number_of_trues = number_of_trues + 1

    piotroski_dictio['Piotroski F-Score'][' '][' '] = number_of_trues

    return piotroski_dictio


def altman_z_score(stock, date=datetime.now()):
    A = metrics.working_capital(stock, date) / financials.total_assets(stock, date)
    B = financials.retained_earnings(stock, date) / financials.total_assets(stock, date)
    C = metrics.ebit(stock, date) / financials.total_assets(stock, date)
    D = metrics.market_capitalization(stock, date) / financials.total_liabilities(stock, date)
    E = financials.net_sales(stock, date) / financials.total_assets(stock, date)
    return 1.2 * A + 1.4 * B + 3.3 * C + 0.6 * D + 1.0 * E


def altman_z_score_plus(stock, date=datetime.now()):
    A = metrics.working_capital(stock, date) / financials.total_assets(stock, date)
    B = financials.retained_earnings(stock, date) / financials.total_assets(stock, date)
    C = metrics.ebit(stock, date) / financials.total_assets(stock, date)
    D = financials.total_shareholders_equity(stock, date) / financials.total_liabilities(stock, date)
    stock_industry = metrics.get_stock_industry(stock)
    if ('Manufacturing' not in stock_industry) and ('Manufacturers' not in stock_industry):
        return 6.56 * A + 3.26 * B + 6.72 * C + 1.05 * D
    elif 'Emerging Markets Integrated' in stock_industry:
        return 3.25 + 6.56 * A + 3.26 * B + 6.72 * C + 1.05 * D
    else:
        return altman_z_score(stock, date)


def ohlson_o_score(stock, date=datetime.now()):
    TA = financials.total_assets(stock, date)
    GNP = metrics.gross_national_product_price_index(date)
    TL = financials.total_liabilities(stock, date)
    WC = metrics.working_capital(stock, date)
    CL = financials.current_total_liabilities(stock, date)
    CA = financials.current_total_assets(stock, date)
    X = 1 if TL > TA else 0
    NI = financials.net_income(stock, date)
    NI_prev = financials.net_income(stock, date - timedelta(days=365))
    FFO = financials.cash_flow_operating_activities(stock, date)
    Y = 1 if (NI < 0 and NI_prev < 0) else 0
    return -1.32 - 0.407 * np.log(TA / GNP) + 6.03 * (TL / TA) - 1.43 * (WC / TA) + 0.0757 * (CL / CA) - 1.72 * X \
           - 2.37 * (NI / TA) - 1.83 * (FFO / TL) + 0.285 * Y - 0.521 * ((NI - NI_prev) / (abs(NI) + abs(NI_prev)))


'''
Earnings Manipulation Models
'''


def beneish_m_score(stock, date):
    pass


def montier_c_score(stock, date):
    pass


if __name__ == '__main__':
    date = datetime.now()
    piotroski_dictio = piotroski_f_score('AAPL', date)

    df = pd.DataFrame.from_dict({(i, j, k): l
                                 for i in piotroski_dictio.keys()
                                 for j in piotroski_dictio[i].keys()
                                 for k, l in piotroski_dictio[i][j].items()}, orient='index',
                                columns=[date.strftime('%Y-%m-%d')])
    print(df.to_string())