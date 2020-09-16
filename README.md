# HOW-TO: Run Live Charting With dxFeed Python API in 100 Lines of Code via DASH

[dxFeed Python API](https://dxfeed.readthedocs.io/en/latest/) offers an easy way to receive streaming financial data.
Combined with  [Dash framework](https://dash.plotly.com/), it allows building production-ready service with about 100
lines of code. Learn how to build live charting with this repository.

## Step 1: Prepare the environment

**Optional: create virtual environment**

 In order to facilitate further work, we recommend creating virtual environment with the tool of your choice: 
 [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/), [Poetry](https://python-poetry.org/docs/),
 [Conda Env](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), etc.

 
**Install required packages: dash, dxfeed**

```bash
pip3 install dash dxfeed
```

## Step 2: Source Code

### dxFeed code:

#### Connect and Subscribe

To start receiving the data:
 1. Connect to the endpoint and specify the subscription. Use the demo endpoint provided by the dxFeed team.
 2. Use the Candle event type for charting. Specify the date_time parameter to manage aggregated data.
 
```python
import dxfeed as dx
from datetime import datetime

date_time = datetime.now() - relativedelta(hours=1)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
``` 

#### Implement Event Handler

Process all received events. 

dxFeed Python API has a [default event handler](https://dxfeed.readthedocs.io/en/latest/basic_usage.html) to work with
pandas DataFrames. To process data required for this task only, let’s implement a custom event listener. 
For this:
 1.	Inherit a class from `dxfeed.EventListener`
 2.	Define the self.update(events) method to implement custom process logic. For more details on creating
  a custom event handler, see [our documentation](https://dxfeed.readthedocs.io/en/latest/custom_handler.html)

Note: here we use `self.aapl_buffer` and `self.amzn_buffer` to store previous events. As the subscription is streaming,
the last candle is updated with incoming data with the same timestamp until events with the next timestamp arrive. 
CandleHandler appends a candle to `self.aapl_data` or `self.amzn_data` only when there are no more updates to the 
current candle. 

`utils/handlers.py`:
```python
from datetime import datetime
import dxfeed as dx
from dxfeed.core.utils.data_class import DequeWithLock


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

Associate the event handler with a subscription using the set_event_handler method and define the data you would like 
to process. We get AAPL and AMZN candles in this example.

```python
candle_subscription.set_event_handler(candle_handler).add_symbols(['AAPL&Q{=5m}', 'AMZN&Q{=5m}'])
``` 

### Dash code:

Dash is an efficient Python framework aimed at building web applications. We will use the app.py file without diving 
deep into specifics. For detailed information, visit the [Dash official website](https://plotly.com/)

#### Import components

Import the necessary dash components.

```python
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
```

#### Add dxFeed code

Add dxFeed code from the dxFeed section. 

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

Define the content of your page.
 
* `dcc.Graph` is the block where chart will be displayed
* `dcc.RadioItems` is the block for radio buttons 
* `dcc.Interval` is a hidden element for an [interval](https://dash.plotly.com/dash-core-components/interval) graph update

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
                interval=1*60*1000,  # in milliseconds
                n_intervals=0
            ),
    ])
])
```

#### Create callback function

Callbacks make interactivity possible. These functions may be called by user's actions such as `dcc.Interval` blocks, 
etc. 

Use a callback to update the graph every minute and to display exactly the instrument that is selected with the radio 
button.

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
 
 #### Configure server app
 
Pass configuration as run_server function arguments. For details, see 
[Dash documentation](https://dash.plotly.com/devtools).
 
 ```python
if __name__ == '__main__':
    app.run_server(debug=False)
```

## Step 3: Run server

Run the Python script. Enjoy the charting.

```bash
python app.py
```

