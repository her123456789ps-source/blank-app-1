import streamlit as st
from streamlit_server_state import server_state, server_state_lock
import time

st.set_page_config(page_title="IPL Mega Auction 2026", layout="centered")

# --- SHARED ENGINE ---
with server_state_lock["mega_draft"]:
    if "live" not in server_state:
        server_state.live = {
            "p_idx": 0, "curr_bid": 2.0, "bidder": "None", "timer": 15,
            "budgets": {"Ayodhya Strikers": 125.0, "Lucknow Giants": 125.0},
            "scores": {"Ayodhya Strikers": 0, "Lucknow Giants": 0},
            "squads": {"Ayodhya Strikers": [], "Lucknow Giants": []}
        }

players = [
    {"name": "Jasprit Bumrah", "role": "Bowler", "rating": 10, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/jas_1.png"},
    {"name": "Virat Kohli", "role": "Batter", "rating": 9, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/vko_1.png"},
    {"name": "Rashid Khan", "role": "Spinner", "rating": 9, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/rsk_1.png"},
    {"name": "Rinku Singh", "role": "Finisher", "rating": 8, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/ris_1.png"},
    {"name": "Abhishek Sharma", "role": "Opener", "rating": 8, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/abs_1.png"},
    {"name": "Matheesha Pathirana", "role": "Bowler", "rating": 8, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/map_1.png"},
    {"name": "Klaasen", "role": "Batter", "rating": 9, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/klp_1.png"},
    {"name": "Travis Head", "role": "Opener", "rating": 9, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/trh_1.png"},
    {"name": "Narine", "role": "All-Rounder", "rating": 9, "img": "https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_320,q_50/ipl/photos/2023/sun_1.png"}
]

st.title("🏆 IPL Mega Auction 2026")
side = st.radio("Select Team:", ["Ayodhya Strikers", "Lucknow Giants"], horizontal=True)

st.sidebar.header("📊 Live Standings")
opp_side = "Lucknow Giants" if side == "Ayodhya Strikers" else "Ayodhya Strikers"
st.sidebar.metric(f"{side} Budget", f"₹{server_state.live['budgets'][side]:.1f} Cr")
st.sidebar.metric(f"Power Score", f"{server_state.live['scores'][side]} pts")

if server_state.live["p_idx"] < len(players):
    p = players[server_state.live["p_idx"]]
    st.image(p["img"], width=150)
    st.subheader(p["name"])
    st.info(f"Role: {p['role']} | Rating: {p['rating']} pts")
    st.metric("Current Bid", f"₹{server_state.live['curr_bid']:.1f} Cr", f"By: {server_state.live['bidder']}")
    
    next_price = server_state.live["curr_bid"] + 0.5
    if server_state.live["budgets"][side] >= next_price:
        if st.button(f"Bid ₹{next_price} Cr"):
            with server_state_lock["mega_draft"]:
                server_state.live["curr_bid"] = next_price
                server_state.live["bidder"] = side
                server_state.live["timer"] = 15
            st.rerun()

    t_spot = st.empty()
    while server_state.live["timer"] > 0:
        t_spot.metric("⏱️ Timer", f"{server_state.live['timer']}s")
        time.sleep(1)
        with server_state_lock["mega_draft"]:
            server_state.live["timer"] -= 1
        st.rerun()

    if server_state.live["timer"] <= 0:
        winner = server_state.live["bidder"]
        if winner != "None":
            st.success(f"🎊 SOLD to {winner}")
            if st.button("Confirm & Next"):
                with server_state_lock["mega_draft"]:
                    server_state.live["budgets"][winner] -= server_state.live["curr_bid"]
                    server_state.live["scores"][winner] += p["rating"]
                    server_state.live["squads"][winner].append(p["name"])
                    server_state.live["p_idx"] += 1
                    server_state.live["curr_bid"] = 2.0
                    server_state.live["bidder"] = "None"
                    server_state.live["timer"] = 15
                st.rerun()
        else:
            if st.button("Unsold - Skip"):
                with server_state_lock["mega_draft"]:
                    server_state.live["p_idx"] += 1
                    server_state.live["timer"] = 15
                st.rerun()
else:
    st.balloons()
    st.header("🏁 AUCTION FINISHED!")
    winner = max(server_state.live["scores"], key=server_state.live["scores"].get)
    st.title(f"🏆 WINNER: {winner}")
                    
