from texts import TEXTS
from pathlib import Path
from utils.handlers import CandleHandler
import dxfeed as dx
from dxfeed.core.DXFeedPy import dxf_initialize_logger
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


# dxFeed init
date_time = datetime.now() - relativedelta(hours=1)
dxf_initialize_logger(f'logs/dx_logs_{datetime.now().strftime("%Y%m%d_%H%M")}.log', True, True, True)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
candle_handler = CandleHandler(40)
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'AMZN&Q{=5m}'])

# Dash app
app = dash.Dash(__name__, title='dxFeed Candle Charting')
app.layout = html.Div([
    html.Link(rel='stylesheet', href='/assets/stylesheet.css'),
    html.Div([html.Img(src='assets/dxfeed_logo.png', id='logo'),
              html.Span('PYTHON API', id='app-title')],
             className="header"),
    dcc.Markdown(TEXTS.get('header'), className='md-text', dangerously_allow_html=True),
    html.Div([
        dcc.Interval(
                id='interval-component',
                interval=5*60*1000,  # in milliseconds
                n_intervals=0
            ),
            dcc.Graph(id='candle-graph'),
            html.Div('Data is received directly from Nasdaq and delayed by 30 minutes.', className='graphDisclaimer'),
            dcc.RadioItems(
                id='candle-stocks',
                options=[
                    {'label': 'AAPL', 'value': 'AAPL'},
                    {'label': 'AMZN', 'value': 'AMZN'},
                ],
                value='AAPL'
            )
    ])
])


@app.callback(Output('candle-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('candle-stocks', 'value')])
def update_candle_graph(n, stocks):
    plots = list()  # List with data to display
    if 'AAPL' in stocks:
        plots.append(go.Candlestick(x=candle_handler.aapl_data['Time'].safe_get(),
                                    open=candle_handler.aapl_data['Open'].safe_get(),
                                    high=candle_handler.aapl_data['High'].safe_get(),
                                    low=candle_handler.aapl_data['Low'].safe_get(),
                                    close=candle_handler.aapl_data['Close'].safe_get(),
                                    name='AAPL'))
    if 'AMZN' in stocks:
        plots.append(go.Candlestick(x=candle_handler.amzn_data['Time'].safe_get(),
                                    open=candle_handler.amzn_data['Open'].safe_get(),
                                    high=candle_handler.amzn_data['High'].safe_get(),
                                    low=candle_handler.amzn_data['Low'].safe_get(),
                                    close=candle_handler.amzn_data['Close'].safe_get(),
                                    name='AMZN'))

    return dict(data=plots, layout=go.Layout(title='AAPL/AMZN 5 minute Candles (30 minutes delay from realtime)',
                                             showlegend=False,
                                             uirevision=True,
                                             font=dict(family="Open Sans, serif", size=18,)
                                             ))


if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_silence_routes_logging=True)
