# SupportAgentAI


# 📊 BrandPulse: Real-Time CX Sentiment Watchdog

> An AI-powered agent that monitors customer support messages in real-time, detects spikes in negative sentiment, and alerts your team via Slack. It also visualizes message trends through a live dashboard.

---

## 🚀 What it Does

- **Classifies support messages** (emotion, sentiment, type, urgency)
- **Tracks 5-minute windows** to detect spikes in angry/high-urgency complaints
- **Sends Slack alerts** when thresholds are breached
- **Displays real-time dashboard** with live messages and historical insights
- **Uses a CSV with timestamps** to simulate realistic streaming from Zomato/Swiggy-style support systems

---

## 🧩 Components

| File | Role |
|------|------|
| `classifier.py` | Emotion, sentiment, type, urgency classifier |
| `spike_detector.py` | Sliding-window detector with thresholds |
| `slack_alert.py` | Sends alerts to a Slack webhook |
| `webhook_server.py` | FastAPI server to receive tickets in real-time |
| `fake_support_sender.py` | Simulates support traffic using a CSV |
| `dashboard.py` | Streamlit dashboard with live and historical views |
| `sample_tickets.csv` | Your simulated support messages |
| `classified_output.csv` | Logs classified messages |
| `window_stats.csv` | 5-minute window spike stats |
| `run_all.py` | Launches server, simulator, and dashboard in one shot |

---

## 🧪 Requirements

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install fastapi uvicorn streamlit transformers pandas altair slack_sdk requests
```

---

## 🗃️ CSV Format (`sample_tickets.csv`)

```csv
timestamp,text,channel
2025-07-21 12:00:00,Where is my order? It's late!,chat
2025-07-21 12:01:00,Thanks for the quick fix!,email
...
```

- `timestamp` (datetime)
- `text` (customer message)
- `channel` (chat, email, ticket, etc.)

> The simulator sends these to your webhook every 3 seconds.

---

## ▶️ How to Run the Whole System

### ✅ Option A: One Command (Recommended)

```bash
python run_all.py
```

> This launches:
> - Webhook backend (FastAPI)
> - CSV-based simulator
> - Real-time Streamlit dashboard (auto-opens in browser)

---

### 🛠️ Option B: Manual (3 Terminals)

**Terminal 1: Webhook receiver**

```bash
uvicorn webhook_server:app --reload --port 8000
```

**Terminal 2: Simulate support messages from CSV**

```bash
python fake_support_sender.py
```

**Terminal 3: Live dashboard**

```bash
streamlit run dashboard.py
```

Dashboard: [http://localhost:8501](http://localhost:8501)

---

## 📊 Dashboard Features

- **Live Zone (last 5 min):**
  - Latest messages
  - Live emotion, urgency, type distribution
- **Historical Zone:**
  - Overall trends
  - Line graph of high-urgency negative spikes
- **Alert Banner:**
  - Turns red if spike threshold (20%) breached

---

## 📦 Slack Setup (Optional)

To receive alerts:

1. Go to https://api.slack.com/apps → Create App
2. Add **Incoming Webhooks**
3. Enable & copy your **Webhook URL**
4. Paste into `webhook_server.py`:

```python
callback=lambda a: send_slack_alert("YOUR_SLACK_WEBHOOK_URL", a),
```

---

## 🧠 Why This Matters

Support teams miss patterns hidden in raw tickets. BrandPulse flags:
- Sudden spikes in frustration
- Emotion/urgency you can’t sort manually
- Moments worth catching before churn or social blowback

---

## 🙌 Inspired by

- AI Agent Hackathon by Product Space
- Real-world needs from CX/product teams
- Simplicity-first PM workflows

