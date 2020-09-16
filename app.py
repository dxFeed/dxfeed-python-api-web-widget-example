from texts import TEXTS
from pathlib import Path
from utils.handlers import CandleHandler
import dxfeed as dx
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
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
candle_handler = CandleHandler(40)
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'AMZN&Q{=5m}'])

# external JavaScript files
external_scripts = [
    'https://ajax.googleapis.com/ajax/libs/webfont/1.6.26/webfont.js',
]

# Dash app
app = dash.Dash(__name__, title='dxFeed Candle Charting', external_scripts=external_scripts,
meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.layout = html.Div([
    # Header Start
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src='assets/images/logo-dxfeed-original.svg', className='logoImage'),
                    html.Span('PYTHON API', className='logoText')
                ], className='headerLogo'),
            ], className='row headerRow'),
        ], className='container')
    ], className='header'),
    # Header End
    html.Div([
        html.Div([
            dcc.Markdown(TEXTS.get('header'), className='mainInfo', dangerously_allow_html=True),
            html.Div([
                dcc.Interval(
                        id='interval-component',
                        interval=5*60*1000,  # in milliseconds
                        n_intervals=0
                    ),
                    dcc.Graph(id='candle-graph', className='graphHolder'),
                    html.Div('Data is received directly from Nasdaq and delayed by 30 minutes.',
                    className='graphDisclaimer'),
                    html.Div([
                        dcc.RadioItems(
                            id='candle-stocks',
                            className='labelButtons',
                            options=[
                                {'label': 'AAPL', 'value': 'AAPL'},
                                {'label': 'AMZN', 'value': 'AMZN'},
                            ],
                            value='AAPL'
                        )
                    ], className='graphLegend')
            ])
        ], className='container')
    ], className='mainContent'),
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

    return dict(data=plots, layout=go.Layout(title='AAPL/AMZN 5 minute candles',
                                             showlegend=False,
                                             uirevision=True,
                                             font=dict(family="Open Sans, sans-serif", size=16,)
                                             ))


if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_silence_routes_logging=True)