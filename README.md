# HOW TO: Run Live Charting With DxFeed Python API in 100 Lines of Code via DASH

Learn how to build live candle charting with this repository. 
[DxFeed Python API](https://dxfeed.readthedocs.io/en/latest/) offers an easy way to get stream financial data.
Together with [Dash framework](https://dash.plotly.com/) one may build production ready service in about 100 lines of
code.

Web widget from this tutorial may be found on [DxFeed website](dxfeed.com)

## Step 1: Prepare the environment

**Optional:** create virtual environment with your favourite tool, e.g.
 [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/), [Poetry](https://python-poetry.org/docs/),
 [Conda Env](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html), etc.
 This will help you in following maintenance.
 
**Install required packages: dash, dxfeed**

```bash
pip3 install dash, dxfeed
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

date_time = datetime.now() - relativedelta(days=5)
endpoint = dx.Endpoint('demo.dxfeed.com:7300')

candle_subscription = endpoint.create_subscription('Candle', date_time=date_time)
``` 

#### Event Handler


### Dash code:

## Step 3: Run server

```bash
python app.py
```

