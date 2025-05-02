# stats-invest

The idea of the project is to test a group of investment models based on z-score stat metrics.
For example, to backtest following DCA strategy:
* use weekly BTC price as historical data timeframe
* use moving 13-weeks (a quarter length) window to make investment decision against
* calculate moving z-score for each datapoint
* allocate each week a constant amount of regular investment
* for each given weekly investment decision evaluation take available amount of cash to invest and the current z-scorre.
* The more (by absolute value, but should be negative) the z-score and more cash available the larger current weekly investment should be.
* Specific percentage could be the percentile of weekly points, corresponding to the current z-score.
