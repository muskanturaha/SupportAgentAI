from collections import deque
from datetime import datetime, timedelta
import pandas as pd

class SpikeDetector:
    """
    5‑minute sliding window; evaluates spike every `check_every` minutes.
    Saves window stats to CSV and triggers callback when threshold breached.
    """
    def __init__(self,
                 window_minutes:int = 5,
                 thresh_neg_percent:float = 0.20,
                 check_every:int = 5,
                 callback=None,
                 history_csv="window_stats.csv"):

        self.window     = deque()
        self.win_min    = window_minutes
        self.thresh     = thresh_neg_percent
        self.check_every= check_every
        self.callback   = callback
        self.next_check = None
        self.history_csv= history_csv
        self.history    = []

    def add(self, ticket:dict):
        now = ticket["timestamp"]
        self.window.append(ticket)

        # purge old
        cut = now - timedelta(minutes=self.win_min)
        while self.window and self.window[0]["timestamp"] < cut:
            self.window.popleft()

        if self.next_check is None:
            self.next_check = (now.replace(second=0, microsecond=0)
                               + timedelta(minutes=self.check_every))

        if now >= self.next_check:
            self._evaluate(now)
            self.next_check += timedelta(minutes=self.check_every)

    # ------------------------------------------------------------------
    def _evaluate(self, now):
        total = len(self.window)
        neg_h = sum(1 for t in self.window
                    if t["emotion"] in {"anger","sadness"} and t["urgency"]=="high")
        pct = (neg_h / total * 100) if total else 0.0

        stat = dict(window_end=now.strftime("%Y-%m-%d %H:%M"),
                    total=total, neg_high=neg_h, percent=round(pct,2))
        self.history.append(stat)
        pd.DataFrame(self.history).to_csv(self.history_csv, index=False)

        if pct >= self.thresh*100 and self.callback:
            self.callback(stat)
