# -*- coding: utf-8 -*-

import base64
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, FancyArrowPatch, Polygon, Rectangle
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="MechanismQuest",
    page_icon="âš™ï¸",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
LOGO_B64 = base64.b64encode((APP_DIR / "assets" / "jcu_logo.png").read_bytes()).decode("ascii")

COLORS = {
    "known": "#2563eb",      # blue
    "relative": "#8b5cf6",   # purple
    "tangent": "#f97316",    # orange
    "normal": "#dc2626",     # red
    "resultant": "#16a34a",  # green
    "link": "#334155",       # slate
    "guide": "#94a3b8",      # light slate
    "construct": "#64748b",  # construction lines
    "note": "#0f766e",       # explanatory notes and constraints
    "angle": "#a16207",      # angle markers and angular dimensions
    "dimension": "#7c3f00",  # length and radius dimensions
    "support": "#475569",    # fixed supports and ground
}

# Matplotlib can otherwise inherit a dark desktop/notebook style.  Fix every
# diagram to the same high-contrast light palette used by the Streamlit UI.
plt.rcParams.update({
    "figure.facecolor": "#ffffff",
    "figure.edgecolor": "#ffffff",
    "axes.facecolor": "#ffffff",
    "axes.edgecolor": "#64748b",
    "axes.labelcolor": "#0f172a",
    "axes.titlecolor": "#0f172a",
    "text.color": "#0f172a",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
    "savefig.facecolor": "#ffffff",
    "savefig.edgecolor": "#ffffff",
    "font.family": "DejaVu Sans",
})

