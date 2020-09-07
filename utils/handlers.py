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
        self.ibm_data = {'Open': DequeWithLock(maxlen=n_events),
                          'High': DequeWithLock(maxlen=n_events),
                          'Low': DequeWithLock(maxlen=n_events),
                          'Close': DequeWithLock(maxlen=n_events),
                          'Time': DequeWithLock(maxlen=n_events),
                         }

    def update(self, events):
        for event in events:
            if event.open > 1:
                if event.symbol.startswith('AAPL'):
                    self.aapl_data['Open'].append(event.open)
                    self.aapl_data['High'].append(event.high)
                    self.aapl_data['Low'].append(event.low)
                    self.aapl_data['Close'].append(event.close)
                    self.aapl_data['Time'].append(datetime.fromtimestamp(event.time // 1000))  # ns to ms
                if event.symbol.startswith('IBM'):
                    self.ibm_data['Open'].append(event.open)
                    self.ibm_data['High'].append(event.high)
                    self.ibm_data['Low'].append(event.low)
                    self.ibm_data['Close'].append(event.close)
                    self.ibm_data['Time'].append(datetime.fromtimestamp(event.time // 1000))
