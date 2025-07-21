# main.py  (only the run() function changed)
import argparse, pandas as pd, os
from data_stream import ticket_stream
from classifier import classify
from spike_detector import SpikeDetector
from slack_alert import send_slack_alert

def run(csv_path, slack_url):
    detector = SpikeDetector(
        window_minutes   = 5,
        check_every      = 5,
        thresh_neg_percent = 0.20,
        callback         = lambda alert: send_slack_alert(slack_url, alert),
        history_csv      = "window_stats.csv"
    )

    # create output files with headers if they don’t exist
    if not os.path.exists("classified_output.csv"):
        pd.DataFrame(columns=[
            "timestamp","text","channel",
            "sentiment","emotion","type","urgency","confidence"
        ]).to_csv("classified_output.csv", index=False)

    for ticket in ticket_stream(csv_path):
        labels = classify(ticket["text"])
        ticket.update(labels)
        detector.add(ticket)

        # append new row
        pd.DataFrame([ticket]).to_csv(
            "classified_output.csv", mode="a", header=False, index=False
        )

        # console log
        #print(
         #   f"[{ticket['timestamp']:%H:%M}] "
         #   f"{ticket['emotion']}/{ticket['urgency']}/{ticket['type']} → "
         #  f"{ticket['text'][:60]}…"
        #)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="Path to input CSV (simulated stream)")
    ap.add_argument("--slack_url", required=True, help="Slack Incoming Webhook URL")
    args = ap.parse_args()
    run(args.csv, args.slack_url)
