import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

#### the following is the side bar

st.sidebar.header('Simple Stock Chart :chart:')

ratio = st.sidebar.selectbox ("Ratio of asset A:", [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
int_rate = st.sidebar.text_input("Enter intrest rate:", 0.05)
symbol = st.sidebar.text_input('Enter Symbol One', 'AAPL')
symbol_2 = st.sidebar.text_input('Enter Symbol Two', 'Tsla')
start_date = st.sidebar.date_input('Start Date', dt.date(2023, 1, 1))
end_date = st.sidebar.date_input('End Date')
# sub_button = st.sidebar.button ('Click to get stock price')

st.sidebar.write('QQQ SPY MSFT TSLA GOOG NVDA META LLY SBUX AMZN XLE')
#################   main pannel 
st.subheader (f"{symbol} + {symbol_2} :wave:")

if True :
	ticker 		= yf.Ticker (symbol)
	ticker_2 	= yf.Ticker (symbol_2)
	
	data 		= ticker.history( start=start_date, end= end_date )
	data_2 		= ticker_2.history( start=start_date, end= end_date )

	portfolio = data.copy (deep = True)

	data['Close_norm'] 		=data['Close']/data['Close'][0]
	data_2['Close_norm'] 	=data_2['Close']/data_2['Close'][0]

	portfolio = data.copy (deep = True)
	portfolio.drop('Open', axis = 1, inplace = True)
	portfolio.drop('Volume', axis = 1, inplace = True)
	portfolio.drop('Dividends', axis = 1, inplace = True)
	portfolio['nav'] = data['Close_norm']*ratio + data_2['Close_norm']*(1-ratio)

	fig_3 = go.Figure()
	fig_3.add_trace (go.Scatter (x=data.index, y=data['Close_norm'], mode='lines', name = symbol))
	fig_3.add_trace (go.Scatter (x=data_2.index, y=data_2['Close_norm'], mode='lines', name = symbol_2))
	fig_3.add_trace (go.Scatter (x=portfolio.index, y=portfolio['nav'], mode='lines', name = 'Potfolio'))
	st.plotly_chart(fig_3)

	# st.dataframe (portfolio)

	data['% Change'] =data['Close']/data['Close'].shift(1) -1
	data.dropna(inplace = True)
	data.rename (columns = {'% Change': 'Stock_One'}, inplace = True)
	annual_return = data['Stock_One'].mean()*252*100
	stdev = np.std (data['Stock_One']) *np.sqrt(252)*100

	data_2['% Change'] =data_2['Close']/data_2['Close'].shift(1) -1
	data_2.dropna(inplace = True)
	data_2.rename (columns = {'% Change': 'Stock_Two'}, inplace = True)
	annual_return_2 = data_2['Stock_Two'].mean()*252*100
	stdev_2 = np.std (data_2['Stock_Two']) *np.sqrt(252)*100

	df = pd.merge(data, data_2, left_index=True, right_index=True)
	correlation = df['Stock_One'].corr(df['Stock_Two'])
	covariance = df['Stock_One'].cov(df['Stock_Two'])

	pricing_date, fundamental, news = st.tabs(['Stock Stats', 'Minimium Variance','News'])

	with pricing_date:
		st.subheader (f"Stats of  {symbol}")		
		st.write('Annualized Return of', symbol, ' is:', round (annual_return,2), '%')
		st.write('Annualized Standard Deviation of:', symbol, ' is:', round (stdev,2), '%')
		sharpe = (annual_return-float(int_rate)*100)/stdev
		st.write('Sharpe Ratio:', symbol, ' is:', round (sharpe,2))

		st.subheader (f"Stats of  {symbol_2}")	
		st.write('Annualized Return of', symbol_2, ' is:', round (annual_return_2,2), '%')
		st.write('Annualized Standard Deviation of:', symbol_2, ' is:', round (stdev_2,2), '%')
		sharpe = (annual_return_2-float(int_rate)*100)/stdev_2
		st.write('Sharpe Ratio:', symbol_2, ' is:', round (sharpe,2))

		st.subheader (f"Cor of  {symbol} and {symbol_2}")	
		st.write("Correlation between One and Two:", round(correlation,4))
		st.write("Covariance between One and Two:", round (covariance,10))

		portfolio['% Change'] =portfolio['nav']/portfolio['nav'].shift(1) -1
		portfolio.dropna(inplace = True)
		annual_return_p = portfolio['% Change'].mean()*252*100
		stdev_p = np.std (portfolio['% Change']) *np.sqrt(252)*100

		st.subheader (f"Portfolio of {ratio} of {symbol} and {symbol_2}")	
		st.write('Annualized Return of', 'One + Two', ' is:-----', round (annual_return_p,2), '%')
		st.write('Annualized Standard Deviation of:', 'One + Two', ' is:-----', round (stdev_p,2), '%')
		sharpe = (annual_return_p-float(int_rate)*100)/stdev_p
		st.write('Sharpe Ratio: is:', round (sharpe,2))

	with fundamental:

		re_list =[]
		stdev_list =[]
		ratio_list = []
		sharpe_list = []

		stdev, stdev_2 = stdev/100, stdev_2/100
		annual_return, annual_return_2 = annual_return/100, annual_return_2/100

		for i in range (11):
			i_a, i_b = i*0.1, (1-i*0.1)
			p_return = i_a*annual_return + i_b*annual_return_2
			p_stdev = np.sqrt ((stdev*i_a)**2 + (stdev_2*i_b)**2 + 2*stdev*stdev_2*covariance)
			sharpe = (p_return-float(int_rate))/p_stdev
			
			re_list.append (p_return)
			stdev_list.append (p_stdev)
			ratio_list.append (i_a)
			sharpe_list.append (sharpe)

		mv_prot = pd.DataFrame ({
			'AssetOne' : ratio_list,
			'return': re_list,
			'risk' : stdev_list,
			'SharpeRatio': sharpe_list
			})
		
		fig_F = go.Figure()
		fig_F.add_trace (go.Scatter (x=mv_prot['risk'], y=mv_prot['return'], mode='lines+markers', name = 'mv_prot'))

		fig_F.update_layout(title='Efficient Frontier of two assets',
                   xaxis_title='Risk (stedev)',
                   yaxis_title='Return')

		st.plotly_chart(fig_F)

		fig_risk = go.Figure()
		fig_risk.add_trace (go.Scatter (x=mv_prot['AssetOne'], y=mv_prot['risk'], mode='lines+markers', name = 'mv_prot'))

		fig_risk.update_layout(title='Asset mix vs. Risk',
           xaxis_title='Ratio of Asset One',
           yaxis_title='Risk (stedev)')

		st.plotly_chart(fig_risk)

		# fig_return = go.Figure()
		# fig_return.add_trace (go.Scatter (x=mv_prot['AssetOne'], y=mv_prot['return'], mode='lines+markers', name = 'mv_prot'))
		# st.plotly_chart(fig_return)

		st.write (mv_prot)

	with news:
		# news_one = ticker.news[0]
		for i in range (5):
			news_one = ticker.news[i]
			st.subheader (news_one ['title'])
			st.write (news_one ['link'])
		# st.write (news_one)
		# st.write (type(ticker.news[0]))