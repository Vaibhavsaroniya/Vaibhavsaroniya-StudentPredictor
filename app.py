"""
app.py — Student Performance Prediction System
MITS Gwalior | AMS Auto-Sync | AI Prediction
"""
import streamlit as st
import pickle, numpy as np, sqlite3, pandas as pd
import time, re, os, sys
import plotly.graph_objects as go

# ── Import AMS scraper (must be in same folder) ────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

_AMS_ERR = ""
try:
    from ams_scraper import start_login, get_state, reset_state, PW_OK
except Exception as _e:
    _AMS_ERR = str(_e)
    PW_OK = False
    def start_login(*a, **k): return False
    def get_state(): return {"status": "idle", "data": None, "error": ""}
    def reset_state(): pass

# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="SPPS — MITS", page_icon="🎓", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600;700&display=swap');
*{font-family:'Rajdhani',sans-serif;}
.main{background:#020818;}
.block-container{padding-top:1rem;}
.hero{background:linear-gradient(135deg,#020818,#0a1628,#020818);
  border:1px solid #00d4ff33;padding:40px;border-radius:22px;text-align:center;margin-bottom:22px;}
.hero h1{font-family:'Orbitron',monospace;font-size:30px;color:#00d4ff;
  text-shadow:0 0 30px #00d4ff88;margin:0;}
.hero p{font-size:15px;color:#88aacc;margin-top:8px;}
.step-box{background:linear-gradient(135deg,#0a1628,#0f2040);
  border:2px solid #00d4ff44;border-radius:18px;padding:30px;
  text-align:center;max-width:680px;margin:0 auto;animation:fi .4s ease;}
@keyframes fi{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.step-title{font-family:'Orbitron',monospace;color:#00d4ff;font-size:17px;margin-bottom:6px;}
.step-sub{color:#88aacc;font-size:13px;}
.dot-wrap{display:flex;justify-content:center;align-items:center;gap:8px;margin-bottom:14px;}
.dot{width:12px;height:12px;border-radius:50%;background:#0a1628;border:2px solid #00d4ff22;}
.dot.active{background:#00d4ff;box-shadow:0 0 10px #00d4ff;border-color:#00d4ff;}
.dot.done{background:#00ff88;border-color:#00ff88;}
.dot-line{width:28px;height:2px;background:#00d4ff22;}
.dot-line.done{background:#00ff88;}
.ams-box{background:linear-gradient(135deg,#0d0d2a,#1a1a3e);
  border:2px solid #7c4dff44;border-radius:18px;padding:26px;
  text-align:center;max-width:580px;margin:0 auto 16px;}
.ams-box h3{font-family:'Orbitron',monospace;color:#a78bfa;font-size:14px;margin-bottom:4px;}
.inst-badge{padding:6px 14px;border-radius:28px;display:inline-block;
  font-family:'Orbitron',monospace;font-size:11px;margin:6px 0;}
.mits-b{background:#001a3d;border:1px solid #00d4ff;color:#00d4ff;}
.other-b{background:#1a1a00;border:1px solid #ffcc00;color:#ffcc00;}
.locked-b{background:linear-gradient(135deg,#003d1f,#006633);border:1px solid #00ff88;
  color:#00ff88;padding:4px 12px;border-radius:18px;
  font-family:'Orbitron',monospace;font-size:10px;display:inline-block;margin-left:6px;}
.subj-card{background:linear-gradient(135deg,#0a1628,#0d1a36);
  border:1px solid #00d4ff22;border-radius:12px;padding:14px 16px;margin:5px 0;}
.subj-name{color:#88ccff;font-size:14px;font-weight:700;}
.subj-code{color:#446688;font-size:11px;font-family:'Orbitron',monospace;}
.subj-fac{color:#88aacc;font-size:12px;margin-top:3px;}
.pct-g{font-family:'Orbitron',monospace;font-size:20px;color:#00ff88;}
.pct-y{font-family:'Orbitron',monospace;font-size:20px;color:#ffcc00;}
.pct-r{font-family:'Orbitron',monospace;font-size:20px;color:#ff4444;}
.type-t{background:#1a237e;color:#82b1ff;padding:2px 8px;border-radius:6px;font-size:10px;}
.type-l{background:#1b5e20;color:#69f0ae;padding:2px 8px;border-radius:6px;font-size:10px;}
.type-n{background:#4a148c;color:#ea80fc;padding:2px 8px;border-radius:6px;font-size:10px;}
.stat-card{background:linear-gradient(135deg,#0a1628,#0f2040);
  border:1px solid #00d4ff44;border-radius:14px;padding:16px;text-align:center;}
.stat-card h2{font-family:'Orbitron',monospace;color:#00d4ff;font-size:28px;margin:0;}
.stat-card p{color:#88aacc;font-size:12px;margin:4px 0 0;}
.pass-box{background:linear-gradient(135deg,#003d1f,#006633);border:2px solid #00ff88;
  padding:24px;border-radius:14px;text-align:center;
  font-family:'Orbitron',monospace;font-size:20px;color:#00ff88;
  animation:gG 2s ease-in-out infinite;}
@keyframes gG{0%,100%{box-shadow:0 0 20px #00ff8844}50%{box-shadow:0 0 40px #00ff8888}}
.fail-box{background:linear-gradient(135deg,#3d0000,#660000);border:2px solid #ff4444;
  padding:24px;border-radius:14px;text-align:center;
  font-family:'Orbitron',monospace;font-size:20px;color:#ff4444;
  animation:gR 2s ease-in-out infinite;}
@keyframes gR{0%,100%{box-shadow:0 0 20px #ff444444}50%{box-shadow:0 0 40px #ff444488}}
.blocked-box{background:linear-gradient(135deg,#3d1a00,#2a1000);border:2px solid #ff8800;
  border-radius:14px;padding:14px;text-align:center;
  font-family:'Orbitron',monospace;color:#ff8800;font-size:15px;}
.gc{background:linear-gradient(135deg,#0a1628aa,#0f2040aa);
  border:1px solid #00d4ff33;border-radius:13px;padding:16px;margin:6px 0;}
.gc h3{color:#00d4ff;font-family:'Orbitron',monospace;font-size:12px;}
.gc p{color:#88aacc;font-size:13px;}
.ab{background:linear-gradient(135deg,#3d0000,#1a0000);border:1px solid #ff4444;
  border-left:4px solid #ff4444;border-radius:11px;padding:12px;margin:6px 0;}
.ab h4{color:#ff4444;margin:0 0 4px;font-family:'Orbitron',monospace;font-size:11px;}
.ab p{color:#ffaaaa;margin:0;font-size:13px;}
.rb{background:linear-gradient(135deg,#001a3d,#002a5e);border:1px solid #00d4ff44;
  border-left:4px solid #00d4ff;border-radius:11px;padding:12px;margin:6px 0;}
.rb h4{color:#00d4ff;margin:0 0 4px;font-family:'Orbitron',monospace;font-size:11px;}
.rb p{color:#88ccff;margin:0;font-size:13px;}
.wb{background:linear-gradient(135deg,#2a1a00,#1a1000);border:1px solid #ffcc00;
  border-left:4px solid #ffcc00;border-radius:11px;padding:12px;margin:6px 0;}
.wb h4{color:#ffcc00;margin:0 0 4px;font-family:'Orbitron',monospace;font-size:11px;}
.wb p{color:#ffeeaa;margin:0;font-size:13px;}
.pb{background:#0a1628;border-radius:8px;height:9px;border:1px solid #00d4ff22;margin:4px 0;}
.pg{height:9px;border-radius:8px;background:linear-gradient(90deg,#00ff88,#00cc66);}
.py{height:9px;border-radius:8px;background:linear-gradient(90deg,#ffcc00,#ff9900);}
.pr{height:9px;border-radius:8px;background:linear-gradient(90deg,#ff4444,#cc0000);}
.sec{font-family:'Orbitron',monospace;font-size:20px;color:#00d4ff;
  text-align:center;text-shadow:0 0 20px #00d4ff66;margin:14px 0;}
.prof-card{background:linear-gradient(135deg,#0a1628,#0f2040);
  border:1px solid #00d4ff44;border-radius:13px;padding:14px;
  text-align:center;margin-bottom:14px;}
.prof-name{font-family:'Orbitron',monospace;color:#00d4ff;font-size:17px;}
.prof-email{color:#88aacc;font-size:13px;margin-top:3px;}
.footer{background:linear-gradient(135deg,#0a1628,#020818);
  border-top:1px solid #00d4ff33;padding:26px;text-align:center;
  margin-top:32px;border-radius:13px;}
.footer h3{font-family:'Orbitron',monospace;color:#00d4ff;font-size:14px;}
.footer p{color:#88aacc;font-size:12px;}
.footer a{color:#00d4ff;text-decoration:none;}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#020818,#0a1628);
  border-right:1px solid #00d4ff22;}
.stButton>button{background:linear-gradient(135deg,#00d4ff22,#0066ff22)!important;
  border:1px solid #00d4ff!important;color:#00d4ff!important;
  font-family:'Orbitron',monospace!important;font-size:11px!important;
  border-radius:9px!important;padding:10px!important;transition:all .3s!important;}
.stButton>button:hover{background:linear-gradient(135deg,#00d4ff44,#0066ff44)!important;
  box-shadow:0 0 14px #00d4ff44!important;}
.stTextInput>div>div>input{background:#0a1628!important;border:1px solid #00d4ff44!important;
  color:white!important;border-radius:9px!important;font-size:14px!important;}
hr{border-color:#00d4ff22!important;}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
DEF = {
    "step": 0, "mode": "manual",
    "name": "", "email": "", "institute": "", "roll": "", "enr": "",
    "att": 75, "hrs": 5, "result": None,
    "locked": False, "subjects": [], "overall": 0.0,
    "tc": 0, "tl": 0, "ta": 0, "status_lbl": "",
}
for k, v in DEF.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════
DB = r"C:\JAVA\StudentPredictor\students.db"

def db_init():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, institute TEXT, roll TEXT,
        attendance REAL, study_hours INTEGER, result TEXT)""")
    c.commit(); c.close()

def db_save(name, email, inst, roll, att, hrs, res):
    c = sqlite3.connect(DB)
    c.execute("INSERT INTO predictions VALUES(NULL,?,?,?,?,?,?,?)",
              (name,email,inst,roll,att,hrs,res))
    c.commit(); c.close()

def db_all():
    c = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM predictions", c)
    c.close(); return df

db_init()
MODEL = pickle.load(open(r"C:\JAVA\StudentPredictor\model.pkl", "rb"))

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def parse_email(raw):
    e = raw.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', e):
        return None, None, None
    d = e.split('@')[1]
    if 'mitsgwl.ac.in' in d or 'mitsgwalior.in' in d:
        return "MITS Gwalior", e.split('@')[0], e
    for dk,n in {'iitd.ac.in':'IIT Delhi','bits-pilani.ac.in':'BITS Pilani',
                 'gmail.com':'Personal','outlook.com':'Personal'}.items():
        if dk in d: return n, d, e
    return d.split('.')[0].upper(), d, e

def bv(p):
    return ("pg","#00ff88") if p>=75 else ("py","#ffcc00") if p>=50 else ("pr","#ff4444")

def pclass(p):
    return "pct-g" if p>=75 else "pct-y" if p>=50 else "pct-r"

def tbadge(t):
    t = (t or "").upper()
    cls = "type-l" if t=="LAB" else "type-n" if t in("NEC","PRACTICAL") else "type-t"
    return f"<span class='{cls}'>{t or 'THEORY'}</span>"

def prof_html(name, email, inst, locked=False):
    is_m = "MITS" in inst
    bc   = "mits-b" if is_m else "other-b"
    ic   = "🎓" if is_m else "🏫"
    lb   = "<span class='locked-b'>🔒 AMS VERIFIED</span>" if locked else ""
    return (f"<div class='prof-card'><div class='prof-name'>{name}</div>"
            f"<div class='prof-email'>📧 {email}</div>"
            f"<div style='margin-top:7px;'>"
            f"<span class='inst-badge {bc}'>{ic} {inst}</span>{lb}"
            f"</div></div>")

# ══════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════
def pie_chart(att, total, pct):
    fig = go.Figure(go.Pie(
        labels=["Present","Absent"], values=[att, max(total-att,0)],
        hole=0.55, marker_colors=["#00ff88","#ff4444"],
        textinfo="percent",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=10,b=10,l=10,r=10), height=250,
        annotations=[dict(text=f"<b>{pct:.1f}%</b>",x=0.5,y=0.5,
                          font_size=20,font_color="#00d4ff",showarrow=False)]
    )
    return fig

def bar_chart(subjects):
    if not subjects: return None
    names  = [s["name"][:18]+("…" if len(s["name"])>18 else "") for s in subjects]
    pcts   = [s["pct"] for s in subjects]
    colors = ["#00ff88" if p>=75 else "#ffcc00" if p>=50 else "#ff4444" for p in pcts]
    fig = go.Figure(go.Bar(
        x=names, y=pcts, marker_color=colors,
        text=[f"{p:.0f}%" for p in pcts], textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=75, line_dash="dash", line_color="#ffcc00",
                  annotation_text="75%", annotation_font_color="#ffcc00")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(2,8,24,0.8)",
        xaxis=dict(tickfont=dict(color="#88aacc",size=10), gridcolor="#00d4ff11"),
        yaxis=dict(tickfont=dict(color="#88aacc"), gridcolor="#00d4ff11",
                   range=[0,115], title="Attendance %", titlefont=dict(color="#88aacc")),
        margin=dict(t=10,b=70,l=40,r=10), height=300,
        font=dict(color="white"),
    )
    return fig

def radar_chart(subjects):
    if len(subjects) < 3: return None
    cats = [s["name"][:12] for s in subjects] + [subjects[0]["name"][:12]]
    vals = [s["pct"] for s in subjects] + [subjects[0]["pct"]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(0,212,255,0.12)",
        line=dict(color="#00d4ff", width=2),
        hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(bgcolor="rgba(10,22,40,0.8)",
                   radialaxis=dict(visible=True,range=[0,100],
                                   tickfont=dict(color="#88aacc",size=9),
                                   gridcolor="#00d4ff22"),
                   angularaxis=dict(tickfont=dict(color="#88ccff",size=10),
                                    gridcolor="#00d4ff22")),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        margin=dict(t=10,b=10,l=30,r=30), height=280,
    )
    return fig

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown(
    "<div style='text-align:center;padding:10px 0;'>"
    "<div style='font-family:Orbitron,monospace;font-size:12px;color:#00d4ff;'>🎓 SPPS</div>"
    "<div style='color:#88aacc;font-size:10px;'>MITS Gwalior</div></div>",
    unsafe_allow_html=True
)
NAV = st.sidebar.selectbox("", [
    "🏠 Home & Predict","🏆 Rankings","⚠️ At Risk",
    "📅 Attendance Tracker","📊 Dashboard","🗄️ Database","ℹ️ About"
])
st.sidebar.markdown("---")
df_s = db_all()
ps = len(df_s[df_s.result=='Pass']) if len(df_s)>0 else 0
fs = len(df_s[df_s.result=='Fail']) if len(df_s)>0 else 0
st.sidebar.markdown(
    f"<div class='gc' style='margin:3px;'>"
    f"<div style='color:#00d4ff;font-family:Orbitron,monospace;font-size:10px;'>LIVE STATS</div>"
    f"<div style='color:white;font-size:18px;margin-top:3px;'>{len(df_s)} Students</div>"
    f"<div style='color:#00ff88;'>✅ {ps} Passed</div>"
    f"<div style='color:#ff4444;'>❌ {fs} Failed</div></div>",
    unsafe_allow_html=True
)
if st.sidebar.button("🔄 New Prediction"):
    reset_state()
    for k,v in DEF.items(): st.session_state[k]=v
    st.rerun()

# ══════════════════════════════════════════════════════════════
# HOME & PREDICT
# ══════════════════════════════════════════════════════════════
if NAV == "🏠 Home & Predict":
    st.markdown(
        "<div class='hero'><h1>🎓 STUDENT PERFORMANCE PREDICTION SYSTEM</h1>"
        "<p>AI Powered • Random Forest • 95% Accuracy • MITS AMS Auto-Sync</p></div>",
        unsafe_allow_html=True
    )

    def dc(i): return "done" if i<st.session_state.step else "active" if i==st.session_state.step else ""
    def lc(i): return "done" if i<st.session_state.step else ""
    LBLS = ["Login","Attendance","Study Hours","Result"]
    st.markdown(
        "<div class='dot-wrap'>"
        + "".join(f"<div class='dot {dc(i)}'></div>" +
                  (f"<div class='dot-line {lc(i)}'></div>" if i<3 else "")
                  for i in range(4))
        + "</div>"
        f"<div style='text-align:center;color:#88aacc;font-size:12px;margin-bottom:14px;'>"
        f"📍 {LBLS[min(st.session_state.step,3)]} | Step {st.session_state.step+1} of 4</div>",
        unsafe_allow_html=True
    )

    # ══════════════════════════════════════════════════
    # STEP 0 — Login
    # ══════════════════════════════════════════════════
    if st.session_state.step == 0:

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✏️  MANUAL ENTRY", use_container_width=True, key="bm"):
                st.session_state.mode = "manual"; st.rerun()
        with c2:
            if st.button("🎓  LOGIN WITH INSTITUTE EMAIL", use_container_width=True, key="ba"):
                st.session_state.mode = "ams"; st.rerun()

        mode = st.session_state.mode
        color = "#00d4ff" if mode == "ams" else "#ffcc00"
        label = "🔒 INSTITUTE EMAIL (AMS)" if mode == "ams" else "✏️ MANUAL ENTRY"
        st.markdown(
            f"<div style='text-align:center;margin:6px 0 16px;'>"
            f"<span style='background:#0a1628;border:1px solid {color};color:{color};"
            f"padding:4px 16px;border-radius:16px;font-family:Orbitron,monospace;font-size:10px;'>"
            f"{label}</span></div>",
            unsafe_allow_html=True
        )

        # ──────────────────────────────────────────────
        # MANUAL MODE
        # ──────────────────────────────────────────────
        if mode == "manual":
            st.markdown(
                "<div class='step-box'>"
                "<div class='step-title'>📝 STUDENT REGISTRATION</div>"
                "<div class='step-sub'>Enter your details manually</div></div>",
                unsafe_allow_html=True
            )
            _, col, _ = st.columns([1,2,1])
            with col:
                st.text_input("👤 Full Name", placeholder="Vaibhav Singh Saroniya", key="mn")
                st.text_input("📧 Institute Email", placeholder="24ai10va73@mitsgwl.ac.in", key="me")
                nv = st.session_state.get("mn","").strip()
                ev = st.session_state.get("me","").strip()
                if ev:
                    p = parse_email(ev)
                    if p[0]:
                        is_m = "MITS" in p[0]
                        st.markdown(
                            f"<div style='text-align:center;margin:5px 0;'>"
                            f"<span class='inst-badge {'mits-b' if is_m else 'other-b'}'>"
                            f"{'🎓' if is_m else '🏫'} {p[0]}</span></div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown("<div style='color:#ff4444;text-align:center;font-size:13px;'>⚠️ Invalid email</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("NEXT → ATTENDANCE ▶", use_container_width=True, key="mnext"):
                    if not nv: st.error("Enter your name!"); st.stop()
                    if not ev: st.error("Enter your email!"); st.stop()
                    pr = parse_email(ev)
                    if not pr[0]: st.error("Invalid email!"); st.stop()
                    st.session_state.name = nv
                    st.session_state.email = pr[2]
                    st.session_state.institute = pr[0]
                    st.session_state.roll = pr[1] or ""
                    st.session_state.locked = False
                    st.session_state.step = 1
                    st.rerun()

        # ──────────────────────────────────────────────
        # AMS MODE
        # ──────────────────────────────────────────────
        else:
            # AMS portal header card
            st.markdown(
                "<div class='ams-box'>"
                "<div style='font-size:32px;'>🏛️</div>"
                "<h3>ACADEMICS MANAGEMENT SYSTEM</h3>"
                "<p style='color:#88aacc;font-size:12px;margin:4px 0;'>"
                "Madhav Institute of Technology &amp; Science, Gwalior</p>"
                "<div style='background:#0a1628;border:1px solid #7c4dff22;border-radius:8px;"
                "padding:8px 14px;margin:10px 0 6px;font-size:12px;color:#88aacc;'>"
                "Login with Institute email: "
                "<span style='color:#a78bfa;'>@mitsgwl.ac.in</span> (Students) | "
                "<span style='color:#a78bfa;'>@mitsgwalior.in</span> (Faculty)"
                "</div></div>",
                unsafe_allow_html=True
            )

            _, col, _ = st.columns([1,2,1])
            with col:
                st.text_input("📧 Institute Email", placeholder="24ai10va73@mitsgwl.ac.in", key="ae")
                ev = st.session_state.get("ae","").strip()
                if ev:
                    pr = parse_email(ev)
                    if pr[0]:
                        is_m = "MITS" in pr[0]
                        st.markdown(
                            f"<div style='text-align:center;margin:4px 0;'>"
                            f"<span class='inst-badge {'mits-b' if is_m else 'other-b'}'>"
                            f"{'🎓' if is_m else '🏫'} {pr[0]}</span></div>",
                            unsafe_allow_html=True
                        )

                st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

                # ── Read current AMS state ──────────────
                ams = get_state()

                # ── STATE: DONE ─────────────────────────
                if ams["status"] == "done" and ams["data"]:
                    d = ams["data"]
                    st.session_state.name      = d.get("name") or ev.split("@")[0].title()
                    st.session_state.email     = ev
                    st.session_state.institute = "MITS Gwalior"
                    st.session_state.roll      = d.get("enrollment","")
                    st.session_state.enr       = d.get("enrollment","")
                    st.session_state.att       = round(float(d.get("overall_pct", 0)))
                    st.session_state.locked    = True
                    st.session_state.subjects  = d.get("subjects",[])
                    st.session_state.overall   = float(d.get("overall_pct",0))
                    st.session_state.tc        = d.get("total_courses",0)
                    st.session_state.tl        = d.get("total_classes",0)
                    st.session_state.ta        = d.get("classes_attended",0)
                    st.session_state.status_lbl= d.get("overall_status","")
                    reset_state()
                    st.success(f"✅ Fetched! {len(d.get('subjects',[]))} subjects | {d.get('overall_pct',0):.1f}%")
                    time.sleep(1.5)
                    st.session_state.step = 1
                    st.rerun()

                # ── STATE: RUNNING ──────────────────────
                elif ams["status"] == "running":
                    st.markdown(
                        "<div style='background:#001a3d;border:1px solid #00d4ff44;"
                        "border-radius:11px;padding:14px;text-align:center;margin:6px 0;'>"
                        "<div style='font-family:Orbitron,monospace;color:#00d4ff;font-size:11px;'>"
                        "🖥️ CHROME IS OPEN</div>"
                        "<div style='color:#88aacc;font-size:12px;margin-top:5px;'>"
                        "Sign in with Google in the browser.<br>"
                        "This page updates automatically.</div></div>",
                        unsafe_allow_html=True
                    )
                    with st.spinner("⏳ Waiting for Google sign-in..."):
                        for _ in range(3):
                            time.sleep(1)
                            if get_state()["status"] != "running":
                                break
                    st.rerun()

                # ── STATE: ERROR ────────────────────────
                elif ams["status"] == "error":
                    err = ams.get("error","Unknown error")
                    st.markdown(
                        f"<div style='background:#3d0000;border:1px solid #ff4444;"
                        f"border-radius:11px;padding:12px;margin:5px 0;'>"
                        f"<div style='color:#ff4444;font-family:Orbitron,monospace;font-size:10px;'>"
                        f"❌ ERROR</div>"
                        f"<div style='color:#ffaaaa;font-size:12px;margin-top:4px;'>{err}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    reset_state()
                    if st.button("🔄 Try Again", use_container_width=True, key="retry"):
                        st.rerun()

                # ── STATE: IDLE — Show the Google button ─
                else:
                    if not PW_OK:
                        st.markdown(
                            f"<div style='background:#1a0800;border:1px solid #ff8800;"
                            f"border-radius:11px;padding:14px;margin:6px 0;'>"
                            f"<div style='color:#ff8800;font-family:Orbitron,monospace;"
                            f"font-size:10px;margin-bottom:6px;'>⚠️ SETUP NEEDED</div>"
                            f"<div style='color:#ffcc88;font-size:12px;'>"
                            f"Run in CMD then restart:</div>"
                            f"<div style='background:#000;border-radius:6px;padding:8px;"
                            f"margin-top:6px;font-family:monospace;font-size:12px;color:#00ff88;'>"
                            f"pip install playwright beautifulsoup4<br>"
                            f"python -m playwright install chromium</div>"
                            f"<div style='color:#886644;font-size:11px;margin-top:5px;'>"
                            f"Error: {_AMS_ERR or 'playwright not installed'}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        # THE GOOGLE SIGN-IN BUTTON
                        # Styled to look like Google, but IS a real Streamlit button
                        st.markdown("""<style>
div[data-testid="stButton"]:has(button[kind="secondary"]) button {
    background: white !important;
    color: #3c4043 !important;
    border: 1px solid #dadce0 !important;
    font-family: 'Google Sans', Roboto, sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.25px !important;
}
div[data-testid="stButton"]:has(button[kind="secondary"]) button:hover {
    background: #f8f9fa !important;
    box-shadow: 0 1px 3px rgba(60,64,67,.3) !important;
}
</style>""", unsafe_allow_html=True)

                        clicked = st.button(
                            "🔵  Sign in with Google",
                            use_container_width=True,
                            key="gsign",
                            type="secondary"
                        )

                        st.markdown(
                            "<div style='background:#001a2e;border:1px solid #00d4ff22;"
                            "border-radius:9px;padding:9px;margin:7px 0;'>"
                            "<span style='color:#88aacc;font-size:11px;'>"
                            "🔐 Chrome opens — sign in with Google normally.<br>"
                            "Your password is <b style='color:#00ff88'>never</b> stored.</span>"
                            "</div>",
                            unsafe_allow_html=True
                        )

                        if clicked:
                            if not ev:
                                st.error("⚠️ Enter your institute email first!")
                            elif 'mitsgwl.ac.in' not in ev.lower() and 'mitsgwalior.in' not in ev.lower():
                                st.error("⚠️ Only works with MITS emails. Use Manual Entry for others.")
                            else:
                                ok = start_login(ev)
                                if ok:
                                    st.success("🖥️ Chrome opening — sign in with Google!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning("A login is already running, please wait.")

    # ══════════════════════════════════════════════════
    # STEP 1 — Attendance
    # ══════════════════════════════════════════════════
    elif st.session_state.step == 1:
        locked   = st.session_state.locked
        overall  = st.session_state.overall
        subjects = st.session_state.subjects
        st.markdown(prof_html(st.session_state.name, st.session_state.email,
                              st.session_state.institute, locked), unsafe_allow_html=True)

        if locked:
            # ── LOCKED AMS VIEW ───────────────────────
            st.markdown(
                "<div class='step-box'>"
                "<div class='step-title'>📅 YOUR ATTENDANCE</div>"
                "<div class='step-sub'>🔒 Fetched from MITS AMS — Cannot be changed</div>"
                "</div>",
                unsafe_allow_html=True
            )

            # Stat row
            tc = st.session_state.tc
            tl = st.session_state.tl
            ta = st.session_state.ta
            s1,s2,s3,s4 = st.columns(4)
            sc,_ = bv(overall)
            oc = "#00ff88" if overall>=75 else "#ffcc00" if overall>=50 else "#ff4444"
            with s1: st.markdown(f"<div class='stat-card'><h2>{tc}</h2><p>📚 Courses</p></div>", unsafe_allow_html=True)
            with s2: st.markdown(f"<div class='stat-card'><h2>{tl}</h2><p>📋 Total Classes</p></div>", unsafe_allow_html=True)
            with s3: st.markdown(f"<div class='stat-card'><h2>{ta}</h2><p>✅ Attended</p></div>", unsafe_allow_html=True)
            with s4: st.markdown(f"<div class='stat-card'><h2 style='color:{oc};'>{overall:.1f}%</h2><p>🎯 Overall 🔒</p></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Charts row
            if tl > 0 or subjects:
                ch1, ch2 = st.columns([1,2])
                with ch1:
                    st.markdown("<div style='color:#00d4ff;font-family:Orbitron,monospace;font-size:11px;margin-bottom:4px;'>🔵 OVERALL DISTRIBUTION</div>", unsafe_allow_html=True)
                    att_val   = ta if tl > 0 else sum(s["attended"] for s in subjects)
                    total_val = tl if tl > 0 else sum(s["held"] for s in subjects)
                    if total_val > 0:
                        st.plotly_chart(pie_chart(att_val, total_val, overall),
                                        use_container_width=True,
                                        config={"displayModeBar":False})
                with ch2:
                    if subjects:
                        st.markdown("<div style='color:#00d4ff;font-family:Orbitron,monospace;font-size:11px;margin-bottom:4px;'>📊 SUBJECT-WISE</div>", unsafe_allow_html=True)
                        fig = bar_chart(subjects)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True,
                                            config={"displayModeBar":False})

            # Radar chart
            if subjects and len(subjects) >= 3:
                st.markdown("<div style='color:#00d4ff;font-family:Orbitron,monospace;font-size:11px;margin-bottom:4px;'>🕸️ PERFORMANCE RADAR</div>", unsafe_allow_html=True)
                _, rc, _ = st.columns([1,2,1])
                with rc:
                    fig = radar_chart(subjects)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True,
                                        config={"displayModeBar":False})

            # Subject cards
            if subjects:
                st.markdown("<div style='font-family:Orbitron,monospace;color:#00d4ff;font-size:12px;margin:12px 0 7px;'>📚 MY COURSES</div>", unsafe_allow_html=True)
                for i in range(0, len(subjects), 3):
                    row = subjects[i:i+3]
                    cols = st.columns(len(row))
                    for ci, subj in enumerate(row):
                        sp = subj["pct"]
                        bc2,_ = bv(sp)
                        pc2 = pclass(sp)
                        ico = "✅" if sp>=75 else "⚠️" if sp>=50 else "🚫"
                        cls = f"{subj['attended']}/{subj['held']}" if subj.get("held",0)>0 else "—"
                        with cols[ci]:
                            st.markdown(
                                f"<div class='subj-card'>"
                                f"<div style='display:flex;justify-content:space-between;align-items:flex-start;'>"
                                f"<div><div class='subj-name'>{subj['name']}</div>"
                                f"<div class='subj-code'>{subj.get('code','')}</div></div>"
                                f"<div>{tbadge(subj.get('type',''))}</div></div>"
                                f"<div class='{pc2}' style='margin:7px 0;'>{ico} {sp:.1f}%</div>"
                                f"<div class='pb'><div class='{bc2}' style='width:{min(sp,100)}%;'></div></div>"
                                f"<div style='color:#88aacc;font-size:11px;margin-top:3px;'>📋 {cls}</div>"
                                + (f"<div class='subj-fac'>👨‍🏫 {subj['faculty']}</div>" if subj.get("faculty") else "")
                                + "</div>",
                                unsafe_allow_html=True
                            )

            # Enrollment
            enr = st.session_state.enr
            if enr:
                st.markdown(f"<div style='text-align:center;color:#446688;font-family:Orbitron,monospace;font-size:10px;margin-top:10px;'>ENROLLMENT: {enr}</div>", unsafe_allow_html=True)

            # Status
            if overall < 50:
                st.markdown("<div class='blocked-box' style='margin-top:10px;'>🚫 EXAM BLOCKED<br><div style='font-size:12px;color:#ffaa44;margin-top:4px;'>Below 50%</div></div>", unsafe_allow_html=True)
            elif overall < 75:
                st.markdown("<div class='wb' style='margin-top:8px;'><h4>⚠️ LOW ATTENDANCE</h4><p>50-75%. Can sit but at risk!</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='rb' style='margin-top:8px;'><h4>✅ GOOD ATTENDANCE</h4><p>Above 75%. Eligible!</p></div>", unsafe_allow_html=True)

            ca,cb = st.columns(2)
            with ca:
                if st.button("◀ BACK", use_container_width=True, key="b1"):
                    st.session_state.step=0; st.rerun()
            with cb:
                if overall < 50:
                    st.markdown("<div style='background:#3d0000;border:1px solid #ff4444;border-radius:9px;padding:10px;text-align:center;color:#ff4444;font-family:Orbitron,monospace;font-size:10px;'>🚫 CANNOT PROCEED</div>", unsafe_allow_html=True)
                else:
                    if st.button("NEXT → STUDY HOURS ▶", use_container_width=True, key="n1"):
                        st.session_state.step=2; st.rerun()

        else:
            # ── MANUAL SLIDER ─────────────────────────
            st.markdown(
                "<div class='step-box'>"
                "<div class='step-title'>📅 ATTENDANCE PERCENTAGE</div>"
                "<div class='step-sub'>How often do you attend class?</div></div>",
                unsafe_allow_html=True
            )
            _, col, _ = st.columns([1,2,1])
            with col:
                a = st.slider("", 0, 100, st.session_state.att,
                              label_visibility="collapsed", key="as")
                st.session_state.att = a
                bc2,cv = bv(a)
                st.markdown(
                    f"<div class='pb'><div class='{bc2}' style='width:{a}%;'></div></div>"
                    f"<div style='text-align:center;font-family:Orbitron,monospace;"
                    f"font-size:38px;color:{cv};margin:8px 0;'>{a}%</div>",
                    unsafe_allow_html=True
                )
                if a<50:   st.markdown("<div class='blocked-box'>🚫 EXAM BLOCKED<br><div style='font-size:12px;color:#ffaa44;'>Below 50%!</div></div>", unsafe_allow_html=True)
                elif a<75: st.markdown("<div class='wb'><h4>⚠️ LOW</h4><p>At risk!</p></div>", unsafe_allow_html=True)
                else:       st.markdown("<div class='rb'><h4>✅ GOOD</h4><p>Eligible!</p></div>", unsafe_allow_html=True)
                ca,cb = st.columns(2)
                with ca:
                    if st.button("◀ BACK", use_container_width=True, key="b1m"): st.session_state.step=0; st.rerun()
                with cb:
                    if st.button("NEXT → STUDY HOURS ▶", use_container_width=True, key="n1m"):
                        if a<50: st.error("🚫 Below 50%!")
                        else: st.session_state.step=2; st.rerun()

    # ══════════════════════════════════════════════════
    # STEP 2 — Study Hours
    # ══════════════════════════════════════════════════
    elif st.session_state.step == 2:
        locked = st.session_state.locked
        st.markdown(prof_html(st.session_state.name, st.session_state.email,
                              st.session_state.institute, locked), unsafe_allow_html=True)
        st.markdown("<div class='step-box'><div class='step-title'>📚 STUDY HOURS / WEEK</div><div class='step-sub'>How many hours do you study per week?</div></div>", unsafe_allow_html=True)
        _, col, _ = st.columns([1,2,1])
        with col:
            h = st.slider("", 0, 20, st.session_state.hrs, label_visibility="collapsed", key="hs")
            st.session_state.hrs = h
            bc2,cv = ("pg","#00ff88") if h>=8 else ("py","#ffcc00") if h>=4 else ("pr","#ff4444")
            st.markdown(
                f"<div class='pb'><div class='{bc2}' style='width:{min(h*5,100)}%;'></div></div>"
                f"<div style='text-align:center;font-family:Orbitron,monospace;font-size:38px;color:{cv};margin:8px 0;'>{h} hrs/wk</div>",
                unsafe_allow_html=True
            )
            if h<3:   st.markdown("<div class='ab'><h4>⚠️ VERY LOW</h4><p>Less than 3 hrs — very risky!</p></div>", unsafe_allow_html=True)
            elif h<6: st.markdown("<div class='wb'><h4>⚡ MODERATE</h4><p>Try to study more!</p></div>", unsafe_allow_html=True)
            else:      st.markdown("<div class='rb'><h4>✅ EXCELLENT</h4><p>More than 6 hrs/week!</p></div>", unsafe_allow_html=True)
            ca,cb = st.columns(2)
            with ca:
                if st.button("◀ BACK", use_container_width=True, key="b2"): st.session_state.step=1; st.rerun()
            with cb:
                if st.button("🚀 GET AI PREDICTION", use_container_width=True, key="n2"): st.session_state.step=3; st.rerun()

    # ══════════════════════════════════════════════════
    # STEP 3 — Result
    # ══════════════════════════════════════════════════
    elif st.session_state.step == 3:
        locked = st.session_state.locked
        name = st.session_state.name; email = st.session_state.email
        inst = st.session_state.institute
        att  = st.session_state.att;  hrs  = st.session_state.hrs
        st.markdown(prof_html(name, email, inst, locked), unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        bc2,_ = bv(att)
        with c1: st.markdown(f"<div class='stat-card'><h2>{att:.1f}%</h2><p>📅 Att {'🔒' if locked else ''}</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='stat-card'><h2>{hrs}</h2><p>📚 Hrs/Wk</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='stat-card'><h2>{'✅' if att>=75 else '⚠️'}</h2><p>Eligible</p></div>", unsafe_allow_html=True)
        st.markdown("---")

        if st.session_state.result is None:
            with st.spinner("🤖 AI analysing..."):
                time.sleep(2)
            pred = MODEL.predict(np.array([[att, hrs, 60]]))[0]
            st.session_state.result = pred
            db_save(name, email, inst, st.session_state.roll, att, hrs, pred)
            st.rerun()

        res = st.session_state.result
        if res == "Pass":
            st.markdown(f"<div class='pass-box'>✅ PREDICTION: PASS!<br><div style='font-size:13px;margin-top:7px;'>{name} is likely to PASS! 🎉</div></div>", unsafe_allow_html=True)
            st.balloons()
            st.markdown("<div class='rb' style='margin-top:12px;'><h4>📧 TIPS</h4><p>✅ Maintain attendance ✅ Keep studying ✅ Practice past papers</p></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='fail-box'>❌ PREDICTION: FAIL!<br><div style='font-size:13px;margin-top:7px;'>{name} is at HIGH RISK!</div></div>", unsafe_allow_html=True)
            st.markdown("<div class='ab' style='margin-top:12px;'><h4>🔔 ACTION NEEDED</h4><p>❗ Increase attendance to 75%+ ❗ Study 6+ hrs/week ❗ Seek tutoring</p></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, col, _ = st.columns([1,2,1])
        with col:
            if st.button("🔄 PREDICT ANOTHER", use_container_width=True):
                reset_state()
                for k,v in DEF.items(): st.session_state[k]=v
                st.rerun()

# ══════════════════════════════════════════════════════════════
# OTHER PAGES
# ══════════════════════════════════════════════════════════════
elif NAV == "🏆 Rankings":
    st.markdown("<p class='sec'>🏆 RANKINGS</p>", unsafe_allow_html=True)
    df = db_all()
    if len(df)==0: st.info("No students yet!")
    else:
        df['sc'] = df['attendance']*0.6 + df['study_hours']*4
        df = df.sort_values('sc',ascending=False).reset_index(drop=True)
        for i, row in df.iterrows():
            m  = "🥇🥈🥉".split("")[min(i,2)] if i < 3 else f"#{i+1}"
            m  = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
            c  = ["#ffd700","#c0c0c0","#cd7f32"][i] if i < 3 else "#00d4ff"
            rc = "#00ff88" if row.result=="Pass" else "#ff4444"
            bc2,_ = bv(row.attendance)
            inst = row.get('institute','')
            is_m = "MITS" in str(inst)
            st.markdown(
                f"<div class='gc' style='border-color:{c}44;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                f"<div><span style='font-size:20px;'>{m}</span>"
                f"<span style='color:{c};font-family:Orbitron,monospace;font-size:14px;margin-left:8px;'>{row['name']}</span>"
                f"<div style='margin-left:30px;margin-top:2px;'>"
                f"<span class='inst-badge {'mits-b' if is_m else 'other-b'}'>{'🎓' if is_m else '🏫'} {inst}</span></div></div>"
                f"<span style='color:{rc};font-family:Orbitron,monospace;'>{row.result}</span></div>"
                f"<div class='pb' style='margin-top:7px;'><div class='{bc2}' style='width:{min(row.attendance,100):.0f}%;'></div></div>"
                f"<div style='color:#88aacc;font-size:11px;margin-top:2px;'>"
                f"📅 {row.attendance:.1f}% | 📚 {row.study_hours} hrs/wk | 🎯 {row.sc:.0f}</div></div>",
                unsafe_allow_html=True
            )

elif NAV == "⚠️ At Risk":
    st.markdown("<p class='sec'>⚠️ AT RISK STUDENTS</p>", unsafe_allow_html=True)
    df = db_all()
    if len(df)==0: st.info("No data!")
    else:
        ar = df[(df.result=='Fail')|(df.attendance<75)|(df.study_hours<4)]
        if len(ar)==0: st.success("🎉 No at-risk students!")
        else:
            for _,r in ar.iterrows():
                reasons=[]
                if r.attendance<50: reasons.append("🚫 BLOCKED")
                elif r.attendance<75: reasons.append("📅 Low attendance")
                if r.study_hours<4: reasons.append("📚 Low study hours")
                if r.result=='Fail': reasons.append("❌ Predicted FAIL")
                st.markdown(f"<div class='ab'><h4>🔔 {r['name']} — {r.get('institute','')}</h4><p>📧 {r.get('email','')}<br>{'  |  '.join(reasons)}</p></div>", unsafe_allow_html=True)

elif NAV == "📅 Attendance Tracker":
    st.markdown("<p class='sec'>📅 TRACKER</p>", unsafe_allow_html=True)
    df = db_all()
    if len(df)==0: st.info("No students!")
    else:
        g=len(df[df.attendance>=75]); l=len(df[(df.attendance>=50)&(df.attendance<75)]); b=len(df[df.attendance<50])
        c1,c2,c3=st.columns(3)
        with c1: st.markdown(f"<div class='stat-card'><h2 style='color:#00ff88;'>{g}</h2><p>✅ Good</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='stat-card'><h2 style='color:#ffcc00;'>{l}</h2><p>⚠️ Low</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='stat-card'><h2 style='color:#ff4444;'>{b}</h2><p>🚫 Blocked</p></div>", unsafe_allow_html=True)
        for _,r in df.sort_values('attendance',ascending=False).iterrows():
            bc2,_ = bv(r.attendance)
            st.markdown(f"<div class='gc' style='padding:11px;'><div style='display:flex;justify-content:space-between;'><span style='color:white;'>{r['name']}</span><span style='color:#88aacc;font-size:12px;'>{r.attendance:.1f}%</span></div><div class='pb'><div class='{bc2}' style='width:{min(r.attendance,100):.0f}%;'></div></div></div>", unsafe_allow_html=True)

elif NAV == "📊 Dashboard":
    st.markdown("<p class='sec'>📊 DASHBOARD</p>", unsafe_allow_html=True)
    df = db_all()
    if len(df)==0: st.info("No data!")
    else:
        t=len(df); p=len(df[df.result=='Pass']); f=len(df[df.result=='Fail'])
        pr=round((p/t)*100); aa=round(df.attendance.mean(),1)
        for col,val,lbl in zip(st.columns(5),[t,p,f,f"{pr}%",f"{aa}%"],["Total","✅ Passed","❌ Failed","Pass Rate","Avg Att."]):
            with col: st.markdown(f"<div class='stat-card'><h2>{val}</h2><p>{lbl}</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        c1,c2=st.columns(2)
        with c1: st.markdown("### Pass vs Fail"); st.bar_chart(df.result.value_counts())
        with c2: st.markdown("### Attendance"); st.bar_chart(df.set_index('name')['attendance'])

elif NAV == "🗄️ Database":
    st.markdown("<p class='sec'>🗄️ DATABASE</p>", unsafe_allow_html=True)
    df = db_all()
    if len(df)==0: st.info("Empty!")
    else: st.dataframe(df, use_container_width=True)

elif NAV == "ℹ️ About":
    st.markdown("<p class='sec'>ℹ️ ABOUT</p>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("<div class='gc'><h3>🎯 PURPOSE</h3><p>Identify at-risk students early.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='gc'><h3>🤖 TECH</h3><p>Python • Streamlit • Random Forest • Playwright • Plotly • SQLite</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='gc'><h3>🔒 AMS LOGIN</h3><p>Chrome opens → student signs in with Google → data auto-fetched. Password never stored.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='gc'><h3>📊 PREDICTION</h3><p>AI uses Attendance + Study Hours. Below 50% = blocked from exam.</p></div>", unsafe_allow_html=True)

st.markdown(
    "<div class='footer'><h3>🎓 STUDENT PERFORMANCE PREDICTION SYSTEM</h3>"
    "<p>Developed by <span style='color:#00d4ff;font-size:15px;font-weight:bold;'>Vaibhav Singh Saroniya</span></p>"
    "<p>📧 <a href='mailto:vaibhavsaroniya@gmail.com'>vaibhavsaroniya@gmail.com</a> | 🎓 MITS Gwalior</p>"
    "<p style='font-size:10px;color:#446688;margin-top:5px;'>Python • Streamlit • Random Forest • Playwright • Plotly</p></div>",
    unsafe_allow_html=True
)