st.markdown(
    """
    <style>
    /* Force one accessible light theme on every browser/OS. */
    :root { color-scheme: light; }
    html, body, [data-testid="stAppViewContainer"], .stApp {
      background: #ffffff !important;
      color: #0f172a !important;
    }
    .stApp { background: #ffffff !important; }
    .block-container { max-width: 1460px; padding-top: 1.05rem; padding-bottom: 2rem; }
    header[data-testid="stHeader"] { background: rgba(255,255,255,.96) !important; }
    #MainMenu, footer { visibility: hidden; }

    /* Main-page and sidebar typography: never inherit a computer's dark theme. */
    [data-testid="stMainBlockContainer"],
    [data-testid="stMainBlockContainer"] p,
    [data-testid="stMainBlockContainer"] li,
    [data-testid="stMainBlockContainer"] label,
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3,
    [data-testid="stMainBlockContainer"] h4,
    [data-testid="stMainBlockContainer"] h5,
    [data-testid="stMainBlockContainer"] h6,
    [data-testid="stMarkdownContainer"] {
      color: #0f172a !important;
    }
    [data-testid="stSidebar"] {
      background: #eef1f5 !important;
      border-right: 1px solid #cbd5e1;
      color: #0f172a !important;
    }
    [data-testid="stSidebar"] .block-container { padding-top: 2.8rem; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
      color: #0f172a !important;
    }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
    .stCaption, small { color: #475569 !important; }
    a { color: #075985 !important; }
    hr { border-color: #cbd5e1 !important; }

    /* Header and instructional panels. */
    .app-header { display:grid; grid-template-columns:230px 1fr 190px; gap:24px; align-items:center; padding:16px 10px 20px; }
    .app-header-logo { display:flex; justify-content:center; }
    .app-header-logo img { width:210px; max-height:92px; object-fit:contain; }
    .app-header-title h1 { margin:0; font-size:34px; line-height:1.05; color:#0f172a !important; }
    .app-header-title p { margin:7px 0 0; color:#334155 !important; line-height:1.45; font-size:15px; }
    .app-header-author { text-align:right; color:#334155 !important; font-size:13px; line-height:1.5; }
    .app-divider { height:1px; background:#cbd5e1; margin:2px 0 18px; }
    .info { background:#e8f2ff !important; border:1px solid #bfdbfe; border-radius:10px; padding:13px 15px; color:#0c4a6e !important; margin:8px 0 16px; }
    .hint { background:#ecfdf3 !important; border:1px solid #86efac; border-radius:10px; padding:11px 13px; color:#14532d !important; margin:8px 0 14px; }
    .warning { background:#fff8e8 !important; border:1px solid #f3c969; border-radius:10px; padding:11px 13px; color:#713f12 !important; margin:8px 0 14px; }
    .card { border:1px solid #cbd5e1; border-radius:10px; padding:14px 16px; margin-bottom:14px; background:#ffffff !important; color:#0f172a !important; }
    .good { background:#ecfdf3 !important; border:1px solid #86efac; color:#14532d !important; border-radius:9px; padding:10px 12px; margin:6px 0; }
    .bad { background:#fff1f2 !important; border:1px solid #fda4af; color:#881337 !important; border-radius:9px; padding:10px 12px; margin:6px 0; }
    .info *, .hint *, .warning *, .card *, .good *, .bad * { color:inherit !important; }
    .mini { color:#475569 !important; font-size:13px; }
    .skill { color:#475569 !important; font-size:13px; margin-top:10px; }
    .legend-row { display:flex; flex-wrap:wrap; gap:14px; color:#0f172a !important; font-size:13px; margin-top:4px; }
    .legend-chip { display:inline-flex; align-items:center; gap:7px; color:#0f172a !important; }
    .legend-box { width:18px; height:4px; border-radius:2px; display:inline-block; }

    /* Inputs, dropdowns and radio choices. */
    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label { color:#0f172a !important; font-weight:600; }
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
      background:#ffffff !important;
      color:#0f172a !important;
      -webkit-text-fill-color:#0f172a !important;
      caret-color:#0f172a !important;
      border-color:#94a3b8 !important;
    }
    [data-baseweb="select"] > div {
      background:#ffffff !important;
      border-color:#94a3b8 !important;
      color:#0f172a !important;
    }
    [data-baseweb="select"] span,
    [data-baseweb="select"] input,
    [data-baseweb="select"] svg { color:#0f172a !important; fill:#0f172a !important; -webkit-text-fill-color:#0f172a !important; }
    [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
      background:#ffffff !important;
      color:#0f172a !important;
    }
    [role="option"] { background:#ffffff !important; color:#0f172a !important; }
    [role="option"]:hover, [role="option"][aria-selected="true"] { background:#e0f2fe !important; color:#0c4a6e !important; }
    div[data-testid="stRadio"] p,
    div[data-testid="stRadio"] span {
      color:#0f172a !important;
      font-family:"DejaVu Sans","Segoe UI Symbol","Noto Sans Symbols 2",sans-serif !important;
      line-height:1.45 !important;
    }

    /* Tabs and buttons. */
    [data-baseweb="tab-list"] { background:#f1f5f9 !important; border-radius:8px 8px 0 0; }
    [data-baseweb="tab"] { color:#334155 !important; background:transparent !important; }
    [data-baseweb="tab"] p { color:#334155 !important; font-weight:600; }
    [data-baseweb="tab"][aria-selected="true"] { background:#ffffff !important; color:#075985 !important; }
    [data-baseweb="tab"][aria-selected="true"] p { color:#075985 !important; }
    .stButton > button, .stDownloadButton > button {
      background:#075985 !important;
      color:#ffffff !important;
      border:1px solid #075985 !important;
      font-weight:700;
    }
    .stButton > button *, .stDownloadButton > button * { color:#ffffff !important; }
    .stButton > button:hover, .stDownloadButton > button:hover {
      background:#0c4a6e !important;
      border-color:#0c4a6e !important;
    }
    .stButton > button:disabled { background:#cbd5e1 !important; color:#475569 !important; border-color:#cbd5e1 !important; }

    /* Built-in messages, formula blocks and expanders. */
    [data-testid="stAlert"] { background:#f8fafc !important; color:#0f172a !important; border:1px solid #cbd5e1 !important; }
    [data-testid="stAlert"] p, [data-testid="stAlert"] div { color:#0f172a !important; }
    [data-testid="stExpander"] { background:#ffffff !important; border-color:#cbd5e1 !important; }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] p { color:#0f172a !important; }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color:#0f172a !important; }
    .katex, .katex * { color:#0f172a !important; }
    code { background:#f1f5f9 !important; color:#7f1d1d !important; }

    /* Visible keyboard focus, independent of browser defaults. */
    button:focus-visible, input:focus-visible, textarea:focus-visible,
    [data-baseweb="select"] > div:focus-within, [role="radio"]:focus-visible {
      outline:3px solid #38bdf8 !important;
      outline-offset:2px !important;
      box-shadow:none !important;
    }

    @media (max-width:980px) {
      .app-header { grid-template-columns:1fr; text-align:center; }
      .app-header-author { text-align:center; }
      .app-header-logo img { width:190px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_header():
    st.markdown(
        f"""
        <div class="app-header">
          <div class="app-header-logo">
            <img src="data:image/png;base64,{LOGO_B64}" alt="JCU">
          </div>
          <div class="app-header-title">
            <h1>MechanismQuest</h1>
            <p>Interactive rigid-body velocity and acceleration analysis practice for EG1011 Statics and Dynamics.</p>
          </div>
          <div class="app-header-author">
            Designed for EG1011<br>
            <b>Dr. Mehdi Khatamifar</b><br>
            James Cook University
          </div>
        </div>
        <div class="app-divider"></div>
        """,
        unsafe_allow_html=True,
    )


PROBLEMS = [
    {
        "id": "V1",
        "topic": "Velocity analysis",
        "level": 1,
        "title": "Fixed-axis rotation at a rim point",
        "difficulty": "Foundation",
        "diagram": "fixed_velocity",
        "description": (
            "A disk rotates about a fixed axis. A point P on the rim is located at "
            "r = 0.30 m. At the instant shown, the disk has angular velocity "
            "Ï‰ = 6 rad/s counterclockwise. Determine the speed of point P."
        ),
        "givens": ["r = 0.30 m", "Ï‰ = 6 rad/s CCW"],
        "direction_questions": [
            {
                "q": "What is the direction of the velocity of point P?",
                "options": [
                    "Toward the centre of the disk",
                    "Radially outward from the centre",
                    "Tangent to the circular path",
                    "Along the radius OP",
                ],
                "correct": "Tangent to the circular path",
                "why": "For fixed-axis rotation, point velocity is always tangent to the path."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct speed relationship.",
                "options": [
                    "v = Î±r",
                    "v = Ï‰r",
                    "v = Ï‰Â²r",
                    "v = r/Ï‰",
                ],
                "correct": "v = Ï‰r",
                "why": "For fixed-axis rotation, the linear speed equals Ï‰r."
            }
        ],
        "solve_outputs": [
            {"label": "Speed of point P", "key": "vP", "value": 1.8, "tol": 0.02, "unit": "m/s"},
        ],
        "solution_lines": [
            r"v_P=\omega r=(6)(0.30)=1.80\ \text{m/s}",
        ],
        "teaching_point": "At a fixed axis, velocity is tangent to the path and its magnitude increases with radius.",
    },
    {
        "id": "V2",
        "topic": "Velocity analysis",
        "level": 2,
        "title": "Relative velocity with a vertical slider",
        "difficulty": "Easy",
        "diagram": "slider_velocity",
        "description": (
            "Link AB has length 0.50 m and is inclined 30Â° above the horizontal. "
            "Point A moves horizontally to the right at 2.0 m/s. Point B is constrained "
            "to move vertically. Determine the angular velocity of the link and the "
            "velocity of B."
        ),
        "givens": ["AB = 0.50 m", "Î¸ = 30Â°", "v_A = 2.0 m/s right", "B is a vertical slider"],
        "direction_questions": [
            {
                "q": "What is the direction of the relative velocity v_B/A?",
                "options": [
                    "Along link AB",
                    "Perpendicular to link AB",
                    "Horizontal only",
                    "Vertical only",
                ],
                "correct": "Perpendicular to link AB",
                "why": "Relative velocity due to rotation is perpendicular to the link."
            },
            {
                "q": "What is the allowed direction of velocity of point B?",
                "options": [
                    "Horizontal only",
                    "Vertical only",
                    "Along AB",
                    "Any direction",
                ],
                "correct": "Vertical only",
                "why": "A slider moves only along its guide."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct vector equation.",
                "options": [
                    "v_B = v_A + Î± Ã— r_B/A",
                    "v_B = v_A + Ï‰ Ã— r_B/A",
                    "v_B = a_A + Ï‰ Ã— r_B/A",
                    "v_B = Ï‰r_B/A",
                ],
                "correct": "v_B = v_A + Ï‰ Ã— r_B/A",
                "why": "Relative velocity for a rigid body is v_B = v_A + Ï‰ Ã— r_B/A."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity Ï‰_AB (CCW positive)", "key": "omegaAB", "value": 8.0, "tol": 0.05, "unit": "rad/s"},
            {"label": "Velocity of B (upward positive)", "key": "vB", "value": 3.4641, "tol": 0.03, "unit": "m/s"},
        ],
        "vector_lines": [
            r"\mathbf r_{B/A}=0.50(\cos30^\circ\,\mathbf i+\sin30^\circ\,\mathbf j)=(0.433\,\mathbf i+0.250\,\mathbf j)\ \text{m}",
            r"\omega_{AB}\mathbf k\times\mathbf r_{B/A}=\omega_{AB}\mathbf k\times(0.433\mathbf i+0.250\mathbf j)=(-0.250\omega_{AB})\mathbf i+(0.433\omega_{AB})\mathbf j",
        ],
        "solution_lines": [
            r"\mathbf r_{B/A}=0.50(\cos30^\circ\,\mathbf i+\sin30^\circ\,\mathbf j)=(0.433\,\mathbf i+0.250\,\mathbf j)\ \text{m}",
            r"\mathbf v_B=\mathbf v_A+\omega_{AB}\mathbf k\times\mathbf r_{B/A}",
            r"\mathbf v_B=(2\,\mathbf i)+( -0.25\omega_{AB}\,\mathbf i+0.433\omega_{AB}\,\mathbf j )",
            r"v_{Bx}=0\Rightarrow 2-0.25\omega_{AB}=0 \Rightarrow \omega_{AB}=8.00\ \text{rad/s}",
            r"v_{By}=0.433(8.00)=3.46\ \text{m/s upward}",
        ],
        "teaching_point": "First mark the slider constraint, then use the x- or y-component equation to find the angular velocity.",
    },
    {
        "id": "V3",
        "topic": "Velocity analysis",
        "level": 3,
        "title": "Two-link mechanism with an inclined groove",
        "difficulty": "Moderate",
        "diagram": "linked_velocity",
        "source_note": "Adapted from Hibbeler, Engineering Mechanics: Dynamics, 14th ed., Problem 16-60.",
        "description": (
            "Link AB is horizontal and pinned at A. Link BC is vertical. Both links have "
            "length 2 m at the instant shown. Slider C moves at 8 m/s down a 45Â° groove. "
            "Determine the angular velocities of links AB and BC. Use counterclockwise as positive."
        ),
        "givens": ["AB = 2 m", "BC = 2 m", "v_C = 8 m/s down the 45Â° groove"],
        "direction_questions": [
            {
                "q": "What is the direction of velocity of point B from the rotation of AB?",
                "options": [
                    "Horizontal",
                    "Vertical",
                    "Along AB",
                    "Along BC",
                ],
                "correct": "Vertical",
                "why": "B moves perpendicular to AB, and AB is horizontal."
            },
            {
                "q": "What is the direction of the relative velocity v_C/B on link BC?",
                "options": [
                    "Along BC",
                    "Perpendicular to BC",
                    "Along the 45Â° groove",
                    "Horizontal only",
                ],
                "correct": "Perpendicular to BC",
                "why": "Relative velocity due to rotation is perpendicular to the link."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct vector equation for link BC.",
                "options": [
                    "v_C = v_B + Ï‰_BC Ã— r_C/B",
                    "a_C = a_B + Î±_BC Ã— r_C/B - Ï‰_BCÂ² r_C/B",
                    "v_C = Ï‰_BC r_C/B",
                    "v_B = v_C + Î±_BC Ã— r_C/B",
                ],
                "correct": "v_C = v_B + Ï‰_BC Ã— r_C/B",
                "why": "This is the relative-velocity equation for the moving link BC."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity Ï‰_AB (CCW positive)", "key": "omegaAB", "value": -2.8284, "tol": 0.03, "unit": "rad/s"},
            {"label": "Angular velocity Ï‰_BC (CCW positive)", "key": "omegaBC", "value": 2.8284, "tol": 0.03, "unit": "rad/s"},
        ],
        "vector_lines": [
            r"\mathbf v_C=8(\cos45^\circ\,\mathbf i-\sin45^\circ\,\mathbf j)=(5.657\,\mathbf i-5.657\,\mathbf j)\ \text{m/s}",
            r"\mathbf r_{C/B}=-2\mathbf j\ \text{m},\qquad \omega_{BC}\mathbf k\times\mathbf r_{C/B}=2\omega_{BC}\mathbf i",
        ],
        "solution_lines": [
            r"\mathbf v_C=8(\cos45^\circ\,\mathbf i-\sin45^\circ\,\mathbf j)=(5.657\,\mathbf i-5.657\,\mathbf j)\ \text{m/s}",
            r"\mathbf v_B=v_B\,\mathbf j",
            r"\mathbf r_{C/B}=(0\,\mathbf i-2\,\mathbf j)\ \text{m}",
            r"\mathbf v_C=\mathbf v_B+\omega_{BC}\mathbf k\times\mathbf r_{C/B}=\mathbf v_B+(2\omega_{BC}\,\mathbf i)",
            r"i:\ 5.657=2\omega_{BC}\Rightarrow \omega_{BC}=2.828\ \text{rad/s}",
            r"j:\ -5.657=v_B",
            r"Since v_B=2\omega_{AB}\text{ downward, }\omega_{AB}=-2.828\ \text{rad/s}",
        ],
        "teaching_point": "At a shared pin, the point has one physical velocity, but each link may have a different angular velocity.",
    },
    {
        "id": "V4",
        "topic": "Velocity analysis",
        "level": 4,
        "title": "Instantaneous centre for a slider-link mechanism",
        "difficulty": "Moderate",
        "diagram": "ic_velocity",
        "description": (
            "Bar AB has angular velocity Ï‰_AB = 6 rad/s counterclockwise and length AB = 0.200 m. "
            "Link BC has length 0.500 m, and point C is a horizontal slider. Determine the angular "
            "velocity of link BC and the velocity of slider C. Report positive angular velocity as CCW "
            "and positive slider velocity to the right."
        ),
        "givens": ["AB = 0.200 m", "BC = 0.500 m", "Ï‰_AB = 6 rad/s CCW", "C is a horizontal slider"],
        "direction_questions": [
            {
                "q": "Which method is most efficient when two velocity directions are known?",
                "options": [
                    "Use only fixed-axis rotation at every point",
                    "Use the instantaneous centre method",
                    "Use acceleration analysis directly",
                    "Use energy methods",
                ],
                "correct": "Use the instantaneous centre method",
                "why": "When two velocity directions are known, the IC method is often fastest."
            },
            {
                "q": "The line from a point to the instantaneous centre is:",
                "options": [
                    "Parallel to the velocity",
                    "Perpendicular to the velocity",
                    "Along the link only",
                    "Always horizontal",
                ],
                "correct": "Perpendicular to the velocity",
                "why": "For any point on the body, velocity is perpendicular to the radius from the IC."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct scalar relationship once the IC is known.",
                "options": [
                    "v = Î±r",
                    "v = Ï‰r",
                    "v = Ï‰Â²r",
                    "v = r/Ï‰",
                ],
                "correct": "v = Ï‰r",
                "why": "At that instant the rigid body behaves like rotation about the IC."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity magnitude of link BC", "key": "omegaBCmag", "value": 1.9596, "tol": 0.03, "unit": "rad/s"},
            {"label": "Velocity magnitude of slider C", "key": "vCmag", "value": 1.3384, "tol": 0.03, "unit": "m/s"},
        ],
        "vector_lines": [
            r"\mathbf r_{B/A}=0.200(\cos45^\circ\,\mathbf i+\sin45^\circ\,\mathbf j)=(0.1414\,\mathbf i+0.1414\,\mathbf j)\ \text{m}",
            r"\mathbf v_B=\omega_{AB}\mathbf k\times\mathbf r_{B/A}=6\mathbf k\times(0.1414\mathbf i+0.1414\mathbf j)=(-0.8485\,\mathbf i+0.8485\,\mathbf j)\ \text{m/s}",
            r"\mathbf r_{C/B}=0.500(\cos(-30^\circ)\,\mathbf i+\sin(-30^\circ)\,\mathbf j)=(0.433\,\mathbf i-0.250\,\mathbf j)\ \text{m}",
            r"\omega_{BC}\mathbf k\times\mathbf r_{C/B}=(0.250\omega_{BC})\mathbf i+(0.433\omega_{BC})\mathbf j",
            r"\mathbf v_C=u\mathbf i\qquad (\text{slider C has no }j\text{-component})",
        ],
        "solution_lines": [
            r"v_B=\omega_{AB}AB=(6)(0.200)=1.20\ \text{m/s}",
            r"\mathbf v_B \text{ is perpendicular to }AB,\quad \mathbf v_C\text{ is horizontal}",
            r"\text{Locate the IC by drawing lines perpendicular to }\mathbf v_B\text{ and }\mathbf v_C",
            r"\mathbf v_C=\mathbf v_B+\omega_{BC}\mathbf k\times\mathbf r_{C/B}",
            r"Using components gives \omega_{BC}=-1.960\ \text{rad/s (clockwise)}",
            r"v_C=-1.338\ \text{m/s (to the left)}",
        ],
        "teaching_point": "The instantaneous centre is mainly a velocity method. It helps you get directions and speed ratios quickly.",
    },
    {
        "id": "V5",
        "topic": "Velocity analysis",
        "level": 5,
        "title": "Open-belt no-slip velocity transfer",
        "difficulty": "Easy",
        "diagram": "belt_velocity",
        "description": (
            "Two pulleys are connected by an open belt with no slip. Pulley A has radius 0.200 m and "
            "rotates at Ï‰_A = 12 rad/s. Pulley B has radius 0.125 m. Determine the angular velocity of B."
        ),
        "givens": ["r_A = 0.200 m", "r_B = 0.125 m", "Ï‰_A = 12 rad/s", "Open belt, no slip"],
        "direction_questions": [
            {
                "q": "For an open belt, pulley B rotates:",
                "options": [
                    "In the same direction as A",
                    "In the opposite direction to A",
                    "With zero angular velocity",
                    "Only clockwise",
                ],
                "correct": "In the same direction as A",
                "why": "An open belt gives the same rotation direction at both pulleys."
            },
            {
                "q": "Under no-slip conditions, what is equal at the belt contact?",
                "options": [
                    "Angular velocities only",
                    "Tangential speeds only",
                    "Radii only",
                    "Moments of inertia only",
                ],
                "correct": "Tangential speeds only",
                "why": "No slip means equal tangential speed at the contact."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct no-slip velocity relation.",
                "options": [
                    "Ï‰_A = Ï‰_B",
                    "Ï‰_A / r_A = Ï‰_B / r_B",
                    "Ï‰_A r_A = Ï‰_B r_B",
                    "Ï‰_A r_B = Ï‰_B r_AÂ²",
                ],
                "correct": "Ï‰_A r_A = Ï‰_B r_B",
                "why": "Equal tangential speeds give Ï‰_A r_A = Ï‰_B r_B."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity Ï‰_B", "key": "omegaB", "value": 19.2, "tol": 0.05, "unit": "rad/s"},
        ],
        "solution_lines": [
            r"\omega_A r_A=\omega_B r_B",
            r"(12)(0.200)=\omega_B(0.125)",
            r"\omega_B=19.2\ \text{rad/s}",
        ],
        "teaching_point": "Same shaft means same angular velocity. No-slip contact means same tangential speed. These are not the same statement.",
    },
    {
        "id": "V6",
        "topic": "Velocity analysis",
        "level": 6,
        "title": "Compound gear train",
        "difficulty": "Moderate",
        "diagram": "gear_train",
        "description": (
            "Gear A has 20 teeth and drives gear B with 60 teeth. Gear B is fixed to the same shaft as gear C, "
            "which has 30 teeth. Gear C drives gear D with 90 teeth. If gear A rotates at 18 rad/s clockwise, "
            "determine the angular velocity magnitude of gear D."
        ),
        "givens": ["N_A = 20", "N_B = 60", "N_C = 30", "N_D = 90", "Ï‰_A = 18 rad/s clockwise"],
        "direction_questions": [
            {
                "q": "External meshing gears rotate in:",
                "options": [
                    "The same direction",
                    "Opposite directions",
                    "Zero direction",
                    "A random direction",
                ],
                "correct": "Opposite directions",
                "why": "External gear contact reverses the rotation direction."
            },
            {
                "q": "Two gears fixed on the same shaft have the same:",
                "options": [
                    "Tangential speed",
                    "Angular velocity",
                    "Number of teeth",
                    "Radius necessarily",
                ],
                "correct": "Angular velocity",
                "why": "If they are on the same shaft, they rotate together with the same Ï‰."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct gear-speed relationship for one external mesh.",
                "options": [
                    "Ï‰_1 N_1 = Ï‰_2 N_2",
                    "Ï‰_1 / N_1 = Ï‰_2 / N_2",
                    "Ï‰_1 N_2 = Ï‰_2 / N_1",
                    "Ï‰_1 = Ï‰_2 always",
                ],
                "correct": "Ï‰_1 N_1 = Ï‰_2 N_2",
                "why": "Equal tangential speeds at meshing pitch circles give Ï‰_1 r_1 = Ï‰_2 r_2. With proportional tooth counts, Ï‰_1 N_1 = Ï‰_2 N_2."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity magnitude of gear D", "key": "omegaD", "value": 2.0, "tol": 0.02, "unit": "rad/s"},
        ],
        "solution_lines": [
            r"\omega_B=\omega_A\frac{N_A}{N_B}=18\frac{20}{60}=6\ \text{rad/s}",
            r"\omega_C=\omega_B=6\ \text{rad/s}",
            r"\omega_D=\omega_C\frac{N_C}{N_D}=6\frac{30}{90}=2\ \text{rad/s}",
            r"\text{A is clockwise, B is counterclockwise, C is counterclockwise, so D is clockwise.}",
        ],
        "teaching_point": "Track the direction carefully: each external mesh reverses the direction, while a same-shaft pair keeps the direction.",
    },
    {
        "id": "A1",
        "topic": "Acceleration analysis",
        "level": 1,
        "title": "Fixed-axis acceleration components",
        "difficulty": "Foundation",
        "diagram": "fixed_acceleration",
        "description": (
            "A disk rotates about a fixed axis. At point P on the rim, r = 0.30 m, Ï‰ = 6 rad/s and "
            "Î± = 4 rad/sÂ² at the instant shown. Determine the tangential acceleration, normal acceleration, "
            "and resultant acceleration of point P."
        ),
        "givens": ["r = 0.30 m", "Ï‰ = 6 rad/s", "Î± = 4 rad/sÂ²"],
        "direction_questions": [
            {
                "q": "Tangential acceleration acts:",
                "options": [
                    "Toward the centre",
                    "Perpendicular to the radius / tangent to the path",
                    "Along the radius outward",
                    "Always vertically",
                ],
                "correct": "Perpendicular to the radius / tangent to the path",
                "why": "Tangential acceleration changes the speed."
            },
            {
                "q": "Normal acceleration acts:",
                "options": [
                    "Away from the centre",
                    "Toward the centre",
                    "Tangent to the path",
                    "Always horizontally",
                ],
                "correct": "Toward the centre",
                "why": "Normal acceleration changes direction and points inward."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct formulas.",
                "options": [
                    "a_t = Ï‰r and a_n = Î±r",
                    "a_t = Î±r and a_n = Ï‰Â²r",
                    "a_t = Ï‰Â²r and a_n = Î±r",
                    "a_t = v/r and a_n = Î±Â²r",
                ],
                "correct": "a_t = Î±r and a_n = Ï‰Â²r",
                "why": "Tangential acceleration depends on Î±, while normal acceleration depends on Ï‰Â²."
            }
        ],
        "solve_outputs": [
            {"label": "Tangential acceleration a_t", "key": "at", "value": 1.2, "tol": 0.02, "unit": "m/sÂ²"},
            {"label": "Normal acceleration a_n", "key": "an", "value": 10.8, "tol": 0.03, "unit": "m/sÂ²"},
            {"label": "Resultant acceleration |a|", "key": "ares", "value": 10.8665, "tol": 0.03, "unit": "m/sÂ²"},
        ],
        "solution_lines": [
            r"a_t=\alpha r=(4)(0.30)=1.20\ \text{m/s}^2",
            r"a_n=\omega^2 r=(6^2)(0.30)=10.8\ \text{m/s}^2",
            r"|a|=\sqrt{a_t^2+a_n^2}=\sqrt{1.20^2+10.8^2}=10.87\ \text{m/s}^2",
        ],
        "teaching_point": "Even if Î± were zero, the normal component could still exist because it depends on Ï‰Â².",
    },
    {
        "id": "A2",
        "topic": "Acceleration analysis",
        "level": 2,
        "title": "Relative acceleration with a vertical slider",
        "difficulty": "Moderate",
        "diagram": "slider_acceleration",
        "description": (
            "Link AB has length 0.50 m and is inclined 30Â° above the horizontal. Point A moves horizontally "
            "to the right at a constant speed of 1.0 m/s, so a_A = 0. Point B is constrained to move vertically. "
            "Complete the velocity step first, then determine the angular acceleration of the link and the acceleration of B. "
            "Use counterclockwise positive and upward positive."
        ),
        "givens": ["AB = 0.50 m", "Î¸ = 30Â°", "v_A = 1.0 m/s constant", "a_A = 0", "B is a vertical slider"],
        "direction_questions": [
            {
                "q": "The relative normal acceleration of B with respect to A points:",
                "options": [
                    "Away from A along AB",
                    "Toward A along AB",
                    "Perpendicular to AB",
                    "Always vertically",
                ],
                "correct": "Toward A along AB",
                "why": "The normal component always points from the moving point toward the base point."
            },
            {
                "q": "Before doing acceleration analysis, what must be found first?",
                "options": [
                    "The kinetic energy",
                    "The velocity analysis and angular velocity Ï‰",
                    "The moment of inertia",
                    "The work done by the link",
                ],
                "correct": "The velocity analysis and angular velocity Ï‰",
                "why": "The normal term uses Ï‰Â², so the velocity analysis must be done first."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-acceleration equation.",
                "options": [
                    "a_B = a_A + Î± Ã— r_B/A - Ï‰Â² r_B/A",
                    "a_B = v_A + Î± Ã— r_B/A - Ï‰Â² r_B/A",
                    "a_B = a_A + Ï‰ Ã— r_B/A",
                    "a_B = Î±r_B/A",
                ],
                "correct": "a_B = a_A + Î± Ã— r_B/A - Ï‰Â² r_B/A",
                "why": "For a rigid body in plane motion, acceleration has tangential and normal relative terms."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration Î±_AB (CCW positive)", "key": "alphaAB", "value": -27.7128, "tol": 0.05, "unit": "rad/sÂ²"},
            {"label": "Acceleration of B (upward positive)", "key": "aB", "value": -16.0, "tol": 0.05, "unit": "m/sÂ²"},
        ],
        "vector_lines": [
            r"\mathbf r_{B/A}=0.50(\cos30^\circ\,\mathbf i+\sin30^\circ\,\mathbf j)=(0.433\,\mathbf i+0.250\,\mathbf j)\ \text{m}",
            r"\alpha_{AB}\mathbf k\times\mathbf r_{B/A}=(-0.250\alpha_{AB})\mathbf i+(0.433\alpha_{AB})\mathbf j",
            r"-\omega_{AB}^2\mathbf r_{B/A}=-16(0.433\mathbf i+0.250\mathbf j)=(-6.928\mathbf i-4.000\mathbf j)",
        ],
        "solution_lines": [
            r"\text{From the velocity step: }\omega_{AB}=4.00\ \text{rad/s}",
            r"\mathbf r_{B/A}=(0.433\,\mathbf i+0.250\,\mathbf j)\ \text{m}",
            r"\mathbf a_B=\mathbf 0+\alpha_{AB}\mathbf k\times\mathbf r_{B/A}-\omega_{AB}^2\mathbf r_{B/A}",
            r"\mathbf a_B=(-0.25\alpha_{AB}-6.928)\mathbf i+(0.433\alpha_{AB}-4.000)\mathbf j",
            r"a_{Bx}=0\Rightarrow -0.25\alpha_{AB}-6.928=0 \Rightarrow \alpha_{AB}=-27.713\ \text{rad/s}^2",
            r"a_{By}=0.433(-27.713)-4=-16.0\ \text{m/s}^2",
        ],
        "teaching_point": "Acceleration analysis is not complete without the normal term. That is the most common omission.",
    },
    {
        "id": "A3",
        "topic": "Acceleration analysis",
        "level": 3,
        "title": "Twisted-belt acceleration transfer",
        "difficulty": "Moderate",
        "diagram": "belt_acceleration",
        "description": (
            "A twisted belt connects wheel A and pulley B without slip, so the pulleys rotate in opposite directions. "
            "Wheel A has radius 0.200 m and starts from rest with constant angular acceleration Î±_A = 3 rad/sÂ². "
            "Pulley B has radius 0.125 m. Determine Ï‰_B, Î±_B, and the tangential and normal acceleration components "
            "of a point P on the rim of B at t = 3 s."
        ),
        "givens": ["r_A = 0.200 m", "r_B = 0.125 m", "Î±_A = 3 rad/sÂ²", "Ï‰_A(0)=0", "t = 3 s", "Twisted belt, no slip"],
        "direction_questions": [
            {
                "q": "For a twisted belt, pulley B rotates:",
                "options": [
                    "In the same direction as A",
                    "In the opposite direction to A",
                    "With zero angular speed",
                    "Only counterclockwise",
                ],
                "correct": "In the opposite direction to A",
                "why": "A twisted/crossed belt reverses the direction of rotation."
            },
            {
                "q": "Which acceleration component transfers directly through the no-slip belt?",
                "options": [
                    "Normal acceleration",
                    "Tangential acceleration",
                    "Resultant acceleration only",
                    "Neither component",
                ],
                "correct": "Tangential acceleration",
                "why": "No slip transfers the tangential acceleration. The normal part is local to each pulley."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct no-slip tangential-acceleration relation.",
                "options": [
                    "Ï‰_AÂ²r_A = Ï‰_BÂ²r_B",
                    "Î±_A r_A = Î±_B r_B",
                    "Î±_A = Î±_B",
                    "a_nA = a_nB",
                ],
                "correct": "Î±_A r_A = Î±_B r_B",
                "why": "Tangential acceleration is the transferred quantity in a no-slip belt."
            }
        ],
        "solve_outputs": [
            {"label": "Angular speed magnitude of pulley B at t = 3 s", "key": "omegaB", "value": 14.4, "tol": 0.05, "unit": "rad/s"},
            {"label": "Angular acceleration magnitude of pulley B", "key": "alphaB", "value": 4.8, "tol": 0.03, "unit": "rad/sÂ²"},
            {"label": "Tangential acceleration of point P on B", "key": "at", "value": 0.6, "tol": 0.02, "unit": "m/sÂ²"},
            {"label": "Normal acceleration of point P on B", "key": "an", "value": 25.92, "tol": 0.05, "unit": "m/sÂ²"},
        ],
        "solution_lines": [
            r"\omega_A=\alpha_A t=(3)(3)=9\ \text{rad/s}",
            r"\omega_A r_A=\omega_B r_B \Rightarrow \omega_B=\frac{9(0.200)}{0.125}=14.4\ \text{rad/s}",
            r"\alpha_A r_A=\alpha_B r_B \Rightarrow \alpha_B=\frac{3(0.200)}{0.125}=4.8\ \text{rad/s}^2",
            r"a_t=\alpha_B r_B=(4.8)(0.125)=0.60\ \text{m/s}^2",
            r"a_n=\omega_B^2 r_B=(14.4^2)(0.125)=25.92\ \text{m/s}^2",
        ],
        "teaching_point": "No slip transfers tangential speed and tangential acceleration. Normal acceleration is computed separately on each pulley.",
    },
    {
        "id": "A4",
        "topic": "Acceleration analysis",
        "level": 4,
        "title": "Linked mechanism: velocity first, then acceleration",
        "difficulty": "Challenging",
        "diagram": "linked_acceleration",
        "description": (
            "Link AB is horizontal and link BC is vertical, with lengths AB = 2 m and BC = 2 m. "
            "From the velocity step, slider C is known to move down a 45Â° groove at 8 m/s, giving "
            "Ï‰_AB = -2.828 rad/s and Ï‰_BC = 2.828 rad/s at this instant. If slider C now has acceleration "
            "3.0 m/sÂ² down the same 45Â° groove, determine the angular accelerations Î±_AB and Î±_BC. "
            "Use counterclockwise as positive."
        ),
        "givens": ["AB = 2 m", "BC = 2 m", "Ï‰_AB = -2.828 rad/s", "Ï‰_BC = 2.828 rad/s", "a_C = 3 m/sÂ² down 45Â° groove"],
        "direction_questions": [
            {
                "q": "The relative normal acceleration of point C with respect to B on link BC points:",
                "options": [
                    "Toward B along BC",
                    "Away from B along BC",
                    "Perpendicular to BC",
                    "Along the groove",
                ],
                "correct": "Toward B along BC",
                "why": "Relative normal acceleration always points from the moving point toward the base point."
            },
            {
                "q": "Why is the velocity step needed before the acceleration step?",
                "options": [
                    "Because Î± depends on kinetic energy",
                    "Because the normal terms use the known angular velocities Ï‰",
                    "Because it makes the drawing prettier",
                    "Because only velocity gives the link lengths",
                ],
                "correct": "Because the normal terms use the known angular velocities Ï‰",
                "why": "The normal relative acceleration terms contain Ï‰Â²."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-acceleration equation for link BC.",
                "options": [
                    "a_C = a_B + Î±_BC Ã— r_C/B - Ï‰_BCÂ² r_C/B",
                    "a_C = v_B + Î±_BC Ã— r_C/B - Ï‰_BCÂ² r_C/B",
                    "a_C = a_B + Ï‰_BC Ã— r_C/B",
                    "a_C = Î±_BC r_C/B only",
                ],
                "correct": "a_C = a_B + Î±_BC Ã— r_C/B - Ï‰_BCÂ² r_C/B",
                "why": "You need both the tangential and normal relative terms."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration Î±_AB (CCW positive)", "key": "alphaAB", "value": -9.0607, "tol": 0.04, "unit": "rad/sÂ²"},
            {"label": "Angular acceleration Î±_BC (CCW positive)", "key": "alphaBC", "value": 9.0607, "tol": 0.04, "unit": "rad/sÂ²"},
        ],
        "vector_lines": [
            r"\mathbf a_C=3(\cos45^\circ\,\mathbf i-\sin45^\circ\,\mathbf j)=(2.121\,\mathbf i-2.121\,\mathbf j)\ \text{m/s}^2",
            r"\mathbf a_B=\alpha_{AB}\mathbf k\times(2\mathbf i)-\omega_{AB}^2(2\mathbf i)=(-16)\mathbf i+(2\alpha_{AB})\mathbf j",
            r"\mathbf r_{C/B}=-2\mathbf j\ \text{m}",
            r"\alpha_{BC}\mathbf k\times\mathbf r_{C/B}=2\alpha_{BC}\mathbf i,\qquad -\omega_{BC}^2\mathbf r_{C/B}=+16\mathbf j",
        ],
        "solution_lines": [
            r"\mathbf a_C=3(\cos45^\circ\,\mathbf i-\sin45^\circ\,\mathbf j)=(2.121\,\mathbf i-2.121\,\mathbf j)\ \text{m/s}^2",
            r"\mathbf a_B=\alpha_{AB}\mathbf k\times(2\mathbf i)-\omega_{AB}^2(2\mathbf i)=(-16)\mathbf i+(2\alpha_{AB})\mathbf j",
            r"\mathbf r_{C/B}=(0\mathbf i-2\mathbf j)\ \text{m}",
            r"\alpha_{BC}\mathbf k\times\mathbf r_{C/B}=(2\alpha_{BC})\mathbf i",
            r"-\omega_{BC}^2\mathbf r_{C/B}=(0\mathbf i+16\mathbf j)",
            r"\mathbf a_C=\mathbf a_B+(2\alpha_{BC})\mathbf i+16\mathbf j",
            r"i:\ 2.121=-16+2\alpha_{BC}\Rightarrow \alpha_{BC}=9.061\ \text{rad/s}^2",
            r"j:\ -2.121=2\alpha_{AB}+16\Rightarrow \alpha_{AB}=-9.061\ \text{rad/s}^2",
        ],
        "teaching_point": "The clean method is always the same: velocity first, identify constraints, then acceleration with tangential and normal components.",
    },

    {
        "id": "V7",
        "topic": "Velocity analysis",
        "level": 7,
        "title": "Two-link mechanism with instantaneous translation",
        "difficulty": "Moderate",
        "diagram": "two_link_translation",
        "source_note": "Adapted from Hibbeler, Engineering Mechanics: Dynamics, 14th ed., Problem 16-58.",
        "description": (
            "Link AB is horizontal, pinned at A, and has length 2 ft. Link BC is 3 ft long and is inclined "
            "30Â° above the horizontal. Slider C moves vertically downward at 4 ft/s. Determine the signed "
            "angular velocities of AB and BC, taking counterclockwise as positive."
        ),
        "givens": ["AB = 2 ft", "BC = 3 ft", "Î¸_BC = 30Â°", "v_C = 4 ft/s downward", "CCW is positive"],
        "direction_questions": [
            {
                "q": "What direction can point B move because AB is horizontal and pinned at A?",
                "options": ["Horizontal only", "Vertical only", "Along AB", "Any direction"],
                "correct": "Vertical only",
                "why": "The velocity of B is perpendicular to the fixed-axis link AB."
            },
            {
                "q": "What is the direction of the relative velocity v_C/B if link BC is rotating?",
                "options": ["Along BC", "Perpendicular to BC", "Vertical only", "Horizontal only"],
                "correct": "Perpendicular to BC",
                "why": "For two points on a rigid link, the relative velocity is perpendicular to the link."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct pair of velocity relations.",
                "options": [
                    "v_B = Ï‰_AB Ã— r_B/A and v_C = v_B + Ï‰_BC Ã— r_C/B",
                    "v_B = Î±_AB Ã— r_B/A and v_C = v_B + Î±_BC Ã— r_C/B",
                    "v_C = Ï‰_BCÂ² r_C/B only",
                    "v_B = v_C for every configuration"
                ],
                "correct": "v_B = Ï‰_AB Ã— r_B/A and v_C = v_B + Ï‰_BC Ã— r_C/B",
                "why": "AB rotates about fixed A, while BC undergoes general plane motion."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity Ï‰_AB (CCW positive)", "key": "omegaAB", "value": -2.0, "tol": 0.02, "unit": "rad/s"},
            {"label": "Angular velocity Ï‰_BC (CCW positive)", "key": "omegaBC", "value": 0.0, "tol": 0.02, "unit": "rad/s"}
        ],
        "vector_lines": [
            r"\mathbf r_{B/A}=2\mathbf i\ \text{ft},\qquad \mathbf v_B=\omega_{AB}\mathbf k\times(2\mathbf i)=2\omega_{AB}\mathbf j",
            r"\mathbf r_{C/B}=3(\cos30^\circ\,\mathbf i+\sin30^\circ\,\mathbf j)=(2.598\mathbf i+1.500\mathbf j)\ \text{ft}",
            r"\omega_{BC}\mathbf k\times\mathbf r_{C/B}=(-1.500\omega_{BC})\mathbf i+(2.598\omega_{BC})\mathbf j"
        ],
        "solution_lines": [
            r"-4\mathbf j=2\omega_{AB}\mathbf j+(-1.500\omega_{BC}\mathbf i+2.598\omega_{BC}\mathbf j)",
            r"i:\ 0=-1.500\omega_{BC}\Rightarrow\omega_{BC}=0",
            r"j:\ -4=2\omega_{AB}+2.598(0)\Rightarrow\omega_{AB}=-2.00\ \text{rad/s}",
            r"\omega_{AB}=2.00\ \text{rad/s clockwise};\quad \omega_{BC}=0\ \text{at this instant}"
        ],
        "teaching_point": "A link can have zero angular velocity at one instant while translating; zero instantaneous angular velocity does not mean the link is permanently stationary.",
    },
    {
        "id": "V8",
        "topic": "Velocity analysis",
        "level": 8,
        "title": "Instantaneous centre in a two-link slider mechanism",
        "difficulty": "Challenging",
        "diagram": "ic_two_link",
        "source_note": "Adapted from Hibbeler, Engineering Mechanics: Dynamics, 14th ed., Problem 16-82.",
        "description": (
            "Link AB is 5 in. long and is oriented 45Â° below the horizontal from fixed pin A. Link BC is 4 in. "
            "long and is oriented 30Â° above the horizontal. Slider C moves upward at 12 in./s. Determine the "
            "signed angular velocities of AB and BC, taking counterclockwise as positive."
        ),
        "givens": ["AB = 5 in.", "BC = 4 in.", "AB at âˆ’45Â°", "BC at +30Â°", "v_C = 12 in./s upward", "CCW is positive"],
        "direction_questions": [
            {
                "q": "The velocity of B is perpendicular to which line?",
                "options": ["The vertical slider guide", "Link AB", "Link BC", "The horizontal axis only"],
                "correct": "Link AB",
                "why": "B belongs to link AB, which rotates about fixed point A."
            },
            {
                "q": "To locate the instantaneous centre of BC, draw through B and C lines that are:",
                "options": ["Parallel to v_B and v_C", "Perpendicular to v_B and v_C", "Parallel to BC", "Always horizontal"],
                "correct": "Perpendicular to v_B and v_C",
                "why": "Each radius from the instantaneous centre is perpendicular to that point's velocity."
            }
        ],
        "equation_questions": [
            {
                "q": "Which equation remains valid whether or not the instantaneous centre is used?",
                "options": [
                    "v_C = v_B + Ï‰_BC Ã— r_C/B",
                    "v_C = Î±_BC Ã— r_C/B",
                    "v_C = Ï‰_AB Ã— r_C/B",
                    "v_B = v_C in every two-link mechanism"
                ],
                "correct": "v_C = v_B + Ï‰_BC Ã— r_C/B",
                "why": "The relative-velocity equation is the general compatibility relation for rigid link BC."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity Ï‰_AB (CCW positive)", "key": "omegaAB", "value": 1.2423, "tol": 0.02, "unit": "rad/s"},
            {"label": "Angular velocity Ï‰_BC (CCW positive)", "key": "omegaBC", "value": 2.1962, "tol": 0.02, "unit": "rad/s"}
        ],
        "vector_lines": [
            r"\mathbf r_{B/A}=5(\cos(-45^\circ)\mathbf i+\sin(-45^\circ)\mathbf j)=(3.536\mathbf i-3.536\mathbf j)\ \text{in.}",
            r"\mathbf v_B=\omega_{AB}\mathbf k\times\mathbf r_{B/A}=(3.536\omega_{AB})\mathbf i+(3.536\omega_{AB})\mathbf j",
            r"\mathbf r_{C/B}=4(\cos30^\circ\mathbf i+\sin30^\circ\mathbf j)=(3.464\mathbf i+2.000\mathbf j)\ \text{in.}"
        ],
        "solution_lines": [
            r"12\mathbf j=\mathbf v_B+\omega_{BC}\mathbf k\times\mathbf r_{C/B}",
            r"0=3.536\omega_{AB}-2.000\omega_{BC}",
            r"12=3.536\omega_{AB}+3.464\omega_{BC}",
            r"\omega_{AB}=1.242\ \text{rad/s},\qquad\omega_{BC}=2.196\ \text{rad/s}",
            r"\text{Both positive results are counterclockwise under the stated sign convention.}"
        ],
        "teaching_point": "The IC construction is a fast geometric check, but the relative-velocity equation is still the safest way to preserve signs.",
    },
    {
        "id": "A5",
        "topic": "Acceleration analysis",
        "level": 5,
        "title": "Sliding ladder: velocity first, then acceleration",
        "difficulty": "Challenging",
        "diagram": "ladder_acceleration",
        "source_note": "Adapted from Hibbeler, Engineering Mechanics: Dynamics, 14th ed., Problem 16-104.",
        "description": (
            "A 16 ft ladder makes a 30Â° angle with the floor. At the instant shown, its lower end A moves left "
            "at 6 ft/s and has a leftward acceleration of 4 ft/sÂ². Determine the angular acceleration of the ladder "
            "and the vertical acceleration of its upper end B. Take counterclockwise and upward as positive."
        ),
        "givens": ["AB = 16 ft", "Î¸ = 30Â°", "v_A = 6 ft/s left", "a_A = 4 ft/sÂ² left", "CCW and upward are positive"],
        "direction_questions": [
            {
                "q": "What constraint applies to the acceleration of B?",
                "options": ["Horizontal only", "Vertical only", "Along the ladder", "Perpendicular to the ladder"],
                "correct": "Vertical only",
                "why": "The wall constrains B to move and accelerate along the vertical guide."
            },
            {
                "q": "Where does the normal relative acceleration of B point?",
                "options": ["From A toward B", "From B toward A", "Vertically upward", "Horizontally left"],
                "correct": "From B toward A",
                "why": "The normal term âˆ’Ï‰Â²r_B/A always points from B toward A."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the complete relative-acceleration equation.",
                "options": [
                    "a_B = a_A + Î± Ã— r_B/A âˆ’ Ï‰Â² r_B/A",
                    "a_B = a_A + Ï‰ Ã— r_B/A",
                    "a_B = Î±Â² r_B/A",
                    "a_B = a_A âˆ’ Î± Ã— r_B/A"
                ],
                "correct": "a_B = a_A + Î± Ã— r_B/A âˆ’ Ï‰Â² r_B/A",
                "why": "Both the tangential Î± Ã— r term and inward normal âˆ’Ï‰Â²r term are required."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration Î±_AB (CCW positive)", "key": "alphaAB", "value": -1.4743, "tol": 0.02, "unit": "rad/sÂ²"},
            {"label": "Acceleration of B (upward positive)", "key": "aB", "value": -24.9282, "tol": 0.08, "unit": "ft/sÂ²"}
        ],
        "vector_lines": [
            r"\mathbf r_{B/A}=16(\cos30^\circ\mathbf i+\sin30^\circ\mathbf j)=(13.856\mathbf i+8.000\mathbf j)\ \text{ft}",
            r"\mathbf v_B=-6\mathbf i+\omega\mathbf k\times\mathbf r_{B/A},\quad v_{Bx}=0\Rightarrow\omega=-0.750\ \text{rad/s}",
            r"\mathbf a_A=-4\mathbf i\ \text{ft/s}^2,\qquad \mathbf a_B=a_B\mathbf j"
        ],
        "solution_lines": [
            r"\mathbf a_B=\mathbf a_A+\alpha\mathbf k\times\mathbf r_{B/A}-\omega^2\mathbf r_{B/A}",
            r"0=-4-8\alpha-(0.750)^2(13.856)\Rightarrow\alpha=-1.474\ \text{rad/s}^2",
            r"a_B=13.856\alpha-(0.750)^2(8.000)=-24.93\ \text{ft/s}^2",
            r"\text{Thus }\alpha=1.47\ \text{rad/s}^2\ \text{clockwise and }B\text{ accelerates downward at }24.9\ \text{ft/s}^2."
        ],
        "teaching_point": "Use the velocity constraints first to obtain Ï‰; the normal acceleration term cannot be evaluated correctly without it.",
    },
]


def get_problem(topic, level):
    for prob in PROBLEMS:
        if prob["topic"] == topic and prob["level"] == level:
            return prob
    return None


def vector_legend_html(topic):
    items = [
        ("Mechanism / geometry", COLORS["link"]),
        ("Notes / constraints", COLORS["note"]),
        ("Known / absolute vector", COLORS["known"]),
    ]
    if topic == "Velocity analysis":
        items.extend([
            ("Relative velocity", COLORS["relative"]),
            ("Result / checked direction", COLORS["resultant"]),
        ])
    else:
        items.extend([
            ("Tangential acceleration", COLORS["tangent"]),
            ("Normal acceleration", COLORS["normal"]),
            ("Resultant / checked direction", COLORS["resultant"]),
        ])
    chips = "".join(
        f'<span class="legend-chip"><span class="legend-box" style="background:{c}"></span>{label}</span>'
        for label, c in items
    )
    return f'<div class="legend-row">{chips}</div>'


def draw_arrow(ax, start, end, color, label=None, lw=2.2, mutation=14, ls='-',
               label_offset=(0.0, 0.0), label_fraction=0.55, label_side=1.0):
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    arrow = FancyArrowPatch(
        start, end, arrowstyle='->', mutation_scale=mutation,
        linewidth=lw, color=color, linestyle=ls, shrinkA=0, shrinkB=0,
        zorder=6,
    )
    ax.add_patch(arrow)
    if label:
        delta = end - start
        length = float(np.linalg.norm(delta))
        normal = np.array([-delta[1], delta[0]]) / length if length else np.array([0.0, 1.0])
        pos = start + label_fraction * delta + 0.13 * label_side * normal + np.asarray(label_offset)
        ax.text(
            pos[0], pos[1], label, color=color, fontsize=10.5, weight='bold',
            ha='center', va='center', zorder=9,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=color, lw=0.5, alpha=0.96),
        )


def draw_double_arrow(ax, start, end, color, label=None, label_offset=(0.0, 0.0), ls='--'):
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    arrow = FancyArrowPatch(
        start, end, arrowstyle='<->', mutation_scale=13, linewidth=1.8,
        color=color, linestyle=ls, zorder=5,
    )
    ax.add_patch(arrow)
    if label:
        mid = 0.5 * (start + end) + np.asarray(label_offset)
        ax.text(mid[0], mid[1], label, color=color, fontsize=9.5, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.95), zorder=8)


def add_point(ax, point, label, offset=(0.10, 0.10), ms=7):
    point = np.asarray(point, dtype=float)
    ax.plot(*point, 'o', color='#0f172a', markeredgecolor='white', markeredgewidth=0.8, ms=ms, zorder=8)
    pos = point + np.asarray(offset)
    ax.text(pos[0], pos[1], label, fontsize=11.5, weight='bold', ha='center', va='center', zorder=9,
            bbox=dict(boxstyle="round,pad=0.10", fc="white", ec="none", alpha=0.92))


def add_sign_convention(ax, text="Positive angular sense: CCW"):
    ax.text(0.015, 0.97, text, transform=ax.transAxes, ha='left', va='top', fontsize=8.8,
            color=COLORS['note'], zorder=20,
            bbox=dict(boxstyle="round,pad=0.28", fc="#ecfeff", ec=COLORS['note'], lw=0.8, alpha=0.96))


def add_note(ax, xy, text, ha='left', va='center', fontsize=8.8):
    ax.text(xy[0], xy[1], text, color=COLORS['note'], fontsize=fontsize, ha=ha, va=va, zorder=9,
            bbox=dict(boxstyle="round,pad=0.22", fc="#f0fdfa", ec=COLORS['note'], lw=0.6, alpha=0.96))


def draw_angle(ax, vertex, radius, theta1, theta2, label, label_radius=None):
    vertex = np.asarray(vertex, dtype=float)
    ax.add_patch(Arc(vertex, 2 * radius, 2 * radius, angle=0, theta1=theta1, theta2=theta2,
                     color=COLORS['angle'], lw=2.0, zorder=5))
    mid = math.radians((theta1 + theta2) / 2)
    lr = label_radius if label_radius is not None else radius + 0.20
    pos = vertex + lr * np.array([math.cos(mid), math.sin(mid)])
    ax.text(pos[0], pos[1], label, color=COLORS['angle'], fontsize=10, weight='bold',
            ha='center', va='center', zorder=8,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.94))


def draw_rotation_arrow(ax, center, radius, theta1, theta2, color, label):
    """Draw an unmistakably curved angular-motion arrow."""
    center = np.asarray(center, dtype=float)
    angles = np.linspace(math.radians(theta1), math.radians(theta2), 80)
    points = center + radius * np.column_stack((np.cos(angles), np.sin(angles)))
    ax.plot(points[:, 0], points[:, 1], color=color, lw=2.2, zorder=5)
    draw_arrow(ax, points[-3], points[-1], color, None, lw=2.2, mutation=12)
    mid = points[len(points) // 2]
    radial = (mid - center) / np.linalg.norm(mid - center)
    pos = mid + 0.18 * radial
    ax.text(pos[0], pos[1], label, color=color, fontsize=10.5, weight='bold',
            ha='center', va='center', zorder=8,
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=color, lw=0.5, alpha=0.96))


def draw_pin_support(ax, point, scale=0.18):
    x, y = point
    tri = Polygon([(x, y - 0.02), (x - scale, y - 0.34), (x + scale, y - 0.34)],
                  closed=True, facecolor='#e2e8f0', edgecolor=COLORS['support'], lw=1.4, zorder=2)
    ax.add_patch(tri)
    ax.plot([x - 1.25 * scale, x + 1.25 * scale], [y - 0.36, y - 0.36], color=COLORS['support'], lw=1.5)


def finish_axis(ax, xlim, ylim):
    ax.figure.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    for label in ax.texts:
        if label.get_color() in (None, "auto", "black", "k", "#000000"):
            label.set_color("#0f172a")
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis('off')
    ax.margins(0.02)


def draw_fixed_velocity():
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    O = np.array([0.0, 0.0]); R = 1.0; theta = math.radians(50)
    P = O + R * np.array([math.cos(theta), math.sin(theta)])
    ax.add_patch(Circle(O, R, fill=False, linewidth=2.6, edgecolor=COLORS['link'], zorder=2))
    ax.plot([O[0], P[0]], [O[1], P[1]], color=COLORS['dimension'], linewidth=2.0, zorder=3)
    add_point(ax, O, 'O', offset=(-0.12, -0.18)); add_point(ax, P, 'P', offset=(0.12, 0.08))
    ax.text(0.37, 0.36, r'$r=0.30\ \mathrm{m}$', color=COLORS['dimension'], fontsize=9.5,
            rotation=50, ha='center', va='bottom', bbox=dict(fc='white', ec='none', alpha=0.9))
    tangent = np.array([-math.sin(theta), math.cos(theta)])
    draw_arrow(ax, P, P + 0.72 * tangent, COLORS['known'], r'$v_P$', label_offset=(0.08, 0.02))
    draw_rotation_arrow(ax, O, 0.42, -55, 75, COLORS['relative'], r'$\omega$')
    add_note(ax, (1.38, -0.72), 'Velocity is tangent\nto the circular path.', ha='center')
    add_sign_convention(ax, 'Given rotation: counterclockwise')
    finish_axis(ax, (-1.35, 2.05), (-1.25, 1.45))
    return fig


def draw_fixed_acceleration():
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    O = np.array([0.0, 0.0]); R = 1.0; theta = math.radians(55)
    P = O + R * np.array([math.cos(theta), math.sin(theta)])
    ax.add_patch(Circle(O, R, fill=False, linewidth=2.6, edgecolor=COLORS['link'], zorder=2))
    ax.plot([O[0], P[0]], [O[1], P[1]], color=COLORS['dimension'], linewidth=2.0, zorder=3)
    add_point(ax, O, 'O', offset=(-0.12, -0.18)); add_point(ax, P, 'P', offset=(0.12, 0.10))
    tangent = np.array([-math.sin(theta), math.cos(theta)])
    inward = (O - P) / np.linalg.norm(O - P)
    draw_arrow(ax, P, P + 0.70 * tangent, COLORS['tangent'], r'$a_t$', label_offset=(0.08, 0.03))
    draw_arrow(ax, P, P + 0.72 * inward, COLORS['normal'], r'$a_n$', label_offset=(-0.02, -0.12), label_side=-1)
    resultant = 0.18 * tangent + 0.92 * inward
    draw_arrow(ax, P + np.array([0.08, -0.04]), P + np.array([0.08, -0.04]) + 0.72 * resultant,
               COLORS['resultant'], r'$\mathbf{a}$', label_offset=(0.12, 0.02), label_side=1)
    add_note(ax, (1.44, -0.82), 'Orange: tangential\nRed: inward normal\nGreen: resultant', ha='center')
    add_sign_convention(ax)
    finish_axis(ax, (-1.35, 2.15), (-1.28, 1.48))
    return fig


def draw_slider_velocity(accel=False):
    fig, ax = plt.subplots(figsize=(8.2, 4.7))
    A = np.array([0.55, 0.55]); L = 2.55; theta = math.radians(30)
    B = A + L * np.array([math.cos(theta), math.sin(theta)])
    # Ground reference and vertical slider guide.
    ax.plot([A[0], A[0] + 1.15], [A[1], A[1]], color=COLORS['construct'], lw=1.4, ls='--')
    ax.plot([B[0]-0.30, B[0]-0.30], [B[1]-1.15, B[1]+1.20], color=COLORS['guide'], lw=2.2)
    ax.plot([B[0]+0.30, B[0]+0.30], [B[1]-1.15, B[1]+1.20], color=COLORS['guide'], lw=2.2)
    ax.add_patch(Rectangle((B[0]-0.20, B[1]-0.28), 0.40, 0.56, facecolor='#f8fafc',
                           edgecolor=COLORS['link'], lw=2.0, zorder=3))
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS['link'], lw=3.0, zorder=3)
    add_point(ax, A, 'A', offset=(-0.12, -0.23)); add_point(ax, B, 'B', offset=(0.15, 0.10))
    mid = (A + B) / 2; normal = np.array([-math.sin(theta), math.cos(theta)])
    ax.text(*(mid + 0.19 * normal), 'AB = 0.50 m', color=COLORS['dimension'], fontsize=9.5,
            rotation=30, ha='center', va='bottom', bbox=dict(fc='white', ec='none', alpha=0.92))
    draw_angle(ax, A, 0.55, 0, 30, r'$30^\circ$', label_radius=0.84)
    if not accel:
        draw_arrow(ax, A + np.array([-0.05, -0.24]), A + np.array([0.95, -0.24]), COLORS['known'],
                   r'$v_A$', label_offset=(0.0, -0.10), label_side=-1)
        draw_arrow(ax, B + np.array([0.58, -0.40]), B + np.array([0.58, 0.88]), COLORS['known'],
                   r'$v_B$', label_offset=(0.12, 0.0), label_side=-1)
        draw_arrow(ax, mid - 0.34 * normal, mid + 0.66 * normal, COLORS['relative'],
                   r'$v_{B/A}$', label_offset=(0.10, 0.02), label_fraction=0.70)
        add_note(ax, (3.70, 0.36), 'Slider velocity is vertical.', ha='right')
    else:
        add_note(ax, (0.46, 2.08), r'$a_A=0$ (A moves at constant speed)')
        draw_double_arrow(ax, B + np.array([0.60, -0.80]), B + np.array([0.60, 0.80]), COLORS['known'],
                          r'$a_B$ along guide', label_offset=(0.45, 0.0))
        toward_A = (A - B) / np.linalg.norm(A - B)
        draw_arrow(ax, mid - 0.38 * normal, mid + 0.55 * normal, COLORS['tangent'],
                   r'$a^t_{B/A}$', label_offset=(-0.14, -0.10), label_fraction=0.25, label_side=-1)
        draw_arrow(ax, B - 0.05 * toward_A, B + 0.88 * toward_A, COLORS['normal'],
                   r'$a^n_{B/A}$', label_offset=(0.02, -0.14), label_side=-1)
        add_note(ax, (3.75, 0.28), 'Normal component points\nfrom B toward A.', ha='right')
    add_sign_convention(ax)
    finish_axis(ax, (-0.30, 4.10), (-0.35, 3.05))
    return fig


def draw_linked_velocity(accel=False):
    fig, ax = plt.subplots(figsize=(9.0, 5.1))
    A = np.array([0.8, 3.15]); B = np.array([3.65, 3.15]); C = np.array([3.65, 0.55])
    # Groove through C at -45 degrees.
    t = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))])
    n = np.array([-t[1], t[0]])
    for off in (-0.13, 0.13):
        p0 = C - 1.20 * t + off * n; p1 = C + 2.05 * t + off * n
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=COLORS['guide'], lw=2.0, zorder=1)
    ax.plot([C[0], C[0] + 1.05], [C[1], C[1]], color=COLORS['construct'], lw=1.3, ls='--')
    draw_angle(ax, C, 0.62, -45, 0, r'$45^\circ$', label_radius=0.92)
    add_note(ax, (5.38, -0.70), 'Inclined slider guide', ha='center')
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS['link'], lw=3.2, zorder=3)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS['link'], lw=3.2, zorder=3)
    draw_pin_support(ax, A, scale=0.20)
    add_point(ax, A, 'A', offset=(-0.10, 0.15), ms=8); add_point(ax, B, 'B', offset=(0.13, 0.14), ms=8)
    add_point(ax, C, 'C', offset=(-0.17, -0.12), ms=8)
    ax.text(2.22, 3.42, 'AB = 2 m', fontsize=10.5, color=COLORS['dimension'], ha='center')
    ax.text(3.92, 1.86, 'BC = 2 m', fontsize=10.5, color=COLORS['dimension'], rotation=90, va='center')
    if not accel:
        draw_arrow(ax, B + np.array([0.58, 0.08]), B + np.array([0.58, -1.18]), COLORS['known'],
                   r'$v_B$', label_offset=(0.13, 0.0), label_side=-1)
        draw_arrow(ax, C + np.array([0.25, -0.02]), C + 1.15 * t + np.array([0.25, -0.02]), COLORS['known'],
                   r'$v_C$', label_offset=(0.08, -0.02), label_side=1)
        draw_arrow(ax, np.array([3.05, 1.78]), np.array([1.92, 1.78]), COLORS['relative'],
                   r'$v_{C/B}$', label_offset=(0.0, 0.08), label_side=-1)
    else:
        draw_double_arrow(ax, B + np.array([0.62, -0.80]), B + np.array([0.62, 0.80]), COLORS['known'],
                          r'$a_B$', label_offset=(0.28, 0.0))
        draw_arrow(ax, C + np.array([0.24, -0.02]), C + 1.12 * t + np.array([0.24, -0.02]), COLORS['known'],
                   r'$a_C$', label_offset=(0.08, -0.02), label_side=1)
        draw_arrow(ax, np.array([3.05, 1.65]), np.array([2.00, 1.65]), COLORS['tangent'],
                   r'$a^t_{C/B}$', label_offset=(0.0, 0.10), label_side=-1)
        draw_arrow(ax, np.array([2.55, 0.85]), np.array([2.55, 1.95]), COLORS['normal'],
                   r'$a^n_{C/B}$', label_offset=(-0.17, 0.0), label_side=1)
        add_note(ax, (1.72, 2.22), 'Normal component points toward B.')
    add_sign_convention(ax)
    finish_axis(ax, (0.05, 6.20), (-1.30, 3.92))
    return fig


def draw_ic_velocity():
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    A = np.array([0.70, 0.60]); B = A + 1.85 * np.array([math.cos(math.radians(45)), math.sin(math.radians(45))])
    C = B + 2.75 * np.array([math.cos(math.radians(-30)), math.sin(math.radians(-30))])
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS['link'], lw=3.0)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS['link'], lw=3.0)
    draw_pin_support(ax, A, scale=0.18)
    # Horizontal slider guide.
    ax.plot([C[0]-0.95, C[0]+0.85], [C[1]-0.25, C[1]-0.25], color=COLORS['guide'], lw=2.1)
    ax.plot([C[0]-0.95, C[0]+0.85], [C[1]+0.25, C[1]+0.25], color=COLORS['guide'], lw=2.1)
    ax.add_patch(Rectangle((C[0]-0.23, C[1]-0.17), 0.46, 0.34, facecolor='#f8fafc', ec=COLORS['link'], lw=2.0))
    add_point(ax, A, 'A', offset=(-0.12, -0.22)); add_point(ax, B, 'B', offset=(0.11, 0.12)); add_point(ax, C, 'C', offset=(0.10, 0.22))
    ax.plot([A[0], A[0]+0.85], [A[1], A[1]], color=COLORS['construct'], ls='--', lw=1.2)
    draw_angle(ax, A, 0.48, 0, 45, r'$45^\circ$', label_radius=0.72)
    ax.plot([B[0], B[0]+0.85], [B[1], B[1]], color=COLORS['construct'], ls='--', lw=1.2)
    draw_angle(ax, B, 0.52, -30, 0, r'$30^\circ$', label_radius=0.80)
    ax.text(*(0.5*(A+B)+np.array([-0.16,0.22])), 'AB = 0.200 m', fontsize=9.4, color=COLORS['dimension'], rotation=45, ha='center')
    ax.text(*(0.5*(B+C)+np.array([0.0,0.27])), 'BC = 0.500 m', fontsize=9.4, color=COLORS['dimension'], rotation=-30, ha='center')
    draw_arrow(ax, B + np.array([0.03, 0.03]), B + np.array([-0.88, 0.92]), COLORS['known'], r'$v_B$', label_offset=(-0.08, 0.08))
    draw_arrow(ax, C + np.array([0.10, 0.42]), C + np.array([-1.12, 0.42]), COLORS['known'], r'$v_C$', label_offset=(0.0, 0.08), label_side=-1)
    # IC construction: radius at C is vertical; radius at B is parallel to AB.
    ax.plot([C[0], C[0]], [C[1]-2.75, C[1]+0.95], color=COLORS['construct'], lw=1.7, ls='--')
    xline = np.array([B[0]-1.6, B[0]+2.8]); yline = B[1] + (xline-B[0])
    ax.plot(xline, yline, color=COLORS['construct'], lw=1.7, ls='--')
    IC = np.array([C[0], B[1] + (C[0]-B[0])])
    add_point(ax, IC, 'IC', offset=(0.18, 0.06), ms=6)
    add_note(ax, (C[0]+0.16, IC[1]-0.28), 'Line âŠ¥ to slider velocity')
    add_note(ax, (B[0]-1.45, B[1]+1.02), r'Line âŠ¥ to $v_B$')
    add_sign_convention(ax)
    finish_axis(ax, (-0.15, 6.25), (-1.30, 4.25))
    return fig


def draw_belt_velocity(accel=False):
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    A = np.array([2.0, 2.15]); rA = 0.82; B = np.array([6.15, 2.15]); rB = 0.52
    ax.add_patch(Circle(A, rA, facecolor='#f8fafc', edgecolor=COLORS['link'], lw=2.6))
    ax.add_patch(Circle(B, rB, facecolor='#f8fafc', edgecolor=COLORS['link'], lw=2.6))
    add_point(ax, A, 'A', offset=(-0.12, -0.13), ms=6); add_point(ax, B, 'B', offset=(-0.12, -0.13), ms=6)
    ax.plot([A[0], A[0]+rA], [A[1], A[1]], color=COLORS['dimension'], lw=1.8)
    ax.plot([B[0], B[0]+rB], [B[1], B[1]], color=COLORS['dimension'], lw=1.8)
    ax.text(A[0]+0.44, A[1]+0.10, r'$r_A$', color=COLORS['dimension'], fontsize=10)
    ax.text(B[0]+0.27, B[1]+0.10, r'$r_B$', color=COLORS['dimension'], fontsize=10)
    if not accel:
        topA=A+np.array([0,rA]); topB=B+np.array([0,rB]); botA=A-np.array([0,rA]); botB=B-np.array([0,rB])
        ax.plot([topA[0],topB[0]],[topA[1],topB[1]],color=COLORS['guide'],lw=3.0)
        ax.plot([botA[0],botB[0]],[botA[1],botB[1]],color=COLORS['guide'],lw=3.0)
        draw_arrow(ax, (3.25,2.92),(4.45,2.82),COLORS['relative'],r'$v_{belt}$',label_offset=(0,0.10),label_side=-1)
        draw_arrow(ax, (4.85,1.43),(3.65,1.33),COLORS['relative'],None)
        add_note(ax,(4.10,3.55),'Open belt: pulleys rotate in the same sense.',ha='center')
        senseB=1
    else:
        ax.plot([A[0],B[0]],[A[1]+rA,B[1]-rB],color=COLORS['guide'],lw=3.0)
        ax.plot([A[0],B[0]],[A[1]-rA,B[1]+rB],color=COLORS['guide'],lw=3.0)
        draw_arrow(ax,(3.10,2.90),(4.25,2.20),COLORS['relative'],r'$v_{belt}$',label_offset=(-0.05,0.10),label_side=-1)
        draw_arrow(ax,(5.00,1.38),(3.85,2.06),COLORS['relative'],None)
        add_note(ax,(4.10,3.58),'Crossed belt: pulleys rotate in opposite senses.',ha='center')
        senseB=-1
    draw_arrow(ax, A+np.array([-0.65,0.60]), A+np.array([0.12,0.94]), COLORS['known'], r'$\omega_A$', label_offset=(-0.05,0.08))
    if senseB==1:
        draw_arrow(ax, B+np.array([-0.40,0.43]), B+np.array([0.12,0.61]), COLORS['resultant'], r'$\omega_B$', label_offset=(0.07,0.08))
    else:
        draw_arrow(ax, B+np.array([-0.40,-0.43]), B+np.array([0.12,-0.61]), COLORS['resultant'], r'$\omega_B$', label_offset=(0.04,-0.10), label_side=-1)
    if accel:
        P=B+np.array([0,rB]); add_point(ax,P,'P',offset=(0.12,0.08),ms=5)
        draw_arrow(ax,P+np.array([0.10,0.02]),P+np.array([0.95,0.02]),COLORS['tangent'],r'$a_t$',label_offset=(0.0,0.10))
        draw_arrow(ax,P+np.array([0,-0.03]),P+np.array([0,-0.75]),COLORS['normal'],r'$a_n$',label_offset=(0.15,0.0),label_side=-1)
        add_note(ax,(5.30,0.42),r'Normal acceleration is local: $a_n=v^2/r$.',ha='center')
    add_sign_convention(ax)
    finish_axis(ax,(0.55,7.35),(0.10,4.05))
    return fig


def draw_gear_train():
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    O = np.array([3.80, 2.20])
    radii = {'A':0.55,'B':1.05,'C':0.65,'D':1.25}
    centers = {
        'B':O, 'C':O,
        'A':O-np.array([radii['A']+radii['B'],0.0]),
        'D':O+np.array([radii['C']+radii['D'],0.0]),
    }
    # Draw large same-shaft gear first, then the smaller concentric gear.
    for name in ['B','A','D','C']:
        c=centers[name]; r=radii[name]
        face='#f8fafc' if name in ('A','D') else ('#eef2ff' if name=='B' else '#ecfeff')
        ax.add_patch(Circle(c,r,facecolor=face,edgecolor=COLORS['link'],lw=2.5,zorder=2 if name!='C' else 3))
        ax.plot(*c,'o',color=COLORS['support'],ms=4,zorder=5)
    ax.text(centers['A'][0]-0.08, centers['A'][1]-0.05, 'A', weight='bold', fontsize=11)
    ax.text(O[0]-0.15, O[1]+0.75, 'B', weight='bold', fontsize=11)
    ax.text(O[0]-0.15, O[1]-0.18, 'C', weight='bold', fontsize=11)
    ax.text(centers['D'][0]-0.08, centers['D'][1]-0.05, 'D', weight='bold', fontsize=11)
    # Contact points show true tangency.
    ax.plot(O[0]-radii['B'],O[1],'o',color=COLORS['angle'],ms=5,zorder=6)
    ax.plot(O[0]+radii['C'],O[1],'o',color=COLORS['angle'],ms=5,zorder=6)
    ax.annotate('B and C are concentric\nand fixed to the same shaft', xy=O, xytext=(4.05,4.28),
                ha='center', va='center', fontsize=9.2, color=COLORS['note'],
                bbox=dict(boxstyle='round,pad=0.25',fc='#f0fdfa',ec=COLORS['note'],lw=0.7),
                arrowprops=dict(arrowstyle='->',color=COLORS['note'],lw=1.2))
    add_note(ax,(1.35,4.05),'External mesh\nreverses direction',ha='center')
    add_note(ax,(6.55,4.15),'External mesh\nreverses direction',ha='center')
    draw_arrow(ax, centers['A']+np.array([-0.48,0.52]), centers['A']+np.array([0.16,0.68]), COLORS['known'], r'$\omega_A$', label_offset=(-0.06,0.09))
    draw_arrow(ax, centers['D']+np.array([-0.72,1.04]), centers['D']+np.array([0.20,1.30]), COLORS['resultant'], r'$\omega_D$', label_offset=(0.04,0.09))
    ax.text(centers['A'][0],1.25,'20 teeth',ha='center',fontsize=9.3,color=COLORS['dimension'])
    ax.text(O[0]-0.75,0.38,'B: 60 teeth',ha='center',fontsize=9.3,color=COLORS['dimension'])
    ax.text(O[0]+0.72,0.66,'C: 30 teeth',ha='center',fontsize=9.3,color=COLORS['dimension'])
    ax.text(centers['D'][0],0.28,'90 teeth',ha='center',fontsize=9.3,color=COLORS['dimension'])
    add_sign_convention(ax)
    finish_axis(ax,(0.55,7.55),(0.05,4.72))
    return fig


def draw_two_link_translation():
    fig, ax = plt.subplots(figsize=(9.0, 4.8))
    A=np.array([0.70,0.75]); B=np.array([2.60,0.75]); C=B+2.35*np.array([math.cos(math.radians(30)),math.sin(math.radians(30))])
    draw_pin_support(ax,A,scale=0.18)
    ax.plot([A[0],B[0]],[A[1],B[1]],color=COLORS['link'],lw=3.0)
    ax.plot([B[0],C[0]],[B[1],C[1]],color=COLORS['link'],lw=3.0)
    ax.plot([C[0]-0.28,C[0]-0.28],[C[1]-1.05,C[1]+1.05],color=COLORS['guide'],lw=2.1)
    ax.plot([C[0]+0.28,C[0]+0.28],[C[1]-1.05,C[1]+1.05],color=COLORS['guide'],lw=2.1)
    ax.add_patch(Rectangle((C[0]-0.20,C[1]-0.27),0.40,0.54,facecolor='#f8fafc',ec=COLORS['link'],lw=2))
    add_point(ax,A,'A',offset=(-0.10,0.14)); add_point(ax,B,'B',offset=(-0.18,-0.20)); add_point(ax,C,'C',offset=(0.15,0.10))
    ax.plot([B[0],B[0]+0.90],[B[1],B[1]],color=COLORS['construct'],ls='--',lw=1.2)
    draw_angle(ax,B,0.52,0,30,r'$30^\circ$',label_radius=0.78)
    ax.text(1.65,0.48,'AB = 2 ft',color=COLORS['dimension'],fontsize=9.5,ha='center')
    ax.text(*(0.5*(B+C)+np.array([-0.16,0.30])),'BC = 3 ft',color=COLORS['dimension'],fontsize=9.5,rotation=30,ha='center')
    draw_arrow(ax,C+np.array([0.58,0.45]),C+np.array([0.58,-0.75]),COLORS['known'],r'$v_C=4\ \mathrm{ft/s}$',label_offset=(0.42,0.0),label_side=-1)
    draw_double_arrow(ax,B+np.array([0.0,-0.62]),B+np.array([0.0,0.62]),COLORS['known'],r'$v_B$ vertical',label_offset=(-0.50,0.22))
    # Direction marker only; its magnitude is found from the equations.
    normal=np.array([-math.sin(math.radians(30)),math.cos(math.radians(30))])
    mid=0.5*(B+C)
    draw_double_arrow(ax,mid-0.40*normal,mid+0.40*normal,COLORS['relative'],r'$v_{C/B}\perp BC$',label_offset=(0.05,-0.23))
    add_note(ax,(5.18,-0.12),'Purple double arrow shows direction only.',ha='right')
    add_sign_convention(ax)
    finish_axis(ax,(0.05,5.55),(-0.35,3.30))
    return fig


def draw_ic_two_link():
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    A=np.array([0.85,3.45]); B=A+2.15*np.array([math.cos(math.radians(-45)),math.sin(math.radians(-45))])
    C=B+2.00*np.array([math.cos(math.radians(30)),math.sin(math.radians(30))])
    draw_pin_support(ax,A,scale=0.18)
    ax.plot([A[0],B[0]],[A[1],B[1]],color=COLORS['link'],lw=3.0)
    ax.plot([B[0],C[0]],[B[1],C[1]],color=COLORS['link'],lw=3.0)
    ax.plot([C[0]-0.28,C[0]-0.28],[C[1]-1.0,C[1]+1.0],color=COLORS['guide'],lw=2.1)
    ax.plot([C[0]+0.28,C[0]+0.28],[C[1]-1.0,C[1]+1.0],color=COLORS['guide'],lw=2.1)
    ax.add_patch(Rectangle((C[0]-0.20,C[1]-0.27),0.40,0.54,facecolor='#f8fafc',ec=COLORS['link'],lw=2))
    add_point(ax,A,'A',offset=(-0.12,0.15)); add_point(ax,B,'B',offset=(-0.04,-0.20)); add_point(ax,C,'C',offset=(0.15,0.10))
    ax.plot([A[0],A[0]+0.85],[A[1],A[1]],color=COLORS['construct'],ls='--',lw=1.2)
    draw_angle(ax,A,0.48,-45,0,r'$45^\circ$',label_radius=0.75)
    ax.plot([B[0],B[0]+0.80],[B[1],B[1]],color=COLORS['construct'],ls='--',lw=1.2)
    draw_angle(ax,B,0.50,0,30,r'$30^\circ$',label_radius=0.76)
    ax.text(*(0.5*(A+B)+np.array([-0.20,0.0])),'AB = 5 in.',color=COLORS['dimension'],fontsize=9.5,rotation=-45,ha='center')
    ax.text(*(0.5*(B+C)+np.array([-0.05,0.24])),'BC = 4 in.',color=COLORS['dimension'],fontsize=9.5,rotation=30,ha='center')
    draw_arrow(ax,C+np.array([0.58,-0.42]),C+np.array([0.58,0.80]),COLORS['known'],r'$v_C=12\ \mathrm{in./s}$',label_offset=(0.46,0.0),label_side=-1)
    draw_arrow(ax,B+np.array([0.05,0.05]),B+np.array([0.80,0.80]),COLORS['known'],r'$v_B$',label_offset=(-0.08,0.08))
    # IC construction for link BC.
    dAB=(B-A)/np.linalg.norm(B-A)
    ax.plot([B[0]-0.8*dAB[0],B[0]+3.0*dAB[0]],[B[1]-0.8*dAB[1],B[1]+3.0*dAB[1]],color=COLORS['construct'],ls='--',lw=1.7)
    ax.plot([C[0],C[0]],[C[1]-2.85,C[1]+0.55],color=COLORS['construct'],ls='--',lw=1.7)
    t=(C[0]-B[0])/dAB[0]; IC=B+t*dAB
    add_point(ax,IC,'IC',offset=(0.20,0.10),ms=6)
    add_note(ax,(1.18,1.18),r'Radius through B is âŠ¥ to $v_B$.')
    add_note(ax,(4.85,0.42),r'Radius through C is âŠ¥ to $v_C$.',ha='right')
    add_sign_convention(ax)
    finish_axis(ax,(0.05,6.15),(-0.45,4.35))
    return fig


def draw_ladder_acceleration():
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    A=np.array([0.75,0.55]); B=A+4.0*np.array([math.cos(math.radians(30)),math.sin(math.radians(30))])
    ax.plot([0.15,B[0]+0.60],[0.45,0.45],color=COLORS['support'],lw=3.0)
    ax.plot([B[0]+0.12,B[0]+0.12],[0.45,3.55],color=COLORS['support'],lw=3.0)
    # Wall/floor hatch marks.
    for x in np.linspace(0.35,B[0]+0.45,10): ax.plot([x,x+0.12],[0.45,0.32],color=COLORS['guide'],lw=0.8)
    for y in np.linspace(0.65,3.40,9): ax.plot([B[0]+0.12,B[0]+0.25],[y,y+0.12],color=COLORS['guide'],lw=0.8)
    ax.plot([A[0],B[0]],[A[1],B[1]],color=COLORS['link'],lw=4.0,zorder=3)
    add_point(ax,A,'A',offset=(0.0,-0.22)); add_point(ax,B,'B',offset=(-0.18,0.12))
    ax.plot([A[0],A[0]+1.0],[A[1],A[1]],color=COLORS['construct'],ls='--',lw=1.2)
    draw_angle(ax,A,0.62,0,30,r'$30^\circ$',label_radius=0.90)
    ax.text(*(0.5*(A+B)+np.array([-0.12,0.20])),'AB = 16 ft',color=COLORS['dimension'],fontsize=10,rotation=30,ha='center')
    draw_arrow(ax,A+np.array([0.28,0.58]),A+np.array([-0.92,0.58]),COLORS['known'],r'$v_A=6\ \mathrm{ft/s}$',label_offset=(0.0,0.11),label_side=-1)
    draw_arrow(ax,A+np.array([0.28,0.98]),A+np.array([-0.72,0.98]),COLORS['known'],r'$a_A=4\ \mathrm{ft/s^2}$',label_offset=(0.0,0.11),label_side=-1)
    draw_double_arrow(ax,B+np.array([0.48,-0.72]),B+np.array([0.48,0.72]),COLORS['resultant'],r'$a_B$ vertical',label_offset=(0.48,0.0))
    inward=(A-B)/np.linalg.norm(A-B); tangent=np.array([-inward[1],inward[0]])
    draw_arrow(ax,B+np.array([-0.10,-0.05]),B+np.array([-0.10,-0.05])+0.92*inward,COLORS['normal'],r'$a^n_{B/A}$',label_offset=(0.0,-0.13),label_side=-1)
    draw_arrow(ax,B+np.array([-0.08,0.05]),B+np.array([-0.08,0.05])+0.78*tangent,COLORS['tangent'],r'$a^t_{B/A}$',label_offset=(-0.12,0.06))
    add_note(ax,(3.95,3.52),'Orange arrow assumes positive Î± (CCW).',ha='right')
    add_sign_convention(ax,'Sign convention: +Î± is CCW; +a_B is upward')
    finish_axis(ax,(-0.45,5.35),(0.15,4.05))
    return fig


def render_problem_figure(problem):
    if problem["diagram"] == "fixed_velocity":
        fig = draw_fixed_velocity()
    elif problem["diagram"] == "fixed_acceleration":
        fig = draw_fixed_acceleration()
    elif problem["diagram"] == "slider_velocity":
        fig = draw_slider_velocity(accel=False)
    elif problem["diagram"] == "slider_acceleration":
        fig = draw_slider_velocity(accel=True)
    elif problem["diagram"] == "linked_velocity":
        fig = draw_linked_velocity(accel=False)
    elif problem["diagram"] == "linked_acceleration":
        fig = draw_linked_velocity(accel=True)
    elif problem["diagram"] == "ic_velocity":
        fig = draw_ic_velocity()
    elif problem["diagram"] == "belt_velocity":
        fig = draw_belt_velocity(accel=False)
    elif problem["diagram"] == "belt_acceleration":
        fig = draw_belt_velocity(accel=True)
    elif problem["diagram"] == "gear_train":
        fig = draw_gear_train()
    elif problem["diagram"] == "two_link_translation":
        fig = draw_two_link_translation()
    elif problem["diagram"] == "ic_two_link":
        fig = draw_ic_two_link()
    elif problem["diagram"] == "ladder_acceleration":
        fig = draw_ladder_acceleration()
    else:
        fig, _ = plt.subplots()
    st.pyplot(fig, clear_figure=True, width="stretch")


def render_learn_tab(topic):
    st.markdown("## Main points and formulas")
    st.markdown(
        """
        <div class="info">
        Use this tab before solving. The goal is to teach a method:
        first identify the motion constraints, then choose the correct equation,
        and only after that substitute the numbers.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if topic == "Velocity analysis":
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("### Step-by-step method")
            st.markdown(
                r"""
                1. **Classify the motion**: translation, fixed-axis rotation, general plane motion, belt/pulley, gear, or instantaneous-centre problem.  
                2. **Mark the known velocity directions** from geometry and constraints before writing equations.  
                3. **Choose the most efficient method**:
                   - fixed-axis rotation,
                   - relative velocity,
                   - IC method,
                   - no-slip belt/pulley relation,
                   - gear-speed relation.  
                4. **Resolve angled vectors into** \(\mathbf{i}\) **and** \(\mathbf{j}\) **components**.  
                5. **Solve the scalar equations** and then check whether the sign and direction make physical sense.  
                """
            )

            st.markdown("### Core equations")
            st.latex(r"\mathbf v_B=\mathbf v_A+\boldsymbol\omega\times\mathbf r_{B/A}")
            st.latex(r"v=\omega r \qquad \text{(fixed-axis rotation)}")
            st.latex(r"\omega_A r_A=\omega_B r_B \qquad \text{(no-slip belt / pulley, equal tangential speed)}")
            st.latex(r"\omega_1 r_1=\omega_2 r_2 \quad \text{or} \quad \omega_1 N_1=\omega_2 N_2 \qquad \text{(gear magnitudes)}")
            st.latex(r"v=\omega\,r_{/IC} \qquad \text{(instantaneous-centre method)}")

            st.markdown("### Important direction rules")
            st.markdown(
                """
                - For a point on a rotating link, velocity is **perpendicular to the line from the centre/base point to that point**.  
                - For a slider, velocity must lie **along its guide**.  
                - For two points on the same rigid body, the relative velocity term is **perpendicular to the line joining the two points**.  
                - For an **open belt**, the pulleys rotate in the **same direction**.  
                - For a **crossed belt**, the pulleys rotate in **opposite directions**.  
                - For **external gears**, the angular velocities are in **opposite directions**.  
                - For gears on the **same shaft**, the angular velocity is the **same**.  
                """
            )

        with col2:
            st.markdown("### When should students use each method?")
            st.markdown(
                r"""
                - **Pure translation** â†’ every point has the **same velocity vector**.  
                - **Fixed-axis rotation** â†’ use \(v=\omega r\) at each point.  
                - **Two points on one moving link** â†’ use the **relative-velocity equation**.  
                - **Slider-link with known directions** â†’ the **IC method** is often fastest for velocity only.  
                - **Belts / pulleys** â†’ use **equal tangential belt speed**.  
                - **Gears** â†’ use **equal pitch-line speed** and the correct direction reversal.  
                """
            )

            st.markdown(
                """
                <div class="warning">
                <b>Important warning</b><br>
                The instantaneous centre is mainly a <b>velocity</b> method.
                It is excellent for direction and speed ratios, but it is not a complete
                acceleration method.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### Common mistakes")
            st.markdown(
                """
                - Drawing the relative velocity **along** the link instead of **perpendicular** to it.  
                - Forgetting that a slider can move **only along the guide**.  
                - Using a belt/pulley equation but then assigning the **wrong rotation direction**.  
                - Forgetting that **external gears reverse direction**.  
                - Confusing **same shaft** with **meshing contact**.  
                - Skipping the vector-resolution step and substituting numbers into the wrong component.  
                - Using the IC method automatically even when the problem is better solved by relative velocity.  
                """
            )

            st.markdown("### Quick teaching reminders")
            st.markdown(
                """
                - Always sketch the direction of each unknown vector first.  
                - If the answer sign comes out negative, it usually means the real direction is opposite to your assumed direction.  
                - In multi-link mechanisms, a point shared by two links has **one physical velocity**, even though each link has its own angular velocity.  
                """
            )

    else:
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("### Step-by-step method")
            st.markdown(
                r"""
                1. **Do the velocity analysis first** if any normal term depends on \(\omega\).  
                2. **Mark the acceleration constraints** of fixed points, sliders, pulleys, and shared pins.  
                3. **Split the relative acceleration into tangential and normal parts**.  
                4. **Write the full vector equation**, not only one part.  
                5. **Resolve into** \(\mathbf{i}\) **and** \(\mathbf{j}\) **components** and solve.  
                """
            )

            st.markdown("### Core equations")
            st.latex(r"\mathbf a_B=\mathbf a_A+\boldsymbol\alpha\times\mathbf r_{B/A}-\omega^2\mathbf r_{B/A}")
            st.latex(r"a_t=\alpha r")
            st.latex(r"a_n=\omega^2 r=\dfrac{v^2}{r}")
            st.latex(r"\alpha_A r_A=\alpha_B r_B \qquad \text{(no-slip tangential acceleration only)}")

            st.markdown("### Direction rules")
            st.markdown(
                r"""
                - Tangential acceleration \(a_t\) is **perpendicular** to the radius or link.  
                - Normal acceleration \(a_n\) points **toward the centre / base point**.  
                - For a link \(AB\), the relative normal acceleration of \(B\) with respect to \(A\) points **from B toward A**.  
                - Slider acceleration must lie **along the guide**.  
                """
            )

        with col2:
            st.markdown("### Big teaching idea")
            st.markdown(
                r"""
                Acceleration analysis is harder than velocity analysis because the relative term has
                **two rotational parts**:
                - a **tangential component** from angular acceleration \(\alpha\)
                - a **normal component** from angular velocity \(\omega\)
                """
            )

            st.markdown(
                """
                <div class="warning">
                <b>Important warning</b><br>
                Do not start with acceleration if the normal term needs a known angular velocity.
                In many mechanism problems, the velocity step must be done first.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("### Common mistakes")
            st.markdown(
                r"""
                - Forgetting the normal term \(\omega^2 r\).  
                - Writing \(\alpha^2 r\) instead of \(\omega^2 r\).  
                - Drawing the normal acceleration **away from** the centre instead of **toward** it.  
                - Treating the IC as a fixed centre for acceleration.  
                - Forgetting that for pulleys / belts, the **tangential** acceleration relationship transfers through no-slip, but the **normal** acceleration is not generally the same because \(a_n=v^2/r\).  
                - Ignoring slider direction constraints.  
                - Mixing tangential and normal parts into one undefined arrow.  
                """
            )

            st.markdown("### Quick teaching reminders")
            st.markdown(
                r"""
                - Always label which part is **tangential** and which part is **normal**.  
                - If you know the belt speed is the same on two pulleys, that does **not** mean the normal accelerations are the same; different radii give different \(v^2/r\).  
                - A negative angular acceleration result means the real sense is opposite to the assumed positive sense.  
                """
            )


def is_close(student, target, tol):
    try:
        return abs(float(student) - float(target)) <= tol
    except Exception:
        return False


def render_direction_tab(problem, mode):
    st.markdown("## Direction check")
    st.markdown(
        """
        <div class="info">
        Choose the correct direction rules before doing the calculations.
        The app uses colour to distinguish the different vectors in the mechanism drawing.
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_problem_figure(problem)
    st.markdown(vector_legend_html(problem["topic"]), unsafe_allow_html=True)
    st.markdown("---")

    for i, item in enumerate(problem["direction_questions"]):
        st.markdown(f"**{i+1}. {item['q']}**")
        response = st.radio(
            f"Direction question {i+1}",
            item["options"],
            key=f"{problem['id']}_dir_{i}",
            label_visibility="collapsed",
        )
        if mode == "Practice":
            if response == item["correct"]:
                st.markdown(f"<div class='good'>Correct. {item['why']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bad'>Not yet. {item['why']}</div>", unsafe_allow_html=True)


def render_equation_tab(problem, mode):
    st.markdown("## Choose the method and the equation")
    st.markdown(
        """
        <div class="info">
        This step teaches students which equation belongs to this type of mechanism.
        The goal is to prevent formula selection errors before the arithmetic begins.
        </div>
        """,
        unsafe_allow_html=True,
    )
    for i, item in enumerate(problem["equation_questions"]):
        st.markdown(f"**{i+1}. {item['q']}**")
        response = st.radio(
            f"Equation question {i+1}",
            item["options"],
            key=f"{problem['id']}_eq_{i}",
            label_visibility="collapsed",
        )
        if mode == "Practice":
            if response == item["correct"]:
                st.markdown(f"<div class='good'>Correct. {item['why']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bad'>Try again. {item['why']}</div>", unsafe_allow_html=True)


def render_problem_tab(problem):
    c1, c2 = st.columns([1.0, 1.1], gap="large")
    with c1:
        st.markdown("## Current problem")
        st.caption(f"{problem['topic']} | Level {problem['level']} | Difficulty: {problem['difficulty']}")
        st.markdown(problem["description"])
        if problem.get("source_note"):
            st.caption(problem["source_note"])
        st.markdown(
            "<div class='hint'><b>Given values</b><br>" + "<br>".join(f"â€¢ {g}" for g in problem["givens"]) + "</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("### Current mechanism diagram")
        render_problem_figure(problem)
        st.markdown(vector_legend_html(problem["topic"]), unsafe_allow_html=True)


def render_solve_tab(problem, mode):
    st.markdown("## Solve and check")
    st.markdown(
        """
        <div class="info">
        Enter the numerical answers. Use the sign convention stated in the question.
        If the question asks for a magnitude only, enter a positive magnitude.
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(min(2, len(problem["solve_outputs"])))
    entered = {}
    for i, out in enumerate(problem["solve_outputs"]):
        with cols[i % len(cols)]:
            entered[out["key"]] = st.number_input(
                f"{out['label']} ({out['unit']})",
                key=f"{problem['id']}_{out['key']}",
                format="%.4f",
            )

    if st.button("Check final answers", key=f"check_{problem['id']}"):
        checks = []
        for out in problem["solve_outputs"]:
            ok = is_close(entered[out["key"]], out["value"], out["tol"])
            checks.append(ok)
            if ok:
                st.markdown(
                    f"<div class='good'>{out['label']}: correct.</div>",
                    unsafe_allow_html=True,
                )
            else:
                if mode == "Practice":
                    st.markdown(
                        f"<div class='bad'>{out['label']}: not yet. Expected approximately {out['value']:.4f} {out['unit']}.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div class='bad'>{out['label']}: not yet. Check the sign convention and component equations.</div>",
                        unsafe_allow_html=True,
                    )

        if all(checks):
            solved = st.session_state.setdefault("solved", set())
            if problem["id"] not in solved:
                solved.add(problem["id"])
                st.session_state["xp"] = st.session_state.get("xp", 0) + 40
            st.success("Excellent â€” this mechanism is solved correctly.")
        else:
            st.info("Keep going. Review the direction and equation tabs if needed.")


def render_solution_tab(problem, mode):
    st.markdown("## Worked solution")
    if mode == "Self-test":
        if not st.session_state.get(f"reveal_{problem['id']}", False):
            st.warning("Self-test mode hides the worked solution until you choose to reveal it.")
            if st.button("Reveal worked solution", key=f"reveal_btn_{problem['id']}"):
                st.session_state[f"reveal_{problem['id']}"] = True
                st.rerun()
            return

    st.markdown("### Recommended method")
    if problem["topic"] == "Velocity analysis":
        st.markdown("Classify the motion, mark the velocity directions, choose the compatibility relation, and solve the components.")
    else:
        st.markdown("Complete velocity analysis first, then add the tangential and normal acceleration components.")

    if problem.get("vector_lines"):
        st.markdown(r"### Vector extraction in $\mathbf{i}$ and $\mathbf{j}$")
        st.markdown(
            """
            <div class="info">
            This extra step shows how the angled vectors are resolved into x- and y-components
            before the final equations are written.
            </div>
            """,
            unsafe_allow_html=True,
        )
        for line in problem["vector_lines"]:
            st.latex(line)

    st.markdown("### Calculation line-by-line")
    for line in problem["solution_lines"]:
        st.latex(line)

    st.markdown("### Teaching point")
    st.markdown(f"<div class='hint'>{problem['teaching_point']}</div>", unsafe_allow_html=True)


def sidebar_controls():
    st.sidebar.markdown("## Mode")
    mode = st.sidebar.radio(
        "Choose activity",
        ["Practice", "Self-test"],
        help="Practice gives immediate guidance. Self-test hides the worked solution until you reveal it."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Practice setup")
    topic = st.sidebar.radio(
        "Topic",
        ["Velocity analysis", "Acceleration analysis"],
    )
    levels = sorted([p["level"] for p in PROBLEMS if p["topic"] == topic])
    level = st.sidebar.selectbox("Level", levels)
    names = {p["level"]: p["title"] for p in PROBLEMS if p["topic"] == topic}
    st.sidebar.caption(f"Problem: {names[level]}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Progress")
    xp = st.session_state.get("xp", 0)
    solved = st.session_state.get("solved", set())
    badge = "Mechanism Explorer" if xp >= 80 else "Getting started"
    st.sidebar.markdown(f"**XP**  \n{xp}")
    st.sidebar.markdown(f"**Badge**  \n{badge}")
    st.sidebar.markdown(
        "<div class='skill'>Current emphasis: method selection, vector direction, relative motion, and clean component equations.</div>",
        unsafe_allow_html=True,
    )

    return mode, topic, level


render_header()
mode, topic, level = sidebar_controls()
problem = get_problem(topic, level)

tab_learn, tab_problem, tab_dir, tab_eq, tab_solve, tab_solution = st.tabs(
    [
        "0. Learn the topic",
        "1. Problem",
        "2. Direction check",
        "3. Choose equation",
        "4. Solve and check",
        "5. Solution",
    ]
)

with tab_learn:
    render_learn_tab(topic)
with tab_problem:
    render_problem_tab(problem)
with tab_dir:
    render_direction_tab(problem, mode)
with tab_eq:
    render_equation_tab(problem, mode)
with tab_solve:
    render_solve_tab(problem, mode)
with tab_solution:
    render_solution_tab(problem, mode)
