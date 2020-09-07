from texts import TEXTS
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


# DxFeed init
date_time = datetime.now() - relativedelta(hours=1)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
candle_handler = CandleHandler(40)
ibm_events_to_show = 40
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'IBM&Q{=5m}'])

# Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    # html.Link(rel='stylesheet', href='/static/stylesheet.css'),
    dcc.Markdown(TEXTS.get('header')),
])


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_silence_routes_logging=True)
