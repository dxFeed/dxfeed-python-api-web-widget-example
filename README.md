# HOW TO: Run Live Charting With DxFeed Python API in 100 Lines of Code via DASH

Learn how to build live candle charting with this repository. 
[DxFeed Python API](https://dxfeed.readthedocs.io/en/latest/) offers an easy way to get stream financial data.
Together with [Dash framework](https://dash.plotly.com/) one may build production ready service in about 100 lines of
code.

## Step 1: Prepare the environment

**Optional:** create virtual environment with your favourite tool, e.g.
 [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/), [Poetry](https://python-poetry.org/docs/),
 [Conda Env](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), etc.
 This will help you in following maintenance.
 
**Install required packages: dash, dxfeed**

```bash
pip3 install dash dxfeed
```

## Step 2: Source Code

### DxFeed code:

#### Connection and Subscription

To start receiving the data the user have to connect to the endpoint and to specify the subscription.
Here we use the demo endpoint "demo.dxfeed.com:7300". It provides stream data with delay.

Candle is the type of subscription we need for charting. We should provide `date_time` parameter, because Candle
is a conflated stream.

```python
import dxfeed as dx
from datetime import datetime

date_time = datetime.now() - relativedelta(hours=1)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
``` 

#### Event Handler

After receiving an event it should be processed. DxFeed Python API has a 
[default event handler](https://dxfeed.readthedocs.io/en/latest/basic_usage.html) to work with
pandas DataFrames.

However, for better performance we used custom event listener. Inherit class from `dxfeed.EventListener` and 
define the `self.update(events)` method to implement custom process logic. More details: 
[Custom Event Handler](https://dxfeed.readthedocs.io/en/latest/custom_handler.html)

Note: we use `self.aapl_buffer` and `self.amzn_buffer` to store previous events. Last candle is updated
with new data coming. This is how stream subscription is implemented. CandleHandler appends 
candle to `self.aapl_data` or `self.amzn_data` only when there are no updates to the candle.
It happens when the events have next timestamp.

`utils/handlers.py`:
```python
class CandleHandler(dx.EventHandler):
    def __init__(self, n_events):
        self.aapl_data = {'Open': DequeWithLock(maxlen=n_events),
                          'High': DequeWithLock(maxlen=n_events),
                          'Low': DequeWithLock(maxlen=n_events),
                          'Close': DequeWithLock(maxlen=n_events),
                          'Time': DequeWithLock(maxlen=n_events),
                          }
        self.aapl_buffer = None
        self.amzn_data = {'Open': DequeWithLock(maxlen=n_events),
                          'High': DequeWithLock(maxlen=n_events),
                          'Low': DequeWithLock(maxlen=n_events),
                          'Close': DequeWithLock(maxlen=n_events),
                          'Time': DequeWithLock(maxlen=n_events),
                         }
        self.amzn_buffer = None

    def update(self, events):
        for event in events:
            if event.symbol.startswith('AAPL'):
                if self.aapl_buffer and event.time != self.aapl_buffer.time:
                    self.aapl_data['Open'].append(self.aapl_buffer.open)
                    self.aapl_data['High'].append(self.aapl_buffer.high)
                    self.aapl_data['Low'].append(self.aapl_buffer.low)
                    self.aapl_data['Close'].append(self.aapl_buffer.close)
                    self.aapl_data['Time'].append(datetime.fromtimestamp(self.aapl_buffer.time // 1000))  # ns to ms
                    self.aapl_buffer = event
                else:
                    self.aapl_buffer = event
            if event.symbol.startswith('AMZN'):
                if self.amzn_buffer and event.time != self.amzn_buffer.time:
                    self.amzn_data['Open'].append(self.amzn_buffer.open)
                    self.amzn_data['High'].append(self.amzn_buffer.high)
                    self.amzn_data['Low'].append(self.amzn_buffer.low)
                    self.amzn_data['Close'].append(self.amzn_buffer.close)
                    self.amzn_data['Time'].append(datetime.fromtimestamp(self.amzn_buffer.time // 1000))
                    self.amzn_buffer = event
                else:
                    self.amzn_buffer = event
```

#### Attach Handler, Add Symbols

Event handler should be associated with subscription. This is done via `set_event_handler` method. 
After we defined the handler, we should define the data we'd like to process. From code above - we'd like to 
get `AAPL` and `AMZN` candles. 

```python
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'AMZN&Q{=5m}'])
``` 

### Dash code:

Dash is a productive Python framework for building web applications. We will go through the code of 
`app.py` file without deep dive into details. For more information visit [Dash official website](https://plotly.com/)

#### Imports

Import the necessary dash components.

```python
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
```

#### DxFeed code

Add DxFeed code from the section above. 

```python
from utils.handlers import CandleHandler
import dxfeed as dx
from datetime import datetime
from dateutil.relativedelta import relativedelta

date_time = datetime.now() - relativedelta(days=3)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')
candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
candle_handler = CandleHandler(40)
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'AMZN&Q{=5m}'])
```

#### Set Layout

Here you define what blocks your web page will consist of. 
* `dcc.Graph` is the block where your plot will be displayed.
* `dcc.RadioItems` is the block for radio buttons. 
* `dcc.Interval` is a hidden element for interval graph update.

```python
app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        dcc.Graph(id='candle-graph'),
        dcc.RadioItems(
            id='candle-stocks',
            options=[
                {'label': 'AAPL', 'value': 'AAPL'},
                {'label': 'AMZN', 'value': 'AMZN'},
            ],
            value='AAPL'
        ),
        dcc.Interval(
                id='interval-component',
                interval=1*1000,  # in milliseconds
                n_intervals=0
            ),
    ])
])
```

#### Create callback function

Callbacks make interactivity possible. These functions may be called by user's actions, `dcc.Interval` blocks, etc.
We use callback to update graph every second and to display chosen with radio button symbol. 

```python
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

    return dict(data=plots, layout=go.Layout(title='AAPL/AMZN candles',
                                             showlegend=False,
                                             uirevision=True))
```  
 
 #### Serve app
 
 Pass configurations for application server
 
 ```python
if __name__ == '__main__':
    app.run_server(debug=False)
```

## Step 3: Run server

Simply run Python script. 

```bash
python app.py
```

