import streamlit as st
import pickle
import numpy as np
import sqlite3
import pandas as pd
import time
import re

st.set_page_config(
    page_title="Student Performance Prediction System",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');
    * { font-family: 'Rajdhani', sans-serif; }
    .main { background-color: #020818; }
    .block-container { padding-top: 1rem; }

    .hero {
        background: linear-gradient(135deg, #020818 0%, #0a1628 50%, #020818 100%);
        border: 1px solid #00d4ff44; padding: 50px 40px;
        border-radius: 24px; text-align: center; margin-bottom: 30px;
    }
    .hero h1 { font-family:'Orbitron',monospace; font-size:38px; color:#00d4ff;
        text-shadow:0 0 30px #00d4ff88; margin:0; letter-spacing:2px; }
    .hero p { font-size:17px; color:#88aacc; margin-top:10px; }

    .step-box {
        background: linear-gradient(135deg, #0a1628, #0f2040);
        border: 2px solid #00d4ff55; border-radius: 20px;
        padding: 40px; text-align: center;
        max-width: 620px; margin: 0 auto;
        animation: fadeIn 0.5s ease;
    }
    @keyframes fadeIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}

    .step-title { font-family:'Orbitron',monospace; color:#00d4ff; font-size:20px; margin-bottom:8px; }
    .step-sub { color:#88aacc; font-size:15px; margin-bottom:20px; }

    .dot-wrap { display:flex; justify-content:center; align-items:center; gap:8px; margin-bottom:20px; }
    .dot { width:12px; height:12px; border-radius:50%; background:#0a1628; border:2px solid #00d4ff33; display:inline-block; }
    .dot.active { background:#00d4ff; box-shadow:0 0 10px #00d4ff; border-color:#00d4ff; }
    .dot.done { background:#00ff88; border-color:#00ff88; }
    .dot-line { width:30px; height:2px; background:#00d4ff22; }
    .dot-line.done { background:#00ff88; }

    .institute-badge {
        padding: 10px 20px; border-radius: 30px; display: inline-block;
        font-family:'Orbitron',monospace; font-size:13px; margin: 10px 0;
    }
    .mits-badge { background:#001a3d; border:1px solid #00d4ff; color:#00d4ff; }
    .other-badge { background:#1a1a00; border:1px solid #ffcc00; color:#ffcc00; }

    .pass-box { background:linear-gradient(135deg,#003d1f,#006633); border:2px solid #00ff88;
        padding:30px; border-radius:16px; text-align:center;
        font-family:'Orbitron',monospace; font-size:24px; color:#00ff88;
        text-shadow:0 0 20px #00ff8888; animation:glowG 2s ease-in-out infinite; }
    @keyframes glowG{0%,100%{box-shadow:0 0 20px #00ff8844}50%{box-shadow:0 0 40px #00ff8888}}

    .fail-box { background:linear-gradient(135deg,#3d0000,#660000); border:2px solid #ff4444;
        padding:30px; border-radius:16px; text-align:center;
        font-family:'Orbitron',monospace; font-size:24px; color:#ff4444;
        text-shadow:0 0 20px #ff444488; animation:glowR 2s ease-in-out infinite; }
    @keyframes glowR{0%,100%{box-shadow:0 0 20px #ff444444}50%{box-shadow:0 0 40px #ff444488}}

    .blocked-box { background:linear-gradient(135deg,#3d1a00,#2a1000); border:2px solid #ff8800;
        border-radius:16px; padding:20px; text-align:center;
        font-family:'Orbitron',monospace; color:#ff8800; font-size:18px; }

    .glass-card { background:linear-gradient(135deg,#0a1628aa,#0f2040aa);
        border:1px solid #00d4ff33; border-radius:16px; padding:20px; margin:8px 0; }
    .glass-card h3 { color:#00d4ff; font-family:'Orbitron',monospace; font-size:13px; }
    .glass-card p { color:#88aacc; font-size:14px; }

    .stat-card { background:linear-gradient(135deg,#0a1628,#0f2040);
        border:1px solid #00d4ff55; border-radius:16px; padding:20px; text-align:center; }
    .stat-card h2 { font-family:'Orbitron',monospace; color:#00d4ff; font-size:34px; margin:0; }
    .stat-card p { color:#88aacc; font-size:14px; margin:5px 0 0 0; }

    .alert-box { background:linear-gradient(135deg,#3d0000,#1a0000);
        border:1px solid #ff4444; border-left:5px solid #ff4444;
        border-radius:12px; padding:15px; margin:10px 0; }
    .alert-box h4 { color:#ff4444; margin:0 0 6px 0; font-family:'Orbitron',monospace; font-size:12px; }
    .alert-box p { color:#ffaaaa; margin:0; font-size:13px; }

    .rec-box { background:linear-gradient(135deg,#001a3d,#002a5e);
        border:1px solid #00d4ff44; border-left:5px solid #00d4ff;
        border-radius:12px; padding:15px; margin:10px 0; }
    .rec-box h4 { color:#00d4ff; margin:0 0 6px 0; font-family:'Orbitron',monospace; font-size:12px; }
    .rec-box p { color:#88ccff; margin:0; font-size:13px; }

    .warn-box { background:linear-gradient(135deg,#2a1a00,#1a1000);
        border:1px solid #ffcc00; border-left:5px solid #ffcc00;
        border-radius:12px; padding:15px; margin:10px 0; }
    .warn-box h4 { color:#ffcc00; margin:0 0 6px 0; font-family:'Orbitron',monospace; font-size:12px; }
    .warn-box p { color:#ffeeaa; margin:0; font-size:13px; }

    .pb-bg { background:#0a1628; border-radius:10px; height:14px; border:1px solid #00d4ff22; margin:8px 0; }
    .pg { height:14px; border-radius:10px; background:linear-gradient(90deg,#00ff88,#00cc66); box-shadow:0 0 10px #00ff8866; }
    .py { height:14px; border-radius:10px; background:linear-gradient(90deg,#ffcc00,#ff9900); box-shadow:0 0 10px #ffcc0066; }
    .pr { height:14px; border-radius:10px; background:linear-gradient(90deg,#ff4444,#cc0000); box-shadow:0 0 10px #ff444466; }

    .section-title { font-family:'Orbitron',monospace; font-size:26px; color:#00d4ff;
        text-align:center; text-shadow:0 0 20px #00d4ff66; margin:20px 0; letter-spacing:2px; }

    .profile-card {
        background:linear-gradient(135deg,#0a1628,#0f2040);
        border:1px solid #00d4ff44; border-radius:16px; padding:20px;
        text-align:center; margin-bottom:20px;
    }
    .profile-name { font-family:'Orbitron',monospace; color:#00d4ff; font-size:20px; }
    .profile-email { color:#88aacc; font-size:14px; margin-top:5px; }
    .profile-institute { margin-top:8px; }

    .footer { background:linear-gradient(135deg,#0a1628,#020818);
        border-top:1px solid #00d4ff33; padding:35px; text-align:center;
        margin-top:40px; border-radius:16px; }
    .footer h3 { font-family:'Orbitron',monospace; color:#00d4ff; font-size:17px; }
    .footer p { color:#88aacc; font-size:14px; }
    .footer a { color:#00d4ff; text-decoration:none; }

    section[data-testid="stSidebar"] { background:linear-gradient(180deg,#020818,#0a1628); border-right:1px solid #00d4ff22; }

    .stButton>button { background:linear-gradient(135deg,#00d4ff22,#0066ff22)!important;
        border:1px solid #00d4ff!important; color:#00d4ff!important;
        font-family:'Orbitron',monospace!important; font-size:12px!important;
        border-radius:10px!important; padding:12px!important; transition:all 0.3s!important; letter-spacing:1px!important; }
    .stButton>button:hover { background:linear-gradient(135deg,#00d4ff44,#0066ff44)!important; box-shadow:0 0 20px #00d4ff44!important; }

    .stTextInput>div>div>input { background:#0a1628!important; border:1px solid #00d4ff44!important;
        color:white!important; border-radius:10px!important; font-size:16px!important; }
    hr { border-color:#00d4ff22!important; }
    </style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────
defaults = {'step':0,'name':'','email':'','institute':'','roll':'','attendance':75,'study_hours':5,'result':None}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── DATABASE ──────────────────────────────────────────────
DB = r"C:\JAVA\StudentPredictor\students.db"

def create_db():
    conn = sqlite3.connect(DB)
    conn.execute('''CREATE TABLE IF NOT EXISTS predictions
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT, email TEXT, institute TEXT, roll TEXT,
         attendance INTEGER, study_hours INTEGER, result TEXT)''')
    conn.commit(); conn.close()

def save_pred(name, email, institute, roll, att, hrs, result):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO predictions (name,email,institute,roll,attendance,study_hours,result) VALUES (?,?,?,?,?,?,?)",
                 (name, email, institute, roll, att, hrs, result))
    conn.commit(); conn.close()

def get_all():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    conn.close(); return df

create_db()
model = pickle.load(open(r"C:\JAVA\StudentPredictor\model.pkl","rb"))

# ── EMAIL PARSER ──────────────────────────────────────────
def parse_email(email):
    email = email.strip().lower()
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None, None, None

    # MITS Gwalior pattern: 24ai10va73@mitsgwl.ac.in
    mits_match = re.match(r'^(\d{2})([a-z]+)(\d+)([a-z]+)(\d+)@mitsgwl\.ac\.in$', email)
    if mits_match:
        year = "20" + mits_match.group(1)
        return "MITS Gwalior", f"MITS'{mits_match.group(1)}", email

    # Other known institutes
    domain = email.split('@')[1]
    institute_map = {
        'iitd.ac.in': 'IIT Delhi',
        'iitb.ac.in': 'IIT Bombay',
        'iitk.ac.in': 'IIT Kanpur',
        'bits-pilani.ac.in': 'BITS Pilani',
        'vitap.ac.in': 'VIT AP',
        'vit.ac.in': 'VIT Vellore',
        'manipal.edu': 'Manipal University',
        'gmail.com': 'Personal (Gmail)',
        'outlook.com': 'Personal (Outlook)',
        'yahoo.com': 'Personal (Yahoo)',
    }
    for d, name in institute_map.items():
        if d in domain:
            return name, domain, email

    # Generic — extract domain name as institute
    inst_name = domain.split('.')[0].upper()
    return inst_name, domain, email
# ── SIMPLE ADMIN LOGIN SYSTEM ─────────────────────────────
ADMIN_PASSWORD = "admin123"

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
# Fixed Navigation Panel
st.sidebar.markdown("<div style='text-align:center;padding:15px 0;'><div style='font-family:Orbitron,monospace;font-size:13px;color:#00d4ff;'>🎓 SPPS</div><div style='color:#88aacc;font-size:11px;'>Navigation Panel</div></div>", unsafe_allow_html=True)

nav = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home & Predict",
        "🏆 Rankings",
        "⚠️ At Risk Students",
        "📅 Attendance Tracker",
        "📊 Dashboard",
        "🗄️ Database",
        "ℹ️ About"
    ]
)
st.sidebar.markdown("---")
df_s = get_all()
p_s = len(df_s[df_s['result']=='Pass']) if len(df_s)>0 else 0
f_s = len(df_s[df_s['result']=='Fail']) if len(df_s)>0 else 0
st.sidebar.markdown(f"""
<div class='glass-card' style='margin:5px;'>
    <div style='color:#00d4ff;font-family:Orbitron,monospace;font-size:11px;'>LIVE STATS</div>
    <div style='color:white;font-size:20px;margin-top:5px;'>{len(df_s)} Students</div>
    <div style='color:#00ff88;'>✅ {p_s} Passed</div>
    <div style='color:#ff4444;'>❌ {f_s} Failed</div>
</div>""", unsafe_allow_html=True)

if st.sidebar.button("🔄 New Prediction"):
    for k,v in defaults.items():
        st.session_state[k] = v
    st.rerun()

# ══════════════════════════════════════════════════════════
# HOME & PREDICT
# ══════════════════════════════════════════════════════════
if nav == "🏠 Home & Predict":

    st.markdown("<div class='hero'><h1>🎓 STUDENT PERFORMANCE<br>PREDICTION SYSTEM</h1><p>AI Powered • Random Forest Model • 95% Accuracy • Multi-Institute Support</p></div>", unsafe_allow_html=True)

    # Progress dots
    def d(i):
        if i < st.session_state.step: return "done"
        if i == st.session_state.step: return "active"
        return ""
    def dl(i):
        return "done" if i < st.session_state.step else ""

    labels = ["Name & Email","Attendance","Study Hours","Result"]
    st.markdown(f"""
    <div class='dot-wrap'>
        <div class='dot {d(0)}'></div><div class='dot-line {dl(0)}'></div>
        <div class='dot {d(1)}'></div><div class='dot-line {dl(1)}'></div>
        <div class='dot {d(2)}'></div><div class='dot-line {dl(2)}'></div>
        <div class='dot {d(3)}'></div>
    </div>
    <div style='text-align:center;color:#88aacc;font-size:13px;margin-bottom:20px;'>
        📍 {labels[min(st.session_state.step,3)]} &nbsp;|&nbsp; Step {st.session_state.step+1} of 4
    </div>""", unsafe_allow_html=True)

    # ── STEP 0 — NAME + EMAIL ─────────────────────────────
    if st.session_state.step == 0:
        st.markdown("<div class='step-box'><div class='step-title'>📝 STUDENT REGISTRATION</div><div class='step-sub'>Enter your name and institute email to begin</div></div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            name_in = st.text_input("👤 Full Name", placeholder="e.g. Vaibhav Singh Saroniya", key="name_in")
            email_in = st.text_input("📧 Institute Email", placeholder="e.g. 24ai10va73@mitsgwl.ac.in", key="email_in")

            # Live email preview
            if email_in:
                inst, roll, cleaned = parse_email(email_in)
                if inst:
                    is_mits = "MITS" in inst
                    badge_class = "mits-badge" if is_mits else "other-badge"
                    icon = "🎓" if is_mits else "🏫"
                    st.markdown(f"<div style='text-align:center;margin:10px 0;'><span class='institute-badge {badge_class}'>{icon} {inst}</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='text-align:center;color:#ff4444;font-size:13px;'>⚠️ Invalid email format</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("NEXT → ATTENDANCE ▶", use_container_width=True):
                if not name_in.strip():
                    st.error("⚠️ Please enter your full name!")
                elif not email_in.strip():
                    st.error("⚠️ Please enter your institute email!")
                else:
                    inst, roll, cleaned = parse_email(email_in)
                    if not inst:
                        st.error("⚠️ Please enter a valid email address!")
                    else:
                        st.session_state.name = name_in.strip()
                        st.session_state.email = cleaned
                        st.session_state.institute = inst
                        st.session_state.roll = roll or ""
                        st.session_state.step = 1
                        st.rerun()

    # ── STEP 1 — ATTENDANCE ───────────────────────────────
    elif st.session_state.step == 1:
        # Profile strip
        is_mits = "MITS" in st.session_state.institute
        badge = "mits-badge" if is_mits else "other-badge"
        icon  = "🎓" if is_mits else "🏫"
        st.markdown(f"""
        <div class='profile-card'>
            <div class='profile-name'>{st.session_state.name}</div>
            <div class='profile-email'>📧 {st.session_state.email}</div>
            <div class='profile-institute'><span class='institute-badge {badge}'>{icon} {st.session_state.institute}</span></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='step-box'><div class='step-title'>📅 ATTENDANCE PERCENTAGE</div><div class='step-sub'>How often do you attend class?</div></div>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            att = st.slider("", 0, 100, st.session_state.attendance, label_visibility="collapsed", key="att_s")
            st.session_state.attendance = att
            bc = "pg" if att>=75 else "py" if att>=50 else "pr"
            ac = "#00ff88" if att>=75 else "#ffcc00" if att>=50 else "#ff4444"
            st.markdown(f"<div class='pb-bg'><div class='{bc}' style='width:{att}%;'></div></div><div style='text-align:center;font-family:Orbitron,monospace;font-size:36px;color:{ac};margin:10px 0;'>{att}%</div>", unsafe_allow_html=True)

            if att < 50:
                st.markdown("<div class='blocked-box'>🚫 EXAM BLOCKED!<br><div style='font-size:14px;margin-top:8px;color:#ffaa44;'>Below 50% attendance — Not eligible to sit in exam!<br>Minimum 50% required.</div></div>", unsafe_allow_html=True)
            elif att < 75:
                st.markdown("<div class='warn-box'><h4>⚠️ LOW ATTENDANCE WARNING</h4><p>Between 50-75%. You can sit in exam but are at high risk!<br>Recommended: Attend more classes to reach 75%+</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='rec-box'><h4>✅ GOOD ATTENDANCE</h4><p>Above 75%. You are eligible for exam. Keep it up!</p></div>", unsafe_allow_html=True)

            ca,cb = st.columns(2)
            with ca:
                if st.button("◀ BACK", use_container_width=True):
                    st.session_state.step=0; st.rerun()
            with cb:
                if st.button("NEXT → STUDY HOURS ▶", use_container_width=True):
                    if att < 50:
                        st.error("🚫 Cannot proceed! Attendance below 50%!")
                    else:
                        st.session_state.step=2; st.rerun()

    # ── STEP 2 — STUDY HOURS ─────────────────────────────
    elif st.session_state.step == 2:
        is_mits = "MITS" in st.session_state.institute
        badge = "mits-badge" if is_mits else "other-badge"
        icon  = "🎓" if is_mits else "🏫"
        st.markdown(f"""
        <div class='profile-card'>
            <div class='profile-name'>{st.session_state.name}</div>
            <div class='profile-email'>📧 {st.session_state.email}</div>
            <div class='profile-institute'><span class='institute-badge {badge}'>{icon} {st.session_state.institute}</span></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div class='step-box'><div class='step-title'>📚 STUDY HOURS PER WEEK</div><div class='step-sub'>How many hours do you study every week?</div></div>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            hrs = st.slider("", 0, 20, st.session_state.study_hours, label_visibility="collapsed", key="hrs_s")
            st.session_state.study_hours = hrs
            bc = "pg" if hrs>=8 else "py" if hrs>=4 else "pr"
            hc = "#00ff88" if hrs>=8 else "#ffcc00" if hrs>=4 else "#ff4444"
            st.markdown(f"<div class='pb-bg'><div class='{bc}' style='width:{min(hrs*5,100)}%;'></div></div><div style='text-align:center;font-family:Orbitron,monospace;font-size:36px;color:{hc};margin:10px 0;'>{hrs} hrs/week</div>", unsafe_allow_html=True)

            if hrs < 3:
                st.markdown("<div class='alert-box'><h4>⚠️ VERY LOW STUDY HOURS</h4><p>Less than 3 hrs/week is very risky. Please study more!</p></div>", unsafe_allow_html=True)
            elif hrs < 6:
                st.markdown("<div class='warn-box'><h4>⚡ MODERATE STUDY HOURS</h4><p>3-6 hrs/week. Increasing this will improve your result!</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='rec-box'><h4>✅ EXCELLENT STUDY HOURS</h4><p>More than 6 hrs/week! You're putting in great effort!</p></div>", unsafe_allow_html=True)

            ca,cb = st.columns(2)
            with ca:
                if st.button("◀ BACK", use_container_width=True):
                    st.session_state.step=1; st.rerun()
            with cb:
                if st.button("🚀 GET AI PREDICTION", use_container_width=True):
                    st.session_state.step=3; st.rerun()

    # ── STEP 3 — RESULT ──────────────────────────────────
    elif st.session_state.step == 3:
        name = st.session_state.name
        email= st.session_state.email
        inst = st.session_state.institute
        att  = st.session_state.attendance
        hrs  = st.session_state.study_hours
        is_mits = "MITS" in inst
        badge = "mits-badge" if is_mits else "other-badge"
        icon  = "🎓" if is_mits else "🏫"

        # Profile card
        st.markdown(f"""
        <div class='profile-card'>
            <div class='profile-name'>{name}</div>
            <div class='profile-email'>📧 {email}</div>
            <div class='profile-institute'><span class='institute-badge {badge}'>{icon} {inst}</span></div>
        </div>""", unsafe_allow_html=True)

        # Stats
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f"<div class='stat-card'><h2>{att}%</h2><p>📅 Attendance</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='stat-card'><h2>{hrs}</h2><p>📚 Hrs/Week</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='stat-card'><h2>{'✅' if att>=75 else '⚠️'}</h2><p>Exam Eligible</p></div>", unsafe_allow_html=True)

        st.markdown("---")

        if st.session_state.result is None:
            with st.spinner("🤖 AI is analyzing your data..."):
                time.sleep(2)
            pred = model.predict(np.array([[att, hrs, 60]]))[0]
            st.session_state.result = pred
            save_pred(name, email, inst, st.session_state.roll, att, hrs, pred)
            st.rerun()

        result = st.session_state.result

        if result == "Pass":
            st.markdown(f"<div class='pass-box'>✅ PREDICTION: PASS!<br><div style='font-size:15px;margin-top:10px;'>{name} from {inst} is likely to PASS! 🎉</div></div>", unsafe_allow_html=True)
            st.balloons()
            st.markdown("""<div class='rec-box' style='margin-top:20px;'>
                <h4>📧 RECOMMENDATIONS</h4>
                <p>
                ✅ Maintain your good attendance<br>
                ✅ Continue your current study schedule<br>
                ✅ Focus on weak subjects for even better results<br>
                ✅ Participate actively in class discussions<br>
                ✅ Practice past exam papers to boost confidence
                </p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='fail-box'>❌ PREDICTION: FAIL!<br><div style='font-size:15px;margin-top:10px;'>{name} is at HIGH RISK of failing!</div></div>", unsafe_allow_html=True)
            st.markdown("""<div class='alert-box' style='margin-top:20px;'>
                <h4>🔔 URGENT ACTION REQUIRED</h4>
                <p>
                ❗ Increase attendance to above 75% immediately<br>
                ❗ Increase study hours to minimum 6 per week<br>
                ❗ Attend extra tutoring or doubt-clearing sessions<br>
                ❗ Inform your teacher or mentor about your situation<br>
                ❗ Create a proper weekly study timetable<br>
                ❗ Avoid distractions and focus on core subjects
                </p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns([1,2,1])
        with c2:
            if st.button("🔄 PREDICT ANOTHER STUDENT", use_container_width=True):
                for k,v in defaults.items():
                    st.session_state[k] = v
                st.rerun()

# ══════════════════════════════════════════════════════════
# RANKINGS
# ══════════════════════════════════════════════════════════
elif nav == "🏆 Rankings":
    st.markdown("<p class='section-title'>🏆 STUDENT RANKINGS</p>", unsafe_allow_html=True)
    df = get_all()
    if len(df)==0: st.info("No students yet! Make some predictions first.")
    else:
        df['score'] = df['attendance']*0.6 + df['study_hours']*4
        df = df.sort_values('score', ascending=False).reset_index(drop=True)
        for i, row in df.iterrows():
            m  = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"#{i+1}"
            c  = "#ffd700" if i==0 else "#c0c0c0" if i==1 else "#cd7f32" if i==2 else "#00d4ff"
            rc = "#00ff88" if row['result']=="Pass" else "#ff4444"
            bc = "pg" if row['attendance']>=75 else "py" if row['attendance']>=50 else "pr"
            inst = row.get('institute','') or ''
            is_m = "MITS" in inst
            badge = f"<span class='institute-badge {'mits-badge' if is_m else 'other-badge'}'>{'🎓' if is_m else '🏫'} {inst}</span>" if inst else ""
            st.markdown(f"""
            <div class='glass-card' style='border-color:{c}44;'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <span style='font-size:24px;'>{m}</span>
                        <span style='color:{c};font-family:Orbitron,monospace;font-size:17px;margin-left:12px;'>{row['name']}</span>
                        <div style='margin-left:38px;margin-top:4px;'>{badge}</div>
                    </div>
                    <span style='color:{rc};font-family:Orbitron,monospace;font-size:16px;'>{row['result']}</span>
                </div>
                <div class='pb-bg' style='margin-top:12px;'><div class='{bc}' style='width:{row["attendance"]}%;'></div></div>
                <div style='color:#88aacc;font-size:13px;margin-top:5px;'>
                    📅 {row['attendance']}% &nbsp;|&nbsp; 📚 {row['study_hours']} hrs/week &nbsp;|&nbsp; 🎯 Score: {row['score']:.0f}
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# AT RISK
# ══════════════════════════════════════════════════════════
elif nav == "⚠️ At Risk Students":
    st.markdown("<p class='section-title'>⚠️ AT RISK STUDENTS</p>", unsafe_allow_html=True)
    df = get_all()
    if len(df)==0: st.info("No data yet!")
    else:
        ar = df[(df['result']=='Fail')|(df['attendance']<75)|(df['study_hours']<4)]
        if len(ar)==0:
            st.success("🎉 No at-risk students! Everyone is performing well!")
        else:
            st.markdown(f"<div style='text-align:center;color:#ff4444;font-size:18px;margin-bottom:20px;'>⚠️ {len(ar)} students need immediate attention!</div>", unsafe_allow_html=True)
            for _, row in ar.iterrows():
                reasons=[]
                if row['attendance']<50: reasons.append("🚫 BLOCKED FROM EXAM — below 50% attendance")
                elif row['attendance']<75: reasons.append("📅 Low attendance (below 75%)")
                if row['study_hours']<4: reasons.append("📚 Very low study hours (below 4 hrs/week)")
                if row['result']=='Fail': reasons.append("❌ AI predicts FAIL")
                inst = row.get('institute','') or 'Unknown'
                email= row.get('email','') or ''
                st.markdown(f"""
                <div class='alert-box'>
                    <h4>🔔 {row['name']} — {inst}</h4>
                    <p>📧 {email}<br>{'<br>'.join(reasons)}</p>
                    <p style='margin-top:8px;color:#ffcc88;'>📧 Action: Contact student • Inform parents • Arrange extra classes</p>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ATTENDANCE TRACKER
# ══════════════════════════════════════════════════════════
elif nav == "📅 Attendance Tracker":
    st.markdown("<p class='section-title'>📅 ATTENDANCE TRACKER</p>", unsafe_allow_html=True)
    df = get_all()
    if len(df)==0: st.info("No students yet!")
    else:
        g = len(df[df['attendance']>=75])
        l = len(df[(df['attendance']>=50)&(df['attendance']<75)])
        b = len(df[df['attendance']<50])
        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(f"<div class='stat-card'><h2 style='color:#00ff88;'>{g}</h2><p>✅ Good (75%+)</p></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='stat-card'><h2 style='color:#ffcc00;'>{l}</h2><p>⚠️ Low (50-75%)</p></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='stat-card'><h2 style='color:#ff4444;'>{b}</h2><p>🚫 Blocked (&lt;50%)</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        for _, row in df.sort_values('attendance', ascending=False).iterrows():
            bc = "pg" if row['attendance']>=75 else "py" if row['attendance']>=50 else "pr"
            s  = "✅ Eligible" if row['attendance']>=75 else "⚠️ At Risk" if row['attendance']>=50 else "🚫 BLOCKED"
            inst = row.get('institute','') or ''
            st.markdown(f"""
            <div class='glass-card' style='padding:15px;'>
                <div style='display:flex;justify-content:space-between;'>
                    <div>
                        <span style='color:white;font-size:16px;'>{row['name']}</span>
                        <span style='color:#88aacc;font-size:13px;margin-left:10px;'>{inst}</span>
                    </div>
                    <span style='color:#88aacc;'>{s}</span>
                </div>
                <div class='pb-bg'><div class='{bc}' style='width:{row["attendance"]}%;'></div></div>
                <div style='color:#88aacc;font-size:12px;margin-top:3px;'>{row["attendance"]}% attendance</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════
elif nav == "📊 Dashboard":
    st.markdown("<p class='section-title'>📊 ANALYTICS DASHBOARD</p>", unsafe_allow_html=True)
    df = get_all()
    if len(df)==0: st.info("No data yet!")
    else:
        t=len(df); p=len(df[df['result']=='Pass']); f=len(df[df['result']=='Fail'])
        pr=round((p/t)*100); aa=round(df['attendance'].mean())
        c1,c2,c3,c4,c5 = st.columns(5)
        for col,val,lbl in zip([c1,c2,c3,c4,c5],[t,p,f,f"{pr}%",f"{aa}%"],["Total","✅ Passed","❌ Failed","Pass Rate","Avg Att."]):
            with col: st.markdown(f"<div class='stat-card'><h2>{val}</h2><p>{lbl}</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("### Pass vs Fail")
            st.bar_chart(df['result'].value_counts())
        with c2:
            st.markdown("### Attendance per Student")
            st.bar_chart(df.set_index('name')['attendance'])
        st.markdown("### Study Hours per Student")
        st.line_chart(df.set_index('name')['study_hours'])

# ══════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════
elif nav == "🗄️ Database":
    st.markdown("<p class='section-title'>🗄️ STUDENT DATABASE</p>", unsafe_allow_html=True)
    df = get_all()
    if len(df)==0: st.info("Database is empty! Make predictions first.")
    else:
        st.markdown(f"<div style='text-align:center;color:#88aacc;margin-bottom:20px;'>Total records: <span style='color:#00d4ff;'>{len(df)}</span></div>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("### ✅ Passed Students")
            pf=df[df['result']=='Pass']; st.success(f"Total: {len(pf)}")
            if len(pf)>0: st.dataframe(pf, use_container_width=True)
        with c2:
            st.markdown("### ❌ Failed Students")
            ff=df[df['result']=='Fail']; st.error(f"Total: {len(ff)}")
            if len(ff)>0: st.dataframe(ff, use_container_width=True)

# ══════════════════════════════════════════════════════════
# ABOUT
# ══════════════════════════════════════════════════════════
elif nav == "ℹ️ About":
    st.markdown("<p class='section-title'>ℹ️ ABOUT THIS SYSTEM</p>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='glass-card'><h3>🎯 PURPOSE</h3><p>This system helps teachers identify at-risk students early so they can provide help and support before exams.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'><h3>🤖 TECHNOLOGY USED</h3><p>• Python Programming<br>• Random Forest ML Model<br>• Streamlit Web Framework<br>• SQLite Database<br>• Pandas & NumPy Libraries</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='glass-card'><h3>📊 HOW PREDICTION WORKS</h3><p>The AI model analyzes:<br><br>1. 📅 <b>Attendance %</b> — Class attendance<br>2. 📚 <b>Study Hours/Week</b><br><br>Students below 50% attendance are automatically blocked from exam eligibility.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'><h3>🏫 INSTITUTE SUPPORT</h3><p>Supports MITS Gwalior email format (mitsgwl.ac.in) and all other institute/personal emails. MITS students are identified automatically from their roll number format.</p></div>", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────
st.markdown("""
<div class='footer'>
    <h3>🎓 STUDENT PERFORMANCE PREDICTION SYSTEM</h3>
    <p>Developed by <span style='color:#00d4ff;font-size:18px;font-weight:bold;'>Vaibhav Singh Saroniya</span></p>
    <p>📧 <a href='mailto:vaibhavsaroniya@gmail.com'>vaibhavsaroniya@gmail.com</a> &nbsp;|&nbsp; 🎓 MITS Gwalior</p>
    <p style='margin-top:10px;font-size:12px;color:#446688;'>Powered by Python • Streamlit • Random Forest AI • SQLite</p>
</div>
""", unsafe_allow_html=True)
