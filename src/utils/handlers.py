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
