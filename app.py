
import base64
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="MechanismQuest",
    page_icon="⚙️",
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
}

st.markdown(
    """
    <style>
    .stApp{background:#fff}
    .block-container{max-width:1460px;padding-top:1.05rem;padding-bottom:2rem}
    [data-testid="stSidebar"]{background:#eef1f5;border-right:1px solid #dde2e8}
    [data-testid="stSidebar"] .block-container{padding-top:2.8rem}
    header[data-testid="stHeader"]{background:transparent}
    #MainMenu,footer{visibility:hidden}
    .app-header{display:grid;grid-template-columns:230px 1fr 190px;gap:24px;align-items:center;padding:16px 10px 20px}
    .app-header-logo{display:flex;justify-content:center}
    .app-header-logo img{width:210px;max-height:92px;object-fit:contain}
    .app-header-title h1{margin:0;font-size:34px;line-height:1.05;color:#0f172a}
    .app-header-title p{margin:7px 0 0;color:#334155;line-height:1.45;font-size:15px}
    .app-header-author{text-align:right;color:#334155;font-size:13px;line-height:1.5}
    .app-divider{height:1px;background:#d9dee5;margin:2px 0 18px}
    .info{background:#e8f2ff;border-radius:10px;padding:13px 15px;color:#0f4c81;margin:8px 0 16px}
    .hint{background:#ecfdf3;border:1px solid #bbf7d0;border-radius:10px;padding:11px 13px;color:#166534;margin:8px 0 14px}
    .warning{background:#fff8e8;border:1px solid #f3d69b;border-radius:10px;padding:11px 13px;color:#7c4a03;margin:8px 0 14px}
    .card{border:1px solid #dfe4ea;border-radius:10px;padding:14px 16px;margin-bottom:14px;background:#fff}
    .good{background:#ecfdf3;border:1px solid #bbf7d0;color:#166534;border-radius:9px;padding:10px 12px;margin:6px 0}
    .bad{background:#fff1f2;border:1px solid #fecdd3;color:#9f1239;border-radius:9px;padding:10px 12px;margin:6px 0}
    .mini{color:#64748b;font-size:13px}
    .skill{color:#7c8798;font-size:13px;margin-top:10px}
    .legend-row{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;margin-top:4px}
    .legend-chip{display:inline-flex;align-items:center;gap:7px}
    .legend-box{width:18px;height:4px;border-radius:2px;display:inline-block}
    @media(max-width:980px){
      .app-header{grid-template-columns:1fr;text-align:center}
      .app-header-author{text-align:center}
      .app-header-logo img{width:190px}
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
            "ω = 6 rad/s counterclockwise. Determine the speed of point P."
        ),
        "givens": ["r = 0.30 m", "ω = 6 rad/s CCW"],
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
                    "v = αr",
                    "v = ωr",
                    "v = ω²r",
                    "v = r/ω",
                ],
                "correct": "v = ωr",
                "why": "For fixed-axis rotation, the linear speed equals ωr."
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
            "Link AB has length 0.50 m and is inclined 30° above the horizontal. "
            "Point A moves horizontally to the right at 2.0 m/s. Point B is constrained "
            "to move vertically. Determine the angular velocity of the link and the "
            "velocity of B."
        ),
        "givens": ["AB = 0.50 m", "θ = 30°", "v_A = 2.0 m/s right", "B is a vertical slider"],
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
                    "v_B = v_A + α × r_B/A",
                    "v_B = v_A + ω × r_B/A",
                    "v_B = a_A + ω × r_B/A",
                    "v_B = ωr_B/A",
                ],
                "correct": "v_B = v_A + ω × r_B/A",
                "why": "Relative velocity for a rigid body is v_B = v_A + ω × r_B/A."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity ω_AB (CCW positive)", "key": "omegaAB", "value": 8.0, "tol": 0.05, "unit": "rad/s"},
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
        "description": (
            "Link AB is horizontal and pinned at A. Link BC is vertical. Both links have "
            "length 2 m at the instant shown. Slider C moves at 8 m/s down a 45° groove. "
            "Determine the angular velocities of links AB and BC. Use counterclockwise as positive."
        ),
        "givens": ["AB = 2 m", "BC = 2 m", "v_C = 8 m/s down the 45° groove"],
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
                    "Along the 45° groove",
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
                    "v_C = v_B + ω_BC × r_C/B",
                    "a_C = a_B + α_BC × r_C/B - ω_BC² r_C/B",
                    "v_C = ω_BC r_C/B",
                    "v_B = v_C + α_BC × r_C/B",
                ],
                "correct": "v_C = v_B + ω_BC × r_C/B",
                "why": "This is the relative-velocity equation for the moving link BC."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity ω_AB (CCW positive)", "key": "omegaAB", "value": -2.8284, "tol": 0.03, "unit": "rad/s"},
            {"label": "Angular velocity ω_BC (CCW positive)", "key": "omegaBC", "value": 2.8284, "tol": 0.03, "unit": "rad/s"},
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
            "Bar AB has angular velocity ω_AB = 6 rad/s counterclockwise and length AB = 0.200 m. "
            "Link BC has length 0.500 m, and point C is a horizontal slider. Determine the angular "
            "velocity of link BC and the velocity of slider C. Report positive angular velocity as CCW "
            "and positive slider velocity to the right."
        ),
        "givens": ["AB = 0.200 m", "BC = 0.500 m", "ω_AB = 6 rad/s CCW", "C is a horizontal slider"],
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
                    "v = αr",
                    "v = ωr",
                    "v = ω²r",
                    "v = r/ω",
                ],
                "correct": "v = ωr",
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
            "rotates at ω_A = 12 rad/s. Pulley B has radius 0.125 m. Determine the angular velocity of B."
        ),
        "givens": ["r_A = 0.200 m", "r_B = 0.125 m", "ω_A = 12 rad/s", "Open belt, no slip"],
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
                    "ω_A = ω_B",
                    "ω_A / r_A = ω_B / r_B",
                    "ω_A r_A = ω_B r_B",
                    "ω_A r_B = ω_B r_A²",
                ],
                "correct": "ω_A r_A = ω_B r_B",
                "why": "Equal tangential speeds give ω_A r_A = ω_B r_B."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity ω_B", "key": "omegaB", "value": 19.2, "tol": 0.05, "unit": "rad/s"},
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
        "givens": ["N_A = 20", "N_B = 60", "N_C = 30", "N_D = 90", "ω_A = 18 rad/s clockwise"],
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
                "why": "If they are on the same shaft, they rotate together with the same ω."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct gear-speed relationship for one external mesh.",
                "options": [
                    "ω_1 N_1 = ω_2 N_2",
                    "ω_1 / N_1 = ω_2 / N_2",
                    "ω_1 N_2 = ω_2 / N_1",
                    "ω_1 = ω_2 always",
                ],
                "correct": "ω_1 N_1 = ω_2 N_2",
                "why": "Equal tangential speeds at meshing pitch circles give ω_1 r_1 = ω_2 r_2. With proportional tooth counts, ω_1 N_1 = ω_2 N_2."
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
            "A disk rotates about a fixed axis. At point P on the rim, r = 0.30 m, ω = 6 rad/s and "
            "α = 4 rad/s² at the instant shown. Determine the tangential acceleration, normal acceleration, "
            "and resultant acceleration of point P."
        ),
        "givens": ["r = 0.30 m", "ω = 6 rad/s", "α = 4 rad/s²"],
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
                    "a_t = ωr and a_n = αr",
                    "a_t = αr and a_n = ω²r",
                    "a_t = ω²r and a_n = αr",
                    "a_t = v/r and a_n = α²r",
                ],
                "correct": "a_t = αr and a_n = ω²r",
                "why": "Tangential acceleration depends on α, while normal acceleration depends on ω²."
            }
        ],
        "solve_outputs": [
            {"label": "Tangential acceleration a_t", "key": "at", "value": 1.2, "tol": 0.02, "unit": "m/s²"},
            {"label": "Normal acceleration a_n", "key": "an", "value": 10.8, "tol": 0.03, "unit": "m/s²"},
            {"label": "Resultant acceleration |a|", "key": "ares", "value": 10.8665, "tol": 0.03, "unit": "m/s²"},
        ],
        "solution_lines": [
            r"a_t=\alpha r=(4)(0.30)=1.20\ \text{m/s}^2",
            r"a_n=\omega^2 r=(6^2)(0.30)=10.8\ \text{m/s}^2",
            r"|a|=\sqrt{a_t^2+a_n^2}=\sqrt{1.20^2+10.8^2}=10.87\ \text{m/s}^2",
        ],
        "teaching_point": "Even if α were zero, the normal component could still exist because it depends on ω².",
    },
    {
        "id": "A2",
        "topic": "Acceleration analysis",
        "level": 2,
        "title": "Relative acceleration with a vertical slider",
        "difficulty": "Moderate",
        "diagram": "slider_acceleration",
        "description": (
            "Link AB has length 0.50 m and is inclined 30° above the horizontal. Point A moves horizontally "
            "to the right at a constant speed of 1.0 m/s, so a_A = 0. Point B is constrained to move vertically. "
            "Complete the velocity step first, then determine the angular acceleration of the link and the acceleration of B. "
            "Use counterclockwise positive and upward positive."
        ),
        "givens": ["AB = 0.50 m", "θ = 30°", "v_A = 1.0 m/s constant", "a_A = 0", "B is a vertical slider"],
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
                    "The velocity analysis and angular velocity ω",
                    "The moment of inertia",
                    "The work done by the link",
                ],
                "correct": "The velocity analysis and angular velocity ω",
                "why": "The normal term uses ω², so the velocity analysis must be done first."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-acceleration equation.",
                "options": [
                    "a_B = a_A + α × r_B/A - ω² r_B/A",
                    "a_B = v_A + α × r_B/A - ω² r_B/A",
                    "a_B = a_A + ω × r_B/A",
                    "a_B = αr_B/A",
                ],
                "correct": "a_B = a_A + α × r_B/A - ω² r_B/A",
                "why": "For a rigid body in plane motion, acceleration has tangential and normal relative terms."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration α_AB (CCW positive)", "key": "alphaAB", "value": -27.7128, "tol": 0.05, "unit": "rad/s²"},
            {"label": "Acceleration of B (upward positive)", "key": "aB", "value": -16.0, "tol": 0.05, "unit": "m/s²"},
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
            "Wheel A has radius 0.200 m and starts from rest with constant angular acceleration α_A = 3 rad/s². "
            "Pulley B has radius 0.125 m. Determine ω_B, α_B, and the tangential and normal acceleration components "
            "of a point P on the rim of B at t = 3 s."
        ),
        "givens": ["r_A = 0.200 m", "r_B = 0.125 m", "α_A = 3 rad/s²", "ω_A(0)=0", "t = 3 s", "Twisted belt, no slip"],
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
                    "ω_A²r_A = ω_B²r_B",
                    "α_A r_A = α_B r_B",
                    "α_A = α_B",
                    "a_nA = a_nB",
                ],
                "correct": "α_A r_A = α_B r_B",
                "why": "Tangential acceleration is the transferred quantity in a no-slip belt."
            }
        ],
        "solve_outputs": [
            {"label": "Angular speed magnitude of pulley B at t = 3 s", "key": "omegaB", "value": 14.4, "tol": 0.05, "unit": "rad/s"},
            {"label": "Angular acceleration magnitude of pulley B", "key": "alphaB", "value": 4.8, "tol": 0.03, "unit": "rad/s²"},
            {"label": "Tangential acceleration of point P on B", "key": "at", "value": 0.6, "tol": 0.02, "unit": "m/s²"},
            {"label": "Normal acceleration of point P on B", "key": "an", "value": 25.92, "tol": 0.05, "unit": "m/s²"},
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
            "From the velocity step, slider C is known to move down a 45° groove at 8 m/s, giving "
            "ω_AB = -2.828 rad/s and ω_BC = 2.828 rad/s at this instant. If slider C now has acceleration "
            "3.0 m/s² down the same 45° groove, determine the angular accelerations α_AB and α_BC. "
            "Use counterclockwise as positive."
        ),
        "givens": ["AB = 2 m", "BC = 2 m", "ω_AB = -2.828 rad/s", "ω_BC = 2.828 rad/s", "a_C = 3 m/s² down 45° groove"],
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
                    "Because α depends on kinetic energy",
                    "Because the normal terms use the known angular velocities ω",
                    "Because it makes the drawing prettier",
                    "Because only velocity gives the link lengths",
                ],
                "correct": "Because the normal terms use the known angular velocities ω",
                "why": "The normal relative acceleration terms contain ω²."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-acceleration equation for link BC.",
                "options": [
                    "a_C = a_B + α_BC × r_C/B - ω_BC² r_C/B",
                    "a_C = v_B + α_BC × r_C/B - ω_BC² r_C/B",
                    "a_C = a_B + ω_BC × r_C/B",
                    "a_C = α_BC r_C/B only",
                ],
                "correct": "a_C = a_B + α_BC × r_C/B - ω_BC² r_C/B",
                "why": "You need both the tangential and normal relative terms."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration α_AB (CCW positive)", "key": "alphaAB", "value": -9.0607, "tol": 0.04, "unit": "rad/s²"},
            {"label": "Angular acceleration α_BC (CCW positive)", "key": "alphaBC", "value": 9.0607, "tol": 0.04, "unit": "rad/s²"},
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
]


def get_problem(topic, level):
    for prob in PROBLEMS:
        if prob["topic"] == topic and prob["level"] == level:
            return prob
    return None


def vector_legend_html(topic):
    items = [
        ("Known / absolute velocity or acceleration", COLORS["known"]),
        ("Relative velocity", COLORS["relative"]),
        ("Tangential acceleration", COLORS["tangent"]),
        ("Normal acceleration", COLORS["normal"]),
        ("Resultant / final answer", COLORS["resultant"]),
    ]
    chips = "".join(
        f'<span class="legend-chip"><span class="legend-box" style="background:{c}"></span>{label}</span>'
        for label, c in items
    )
    return f'<div class="legend-row">{chips}</div>'


def draw_arrow(ax, start, end, color, label=None, lw=2.2, mutation=14, ls='-'):
    arrow = FancyArrowPatch(
        start, end, arrowstyle='->', mutation_scale=mutation,
        linewidth=lw, color=color, linestyle=ls
    )
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(mx, my + 0.08, label, color=color, fontsize=10, weight='bold',
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))


def finish_axis(ax, xlim, ylim):
    ax.set_aspect('equal')
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis('off')


def draw_fixed_velocity():
    fig, ax = plt.subplots(figsize=(7.3, 3.8))
    center = np.array([0.0, 0.0])
    R = 1.0
    theta = math.radians(50)
    P = np.array([R * math.cos(theta), R * math.sin(theta)])
    ax.add_patch(Circle(center, R, fill=False, linewidth=2.0, edgecolor=COLORS["link"]))
    ax.plot(*center, 'o', color='black', ms=5)
    ax.text(center[0] - 0.08, center[1] - 0.18, "O", fontsize=11, weight="bold")
    ax.plot(*P, 'o', color='black', ms=5)
    ax.text(P[0] + 0.08, P[1] + 0.02, "P", fontsize=11, weight="bold")
    ax.plot([center[0], P[0]], [center[1], P[1]], color=COLORS["guide"], linewidth=2)
    ax.text(0.38, 0.42, "r", color=COLORS["guide"], fontsize=10)
    tangent = np.array([-math.sin(theta), math.cos(theta)])
    draw_arrow(ax, P, P + 0.55 * tangent, COLORS["known"], r"$v_P$")
    arc = np.linspace(math.radians(310), math.radians(20), 80)
    ax.plot(0.33 * np.cos(arc), 0.33 * np.sin(arc), color=COLORS["relative"], linewidth=2)
    draw_arrow(ax, (0.33 * math.cos(math.radians(20)), 0.33 * math.sin(math.radians(20))),
               (0.35 * math.cos(math.radians(12)), 0.35 * math.sin(math.radians(12))),
               COLORS["relative"], r"$\omega$", lw=2)
    finish_axis(ax, (-1.35, 1.95), (-1.2, 1.35))
    return fig


def draw_fixed_acceleration():
    fig, ax = plt.subplots(figsize=(7.3, 3.8))
    center = np.array([0.0, 0.0])
    R = 1.0
    theta = math.radians(55)
    P = np.array([R * math.cos(theta), R * math.sin(theta)])
    ax.add_patch(Circle(center, R, fill=False, linewidth=2.0, edgecolor=COLORS["link"]))
    ax.plot(*center, 'o', color='black', ms=5)
    ax.text(center[0] - 0.08, center[1] - 0.18, "O", fontsize=11, weight="bold")
    ax.plot(*P, 'o', color='black', ms=5)
    ax.text(P[0] + 0.08, P[1] + 0.04, "P", fontsize=11, weight="bold")
    ax.plot([center[0], P[0]], [center[1], P[1]], color=COLORS["guide"], linewidth=2)
    tangent = np.array([-math.sin(theta), math.cos(theta)])
    radial_in = center - P
    radial_in = radial_in / np.linalg.norm(radial_in)
    draw_arrow(ax, P, P + 0.55 * tangent, COLORS["tangent"], r"$a_t$")
    draw_arrow(ax, P, P + 0.62 * radial_in, COLORS["normal"], r"$a_n$")
    resultant = 0.18 * tangent + 0.95 * radial_in
    draw_arrow(ax, P, P + 0.72 * resultant, COLORS["resultant"], r"$a$")
    finish_axis(ax, (-1.35, 2.05), (-1.25, 1.35))
    return fig


def draw_slider_velocity(accel=False):
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    A = np.array([0.4, 0.5])
    L = 2.5
    theta = math.radians(30)
    B = A + L * np.array([math.cos(theta), math.sin(theta)])
    # slider
    ax.plot([B[0]-0.25, B[0]-0.25], [B[1]-1.1, B[1]+1.1], color=COLORS["guide"], lw=2)
    ax.plot([B[0]+0.25, B[0]+0.25], [B[1]-1.1, B[1]+1.1], color=COLORS["guide"], lw=2)
    ax.add_patch(Rectangle((B[0]-0.18, B[1]-0.26), 0.36, 0.52, fill=False, ec=COLORS["link"], lw=2))
    # link
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=2.4)
    ax.plot(*A, 'o', color='black', ms=6)
    ax.plot(*B, 'o', color='black', ms=6)
    ax.text(A[0]-0.12, A[1]-0.28, "A", fontsize=11, weight='bold')
    ax.text(B[0]+0.12, B[1]+0.05, "B", fontsize=11, weight='bold')
    ax.text((A[0]+B[0])/2-0.1, (A[1]+B[1])/2+0.20, "AB", color=COLORS["link"], fontsize=10)
    draw_arrow(ax, A + np.array([-0.05, 0.38]), A + np.array([0.95, 0.38]), COLORS["known"], r"$v_A$")
    if not accel:
        draw_arrow(ax, B + np.array([0.55, -0.15]), B + np.array([0.55, 1.0]), COLORS["known"], r"$v_B$")
        mid = (A + B) / 2
        perp = np.array([-math.sin(theta), math.cos(theta)])
        draw_arrow(ax, mid + np.array([0.18, -0.22]), mid + np.array([0.18, -0.22]) + 0.9 * perp, COLORS["relative"], r"$v_{B/A}$")
    else:
        draw_arrow(ax, B + np.array([0.62, 0.12]), B + np.array([0.62, -0.95]), COLORS["known"], r"$a_B$")
        mid = (A + B) / 2
        perp = np.array([-math.sin(theta), math.cos(theta)])
        toward_A = (A - B) / np.linalg.norm(A - B)
        draw_arrow(ax, mid + np.array([0.30, 0.05]), mid + np.array([0.30, 0.05]) + 0.82 * perp, COLORS["tangent"], r"$a^t_{B/A}$")
        draw_arrow(ax, B + np.array([-0.08, -0.05]), B + np.array([-0.08, -0.05]) + 0.9 * toward_A, COLORS["normal"], r"$a^n_{B/A}$")
    ax.text(A[0]+0.55, A[1]-0.38, r"$30^\circ$", fontsize=10)
    finish_axis(ax, (-0.35, 3.65), (-0.35, 2.8))
    return fig


def draw_linked_velocity(accel=False):
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    A = np.array([0.8, 3.1])
    B = np.array([3.6, 3.1])
    C = np.array([3.6, 0.5])

    # 45-degree groove
    ax.plot([2.2, 5.4], [1.9, -1.3], color=COLORS["guide"], lw=2)
    ax.plot([2.45, 5.65], [2.15, -1.05], color=COLORS["guide"], lw=2)
    ax.text(4.55, -0.75, "45° groove", fontsize=10, color=COLORS["construct"])

    # links
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=2.8)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS["link"], lw=2.8)

    # joints
    for pt, lab, dx, dy in [(A, "A", -0.14, 0.14), (B, "B", 0.08, 0.12), (C, "C", 0.08, -0.08)]:
        ax.plot(*pt, 'o', color='black', ms=8)
        ax.text(pt[0]+dx, pt[1]+dy, lab, fontsize=12, weight='bold')

    # dimensions
    ax.text(2.05, 3.35, "AB = 2 m", fontsize=11, color=COLORS["link"])
    ax.text(3.82, 1.85, "BC = 2 m", fontsize=11, color=COLORS["link"], rotation=90, va='center')

    if not accel:
        draw_arrow(ax, B + np.array([0.62, 0.10]), B + np.array([0.62, -1.10]), COLORS["known"], r"$v_B$")
        draw_arrow(ax, C + np.array([0.18, -0.04]), C + np.array([1.20, -1.06]), COLORS["known"], r"$v_C$")
        # relative velocity perpendicular to BC, drawn clearly to the left
        draw_arrow(ax, np.array([2.35, 1.80]), np.array([1.45, 1.80]), COLORS["relative"], r"$v_{C/B}$")
    else:
        draw_arrow(ax, B + np.array([0.62, 0.12]), B + np.array([0.62, -1.10]), COLORS["known"], r"$a_B$")
        draw_arrow(ax, C + np.array([0.20, -0.04]), C + np.array([1.18, -1.02]), COLORS["known"], r"$a_C$")
        # Tangential component leftward and separate
        draw_arrow(ax, np.array([3.00, 2.05]), np.array([2.05, 2.05]), COLORS["tangent"], r"$a^t_{C/B}$")
        # Normal component upward, toward B
        draw_arrow(ax, np.array([2.40, 1.05]), np.array([2.40, 1.95]), COLORS["normal"], r"$a^n_{C/B}$")
        ax.text(1.82, 2.32, "tangential", fontsize=8.8, color=COLORS["tangent"])
        ax.text(2.48, 2.05, "toward B", fontsize=8.8, color=COLORS["normal"])

    finish_axis(ax, (0.1, 6.1), (-1.35, 3.8))
    return fig


def draw_ic_velocity():
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    A = np.array([0.8, 0.5])
    B = A + 1.8 * np.array([math.cos(math.radians(45)), math.sin(math.radians(45))])
    C = B + 2.8 * np.array([math.cos(math.radians(-30)), math.sin(math.radians(-30))])

    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=2.7)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS["link"], lw=2.7)

    ax.plot([C[0]-1.0, C[0]+0.7], [C[1]-0.22, C[1]-0.22], color=COLORS["guide"], lw=2)
    ax.plot([C[0]-1.0, C[0]+0.7], [C[1]+0.22, C[1]+0.22], color=COLORS["guide"], lw=2)
    ax.add_patch(Rectangle((C[0]-0.23, C[1]-0.16), 0.46, 0.32, fill=False, ec=COLORS["link"], lw=2))
    ax.text(C[0]-0.6, C[1]+0.38, "horizontal slider", fontsize=9, color=COLORS["construct"])

    for pt, lab, dx, dy in [(A, "A", -0.12, -0.24), (B, "B", 0.07, 0.08), (C, "C", 0.06, 0.22)]:
        ax.plot(*pt, 'o', color='black', ms=7)
        ax.text(pt[0]+dx, pt[1]+dy, lab, fontsize=12, weight='bold')

    ax.text((A[0]+B[0])/2-0.18, (A[1]+B[1])/2+0.24, "AB = 0.200 m", fontsize=10, color=COLORS["link"])
    ax.text((B[0]+C[0])/2-0.05, (B[1]+C[1])/2+0.28, "BC = 0.500 m", fontsize=10, color=COLORS["link"])

    draw_arrow(ax, B + np.array([0.02, 0.02]), B + np.array([-0.88, 0.88]), COLORS["known"], r"$v_B$")
    draw_arrow(ax, C + np.array([0.0, 0.30]), C + np.array([-1.15, 0.30]), COLORS["known"], r"$v_C$")

    ax.plot([C[0], C[0]], [C[1]-2.8, C[1]+1.2], color=COLORS["construct"], lw=1.9, ls='--')
    xline = np.array([B[0]-2.0, B[0]+1.6])
    yline = B[1] + 1 * (xline - B[0])
    ax.plot(xline, yline, color=COLORS["construct"], lw=1.9, ls='--')
    IC = np.array([C[0], B[1] + (C[0]-B[0])])

    ax.plot(*IC, 'o', color='black', ms=6)
    ax.text(IC[0]+0.10, IC[1]+0.02, "IC", fontsize=11.5, weight='bold', color=COLORS["construct"])
    ax.text(C[0]+0.12, IC[1]-0.25, "line ⟂ to slider velocity", fontsize=8.6, color=COLORS["construct"])
    ax.text(B[0]-1.1, B[1]+1.15, "line ⟂ to $v_B$", fontsize=8.6, color=COLORS["construct"])

    ax.plot([IC[0], B[0]], [IC[1], B[1]], color=COLORS["guide"], lw=1.9)
    ax.plot([IC[0], C[0]], [IC[1], C[1]], color=COLORS["guide"], lw=1.9)
    ax.text((IC[0]+B[0])/2-0.28, (IC[1]+B[1])/2+0.10, r"$r_{B/IC}$", fontsize=9.5, color=COLORS["guide"])
    ax.text(IC[0]+0.10, (IC[1]+C[1])/2, r"$r_{C/IC}$", fontsize=9.5, color=COLORS["guide"])

    finish_axis(ax, (-0.1, 6.2), (-1.35, 4.2))
    return fig


def draw_belt_velocity(accel=False):
    fig, ax = plt.subplots(figsize=(8.8, 4.5))
    A = np.array([2.0, 2.2]); rA = 0.82
    B = np.array([6.2, 2.2]); rB = 0.52

    ax.add_patch(Circle(A, rA, fill=False, ec=COLORS["link"], lw=2.4))
    ax.add_patch(Circle(B, rB, fill=False, ec=COLORS["link"], lw=2.4))
    ax.text(A[0]-0.10, A[1]-0.08, "A", fontsize=12, weight='bold')
    ax.text(B[0]-0.10, B[1]-0.08, "B", fontsize=12, weight='bold')
    ax.text(A[0]-0.95, A[1]+1.08, r"$r_A$", fontsize=10, color=COLORS["link"])
    ax.text(B[0]+0.58, B[1]+0.74, r"$r_B$", fontsize=10, color=COLORS["link"])

    if not accel:
        # Open belt: same rotation direction
        topA = A + np.array([0.0, rA]); topB = B + np.array([0.0, rB])
        botA = A + np.array([0.0, -rA]); botB = B + np.array([0.0, -rB])
        ax.plot([topA[0], topB[0]], [topA[1], topB[1]], color=COLORS["guide"], lw=2.6)
        ax.plot([botA[0], botB[0]], [botA[1], botB[1]], color=COLORS["guide"], lw=2.6)
        ax.text(3.55, 3.35, "open belt", fontsize=10.2, color=COLORS["construct"])
        ax.text(3.25, 3.05, "same belt speed  v = ω_A r_A = ω_B r_B", fontsize=9.2, color=COLORS["construct"])
        ax.text(3.55, 0.82, "same rotation direction", fontsize=9.0, color=COLORS["construct"])
        draw_arrow(ax, np.array([3.25, 3.00]), np.array([4.35, 3.00]), COLORS["relative"], None, lw=2.0)
        draw_arrow(ax, np.array([4.95, 1.32]), np.array([3.85, 1.32]), COLORS["relative"], None, lw=2.0)
        angB = np.linspace(math.radians(250), math.radians(40), 90)
    else:
        # Crossed belt: opposite rotation direction
        ax.plot([A[0], B[0]], [A[1]+rA, B[1]-rB], color=COLORS["guide"], lw=2.6)
        ax.plot([A[0], B[0]], [A[1]-rA, B[1]+rB], color=COLORS["guide"], lw=2.6)
        ax.text(3.45, 3.40, "crossed belt", fontsize=10.2, color=COLORS["construct"])
        ax.text(3.00, 3.10, "same belt speed  v = ω_A r_A = ω_B r_B", fontsize=9.2, color=COLORS["construct"])
        ax.text(3.35, 0.72, "opposite rotation direction", fontsize=9.0, color=COLORS["construct"])
        draw_arrow(ax, np.array([3.10, 3.00]), np.array([4.30, 2.18]), COLORS["relative"], None, lw=2.0)
        draw_arrow(ax, np.array([4.95, 1.28]), np.array([3.75, 2.08]), COLORS["relative"], None, lw=2.0)
        angB = np.linspace(math.radians(130), math.radians(-160), 90)

    # rotation arrows
    angA = np.linspace(math.radians(250), math.radians(40), 90)
    ax.plot(A[0]+0.52*np.cos(angA), A[1]+0.52*np.sin(angA), color=COLORS["known"], lw=2)
    draw_arrow(ax,
               (A[0]+0.52*math.cos(math.radians(40)), A[1]+0.52*math.sin(math.radians(40))),
               (A[0]+0.57*math.cos(math.radians(28)), A[1]+0.57*math.sin(math.radians(28))),
               COLORS["known"], r"$\omega_A$", lw=2)
    ax.plot(B[0]+0.34*np.cos(angB), B[1]+0.34*np.sin(angB), color=COLORS["resultant"], lw=2)
    draw_arrow(ax,
               (B[0]+0.34*math.cos(angB[-2]), B[1]+0.34*math.sin(angB[-2])),
               (B[0]+0.38*math.cos(angB[-1]), B[1]+0.38*math.sin(angB[-1])),
               COLORS["resultant"], r"$\omega_B$", lw=2)

    if accel:
        P = np.array([B[0], B[1]+rB])
        ax.plot(*P, 'o', color='black', ms=5)
        ax.text(P[0]+0.12, P[1]+0.06, "P", fontsize=10, weight='bold')
        draw_arrow(ax, P + np.array([0.10, 0.02]), P + np.array([0.92, 0.02]), COLORS["tangent"], r"$a_t$")
        draw_arrow(ax, P + np.array([0.0, -0.04]), P + np.array([0.0, -0.84]), COLORS["normal"], r"$a_n$")
        ax.text(5.25, 0.30, r"normal part = $v^2/r$, so it differs for different radii", fontsize=8.4, color=COLORS["construct"])

    finish_axis(ax, (0.5, 7.4), (0.15, 4.0))
    return fig


def draw_gear_train():
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    centers = {
        "A": np.array([1.3, 3.2]),
        "B": np.array([3.8, 3.2]),
        "C": np.array([3.8, 1.2]),
        "D": np.array([6.8, 1.2]),
    }
    radii = {"A": 0.55, "B": 1.05, "C": 0.65, "D": 1.25}

    for name in ["A", "B", "C", "D"]:
        c = centers[name]
        r = radii[name]
        ax.add_patch(Circle(c, r, fill=False, ec=COLORS["link"], lw=2.4))
        ax.text(c[0]-0.10, c[1]-0.08, name, fontsize=12, weight='bold')

    # same shaft between B and C
    ax.plot([3.8, 3.8], [2.12, 2.28], color='black', lw=3.2)
    ax.text(4.22, 2.18, "same shaft", fontsize=9.5, color=COLORS["construct"])

    # mesh labels, spaced away
    ax.text(2.40, 4.15, "A meshes with B", fontsize=9.2, color=COLORS["construct"])
    ax.text(5.30, 2.18, "C meshes with D", fontsize=9.2, color=COLORS["construct"])

    # direction arrows
    draw_arrow(ax, centers["A"] + np.array([0.0, 0.70]), centers["A"] + np.array([0.40, 0.18]), COLORS["known"], r"$\omega_A$", lw=2)
    draw_arrow(ax, centers["D"] + np.array([0.0, 1.35]), centers["D"] + np.array([0.42, 0.78]), COLORS["resultant"], r"$\omega_D$", lw=2)

    # teeth counts below circles, clear and non-overlapping
    ax.text(0.95, 2.25, "20 teeth", fontsize=9.3, color=COLORS["link"])
    ax.text(3.35, 1.85, "60 teeth", fontsize=9.3, color=COLORS["link"])
    ax.text(4.65, 0.05, "30 teeth", fontsize=9.3, color=COLORS["link"])
    ax.text(7.20, -0.12, "90 teeth", fontsize=9.3, color=COLORS["link"])

    # notes on directions
    ax.text(2.10, 0.10, "External gears reverse direction; gears on the same shaft share the same ω.", fontsize=8.7, color=COLORS["construct"])

    finish_axis(ax, (0.2, 8.1), (-0.35, 4.7))
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
    else:
        fig, _ = plt.subplots()
    st.pyplot(fig, clear_figure=True)


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
                """
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
                """
                - **Pure translation** → every point has the **same velocity vector**.  
                - **Fixed-axis rotation** → use \(v=\omega r\) at each point.  
                - **Two points on one moving link** → use the **relative-velocity equation**.  
                - **Slider-link with known directions** → the **IC method** is often fastest for velocity only.  
                - **Belts / pulleys** → use **equal tangential belt speed**.  
                - **Gears** → use **equal pitch-line speed** and the correct direction reversal.  
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
                """
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
                """
                - Tangential acceleration \(a_t\) is **perpendicular** to the radius or link.  
                - Normal acceleration \(a_n\) points **toward the centre / base point**.  
                - For a link \(AB\), the relative normal acceleration of \(B\) with respect to \(A\) points **from B toward A**.  
                - Slider acceleration must lie **along the guide**.  
                """
            )

        with col2:
            st.markdown("### Big teaching idea")
            st.markdown(
                """
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
                """
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
                """
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
        st.markdown(
            "<div class='hint'><b>Given values</b><br>" + "<br>".join(f"• {g}" for g in problem["givens"]) + "</div>",
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
            st.success("Excellent — this mechanism is solved correctly.")
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
        st.markdown("### Vector extraction in $\mathbf{i}$ and $\mathbf{j}$")
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
