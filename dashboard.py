import streamlit as st, pandas as pd, altair as alt, os, time
from datetime import datetime, timedelta

DATA="classified_output.csv"; WIN="window_stats.csv"; REFRESH=5; THRESH=20

st.set_page_config(layout="wide")
st.title("📊 BrandPulse – Real‑Time CX Dashboard")

def load_df(path):
    if not os.path.exists(path) or os.path.getsize(path)==0:
        return pd.DataFrame()
    return pd.read_csv(path)

def to_dt(df,col):
    if col in df.columns:
        df[col]=pd.to_datetime(df[col],errors="coerce")
        df=df[df[col].notna()]
    return df

rerun=st.experimental_rerun

while True:
    df=to_dt(load_df(DATA),"timestamp")
    wf=to_dt(load_df(WIN),"window_end")
    now=datetime.now(); live_cut=now-timedelta(minutes=5)
    live=df[df["timestamp"]>=live_cut]

    # ALERT banner
    if not wf.empty and wf.iloc[-1]["percent"]>=THRESH:
        st.error(f"🚨 Active Spike! {wf.iloc[-1]['percent']}% high-urgency negative.")
    else:
        st.success("✅ No active spike.")

    st.markdown("---")

    # Live Zone
    st.subheader("🟢 Live Zone – last 5 min")
    lc1,lc2=st.columns([1,2])
    with lc1:
        st.dataframe(live.tail(12),height=240,use_container_width=True)
    with lc2:
        if not live.empty:
            c1,c2,c3=st.columns(3)
            with c1: st.bar_chart(live["emotion"].value_counts())
            with c2: st.bar_chart(live["urgency"].value_counts())
            with c3: st.bar_chart(live["type"].value_counts())
        else:
            st.info("Waiting for live data…")

    st.markdown("---")

    # Historical zone
    st.subheader("📘 Historical Zone – session")
    if not df.empty:
        hc1,hc2=st.columns([1,2])
        with hc1:
            st.bar_chart(df["emotion"].value_counts())
            st.bar_chart(df["urgency"].value_counts())
        with hc2:
            if not wf.empty:
                wf["window_end"]=pd.to_datetime(wf["window_end"])
                line=alt.Chart(wf).mark_line(point=True).encode(
                    x="window_end:T",y="percent:Q",
                    tooltip=["window_end:T","total","neg_high","percent"]
                ).properties(height=300)
                rule=alt.Chart(pd.DataFrame({"y":[THRESH]})).mark_rule(color="red").encode(y="y:Q")
                st.altair_chart(line+rule,use_container_width=True)
    else:
        st.info("Waiting for messages…")

    time.sleep(REFRESH)
    rerun()
