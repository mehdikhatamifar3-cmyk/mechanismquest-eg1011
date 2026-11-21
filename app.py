
# -*- coding: ascii -*-
"""MechanismQuest: encoding-proof Streamlit application.

All source text is ASCII. User-facing Unicode is produced only by explicit
Unicode escapes, HTML entities, or LaTeX commands.
"""

import base64
import math
from pathlib import Path


def _mojibake_markers():
    """Return common UTF-8-as-Windows-1252 corruption fragments."""
    return (
        "\u00c2", "\u00c3", "\u00ce", "\u00cf", "\u00e2\u20ac",
        "\u00e2\u0161", "\u00ef\u00b8", "\ufffd",
    )


def _find_text_corruption(value, path="root"):
    """Recursively find mojibake, replacement characters, and C1 controls."""
    findings = []
    if isinstance(value, str):
        for marker in _mojibake_markers():
            if marker in value:
                findings.append(path + ": marker " + repr(marker))
        if any(0x80 <= ord(ch) <= 0x9F for ch in value):
            findings.append(path + ": C1 control character")
    elif isinstance(value, dict):
        for key, item in value.items():
            findings.extend(_find_text_corruption(key, path + ".key"))
            findings.extend(_find_text_corruption(item, path + "[" + repr(key) + "]"))
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            findings.extend(_find_text_corruption(item, path + "[" + str(index) + "]"))
    return findings


def startup_source_sanitisation_check():
    """Fail fast if the deployed source is not strict ASCII or contains mojibake."""
    raw = Path(__file__).read_bytes()
    try:
        source_text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            "Encoding safety check failed: app.py contains a raw non-ASCII byte "
            "at offset " + str(exc.start) + ". Deploy the supplied ASCII-only file."
        ) from exc
    findings = _find_text_corruption(source_text, "app.py")
    if findings:
        raise RuntimeError("Encoding safety check failed: " + "; ".join(findings[:8]))
    return True


startup_source_sanitisation_check()

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="MechanismQuest",
    page_icon="\u2699\ufe0f",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent


def load_logo_b64():
    """Load the optional JCU logo without preventing the app from starting."""
    logo_path = APP_DIR / "assets" / "jcu_logo.png"
    if not logo_path.is_file():
        return ""
    return base64.b64encode(logo_path.read_bytes()).decode("ascii")


LOGO_B64 = load_logo_b64()
APP_BUILD_ID = "science-and-diagram-review-2026-11-21-r6"

# Mechanics references checked during the scientific review:
# https://mechref.engr.illinois.edu/dyn/rkg.html
# https://mechanicsmap.psu.edu/websites/12_rigid_body_kinematics/12-3_belt_and_gear_driven_systems/belt_and_gear_driven_systems.html
# All examples assume planar rigid links, ideal pins, fixed straight slider
# guides, fixed pulley/gear centres, and inextensible belts without slip.

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
    .logo-fallback { color:#0f172a; text-align:center; line-height:1.25; }
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
    div[data-testid="stRadio"] span { color:#0f172a !important; }

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
    logo_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" alt="JCU">'
        if LOGO_B64
        else '<div class="logo-fallback"><b>JCU</b><br>James Cook University</div>'
    )
    st.markdown(
        f"""
        <div class="app-header">
          <div class="app-header-logo">{logo_html}</div>
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


_MATH_TOKEN_PATTERNS = (
    # Longest and most specific expressions first.
    ("v_B = v_A + \u03c9 \u00d7 r_B/A", r"\mathbf{v}_B=\mathbf{v}_A+\boldsymbol\omega\times\mathbf{r}_{B/A}"),
    ("\u03c9_A r_A = \u03c9_B r_B", r"\omega_A r_A=\omega_B r_B"),
    ("\u03c9_1 r_1 = \u03c9_2 r_2", r"\omega_1 r_1=\omega_2 r_2"),
    ("\u03c9_1 N_1 = \u03c9_2 N_2", r"\omega_1 N_1=\omega_2 N_2"),
    ("a_t = \u03b1r and a_n = \u03c9\u00b2r", r"a_t=\alpha r\quad\text{and}\quad a_n=\omega^2r"),
    (r"-omega_BC squared times r_C/B", r"-\omega_{BC}^{2}\mathbf{r}_{C/B}"),
    ("a_n(C/B)", r"\mathbf{a}^{n}_{C/B}"),
    (r"v_B/A", r"\mathbf{v}_{B/A}"),
    (r"v_C/B", r"\mathbf{v}_{C/B}"),
    (r"a_B/A", r"\mathbf{a}_{B/A}"),
    (r"a_C/B", r"\mathbf{a}_{C/B}"),
    (r"r_B/A", r"\mathbf{r}_{B/A}"),
    (r"r_C/B", r"\mathbf{r}_{C/B}"),
    ("\u03c9r", r"\omega r"),
    ("\u03b1r", r"\alpha r"),
    ("\u03c9\u00b2r", r"\omega^{2}r"),
    ("\u03b1\u00b2r", r"\alpha^{2}r"),
    ("\u03c9_BC\u00b2", r"\omega_{BC}^{2}"),
    ("\u03c9_AB\u00b2", r"\omega_{AB}^{2}"),
    ("\u03b1_BC\u00b2", r"\alpha_{BC}^{2}"),
    ("\u03b1_AB\u00b2", r"\alpha_{AB}^{2}"),
    ("\u03c9_A\u00b2", r"\omega_A^{2}"),
    ("\u03c9_B\u00b2", r"\omega_B^{2}"),
    ("\u03b1_A\u00b2", r"\alpha_A^{2}"),
    ("\u03b1_B\u00b2", r"\alpha_B^{2}"),
    ("\u03c9\u00b2", r"\omega^{2}"),
    ("\u03b1\u00b2", r"\alpha^{2}"),
    ("\u03c9_AB", r"\omega_{AB}"),
    ("\u03c9_BC", r"\omega_{BC}"),
    ("\u03b1_AB", r"\alpha_{AB}"),
    ("\u03b1_BC", r"\alpha_{BC}"),
    ("\u03c9_A", r"\omega_A"),
    ("\u03c9_B", r"\omega_B"),
    ("\u03c9_C", r"\omega_C"),
    ("\u03c9_D", r"\omega_D"),
    ("\u03b1_A", r"\alpha_A"),
    ("\u03b1_B", r"\alpha_B"),
    (r"v_B", r"\mathbf{v}_B"),
    (r"v_C", r"\mathbf{v}_C"),
    (r"v_A", r"\mathbf{v}_A"),
    (r"v_P", r"\mathbf{v}_P"),
    (r"a_B", r"\mathbf{a}_B"),
    (r"a_C", r"\mathbf{a}_C"),
    (r"a_A", r"\mathbf{a}_A"),
    (r"a_P", r"\mathbf{a}_P"),
    (r"a_t", r"a_t"),
    (r"a_n", r"a_n"),
    (r"s_C", r"s_C"),
    ("\u00d7", r"\times"),
    ("\u03c9", r"\omega"),
    ("\u03b1", r"\alpha"),
    ("\u03b8", r"\theta"),
)


def _outside_math_transform(text, transform):
    """Apply a transform only outside existing dollar-delimited math spans."""
    parts = str(text).split("$")
    for index in range(0, len(parts), 2):
        parts[index] = transform(parts[index])
    return "$".join(parts)


def _replace_math_tokens(text):
    """Replace plain student-facing variable names with rendered inline LaTeX."""
    import re

    def transform(segment):
        protected = []
        protected_latex = []

        def protect(match):
            protected.append(match.group(0))
            return "@@MATH" + str(len(protected) - 1) + "@@"

        def protect_latex(value):
            protected_latex.append(value)
            return "@@LATEX" + str(len(protected_latex) - 1) + "@@"

        quantity_pattern = re.compile(
            r"(?<![A-Za-z0-9_])"
            r"(?:AB|BC|[rNvasta](?:_[A-Za-z0-9/]+)?(?:\(0\))?|[\u03c9\u03b1\u03b8](?:_[A-Za-z0-9]+)?(?:\u00b2)?)"
            r"\s*=\s*[-+]?\d+(?:\.\d+)?"
            r"(?:\s*(?:m/s\u00b2|rad/s\u00b2|m/s|rad/s|m|s|\u00b0))?"
        )
        segment = quantity_pattern.sub(protect, segment)
        number_unit_pattern = re.compile(
            r"(?<![A-Za-z0-9])[-+]?\d+(?:\.\d+)?\s*(?:m/s\u00b2|rad/s\u00b2|m/s|rad/s|m|s)"
        )
        segment = number_unit_pattern.sub(protect, segment)
        segment = re.sub(r"(?<![A-Za-z0-9])[-+]?\d+(?:\.\d+)?\u00b0", protect, segment)

        for plain, latex in _MATH_TOKEN_PATTERNS:
            pattern = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(plain) + r"(?![A-Za-z0-9_])")
            segment = pattern.sub(lambda _m, value=latex: protect_latex(value), segment)

        for plain, latex in {
            "\u03c9r": r"\omega r", "\u03b1r": r"\alpha r", "v\u00b2/r": r"v^{2}/r",
            "+x": r"+x", "+y": r"+y", "-x": r"-x", "+s_C": r"+s_C",
        }.items():
            segment = segment.replace(plain, "$" + latex + "$")

        for index, original in enumerate(protected):
            latex = original.replace("\u03c9", r"\omega").replace("\u03b1", r"\alpha").replace("\u03b8", r"\theta")
            latex = latex.replace("\u00b2", "^{2}").replace("\u00b0", "^{\\circ}")
            latex = re.sub(r"(\\(?:omega|alpha|theta)|[rNvasa])_([A-Za-z0-9/]+)", r"\1_{\2}", latex)
            # A numeric given such as v_A = 2 m/s is a scalar speed/component.
            # Vector equations are formatted separately below.
            latex = re.sub(
                r"(?<![A-Za-z])r_\{([A-Z]/[A-Z])\}",
                lambda match: r"\mathbf{r}_{" + match.group(1) + "}",
                latex,
            )
            latex = re.sub(
                r"\s+(m/s\^\{2\}|rad/s\^\{2\}|m/s|rad/s|m|s)$",
                lambda match: r"\ \mathrm{" + match.group(1) + "}",
                latex,
            )
            segment = segment.replace("@@MATH" + str(index) + "@@", "$" + latex + "$")
        for index, latex in enumerate(protected_latex):
            segment = segment.replace("@@LATEX" + str(index) + "@@", "$" + latex + "$")
        return segment

    return _outside_math_transform(text, transform)


def format_math_text(text):
    """Return Streamlit Markdown with every student-facing formula rendered."""
    return _replace_math_tokens(str(text))


def equation_markdown(text):
    """Render an equation-choice string as one LaTeX expression."""
    import re

    value = str(text)
    suffix = ""
    for phrase in (" always", " only"):
        if value.endswith(phrase):
            value = value[:-len(phrase)]
            suffix = r"\quad\text{" + phrase.strip() + "}"
            break
    value = value.replace(" and ", r"\quad\text{and}\quad ")
    value = value.replace("\u03c9", r"\omega").replace("\u03b1", r"\alpha").replace("\u03b8", r"\theta")
    value = value.replace("\u00d7", r"\times").replace("\u00b2", "^{2}")
    value = re.sub(r"(\\(?:omega|alpha|theta)|[varkNs])_([A-Za-z0-9/]+)", r"\1_{\2}", value)
    value = re.sub(
        r"(?<![A-Za-z])([va])_\{([A-Z](?:/[A-Z])?)\}",
        lambda match: r"\mathbf{" + match.group(1) + "}_{" + match.group(2) + "}",
        value,
    )
    value = re.sub(
        r"(?<![A-Za-z])([va])_([A-Z](?:/[A-Z])?)",
        lambda match: r"\mathbf{" + match.group(1) + "}_{" + match.group(2) + "}",
        value,
    )
    value = re.sub(
        r"(?<![A-Za-z])r_\{([A-Z]/[A-Z])\}",
        lambda match: r"\mathbf{r}_{" + match.group(1) + "}",
        value,
    )
    value = re.sub(
        r"(\\(?:omega|alpha|theta))(?=[A-Za-z])",
        lambda match: match.group(1) + " ",
        value,
    )
    value = re.sub(
        r"(\\(?:omega|alpha))(\_\{[^}]+\})?(?=\s*\\times)",
        lambda match: r"\boldsymbol{" + match.group(1) + "}" + (match.group(2) or ""),
        value,
    )
    return "$" + value + suffix + "$"


def _display_options(options, equation=False):
    formatter = equation_markdown if equation else format_math_text
    return [formatter(option) for option in options]


def render_given_values(givens):
    """Use Markdown rather than raw HTML so subscripts and units render."""
    with st.container(border=True):
        st.markdown("**Given values**")
        for given in givens:
            st.markdown("- " + format_math_text(given))


def unit_markdown(unit):
    value = str(unit).replace("\u00b2", "^2")
    return r"$\mathrm{" + value + "}$"


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
            "\u03c9 = 6 rad/s counterclockwise. Determine the speed of point P."
        ),
        "givens": ["r = 0.30 m", "\u03c9 = 6 rad/s CCW"],
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
                    "v = \u03b1r",
                    "v = |\u03c9|r",
                    "v = \u03c9\u00b2r",
                    "v = r/\u03c9",
                ],
                "correct": "v = |\u03c9|r",
                "why": r"For fixed-axis rotation, speed is $v=|\omega|r$."
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
            "Link AB has length 0.50 m and is inclined 30\u00b0 above the horizontal. "
            "Point A moves horizontally to the right at 2.0 m/s. Point B is constrained "
            "to move vertically. Determine the angular velocity of the link and the "
            "velocity of B."
        ),
        "givens": ["AB = 0.50 m", "\u03b8 = 30\u00b0", "v_A = 2.0 m/s right", "B is a vertical slider"],
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
                    "v_B = v_A + \u03b1 \u00d7 r_B/A",
                    "v_B = v_A + \u03c9 \u00d7 r_B/A",
                    "v_B = a_A + \u03c9 \u00d7 r_B/A",
                    "v_B = \u03c9r_B/A",
                ],
                "correct": "v_B = v_A + \u03c9 \u00d7 r_B/A",
                "why": "Relative velocity for a rigid body is v_B = v_A + \u03c9 \u00d7 r_B/A."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity \u03c9_AB (CCW positive)", "key": "omegaAB", "value": 8.0, "tol": 0.05, "unit": "rad/s"},
            {"label": "Velocity of B (upward positive)", "key": "vB", "value": 2.0 * math.sqrt(3.0), "tol": 0.03, "unit": "m/s"},
        ],
        "vector_lines": [
            r"\mathbf{r}_{B/A}=0.50(\cos30^\circ\,\mathbf{i}+\sin30^\circ\,\mathbf{j})=(0.433\,\mathbf{i}+0.250\,\mathbf{j})\ \text{m}",
            r"\omega_{AB}\mathbf{k}\times\mathbf{r}_{B/A}=\omega_{AB}\mathbf{k}\times(0.433\mathbf{i}+0.250\mathbf{j})=(-0.250\omega_{AB})\mathbf{i}+(0.433\omega_{AB})\mathbf{j}",
        ],
        "solution_lines": [
            r"\mathbf{r}_{B/A}=0.50(\cos30^\circ\,\mathbf{i}+\sin30^\circ\,\mathbf{j})=(0.433\,\mathbf{i}+0.250\,\mathbf{j})\ \text{m}",
            r"\mathbf{v}_B=\mathbf{v}_A+\omega_{AB}\mathbf{k}\times\mathbf{r}_{B/A}",
            r"\mathbf{v}_B=(2\,\mathbf{i})+( -0.25\omega_{AB}\,\mathbf{i}+0.433\omega_{AB}\,\mathbf{j} )",
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
            "length 2 m at the instant shown. Slider C moves at 8 m/s down a 45\u00b0 groove. "
            "Determine the angular velocities of links AB and BC. Use counterclockwise as positive."
        ),
        "givens": ["AB = 2 m", "BC = 2 m", "v_C = 8 m/s down the 45\u00b0 groove"],
        "direction_questions": [
            {
                "q": "What is the direction of velocity of point B from the rotation of AB?",
                "options": [
                    "Horizontal",
                    "Vertical",
                    "Along AB",
                    "Down the 45\u00b0 groove",
                ],
                "correct": "Vertical",
                "why": "B moves perpendicular to AB, and AB is horizontal."
            },
            {
                "q": "What is the direction of the relative velocity v_C/B on link BC?",
                "options": [
                    "Along BC",
                    "Perpendicular to BC",
                    "Along the 45\u00b0 groove",
                    "Zero relative velocity at every instant",
                ],
                "correct": "Perpendicular to BC",
                "why": "Relative velocity due to rotation is perpendicular to the link."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct vector equation for link BC.",
                "options": [
                    "v_C = v_B + \u03c9_BC \u00d7 r_C/B",
                    "a_C = a_B + \u03b1_BC \u00d7 r_C/B - \u03c9_BC\u00b2 r_C/B",
                    "v_C = \u03c9_BC r_C/B",
                    "v_B = v_C + \u03b1_BC \u00d7 r_C/B",
                ],
                "correct": "v_C = v_B + \u03c9_BC \u00d7 r_C/B",
                "why": "This is the relative-velocity equation for the moving link BC."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity \u03c9_AB (CCW positive)", "key": "omegaAB", "value": -2.0 * math.sqrt(2.0), "tol": 0.03, "unit": "rad/s"},
            {"label": "Angular velocity \u03c9_BC (CCW positive)", "key": "omegaBC", "value": 2.0 * math.sqrt(2.0), "tol": 0.03, "unit": "rad/s"},
        ],
        "vector_lines": [
            r"\mathbf{v}_C=8(\cos45^\circ\,\mathbf{i}-\sin45^\circ\,\mathbf{j})=(5.657\,\mathbf{i}-5.657\,\mathbf{j})\ \text{m/s}",
            r"\mathbf{r}_{C/B}=-2\mathbf{j}\ \text{m},\qquad \omega_{BC}\mathbf{k}\times\mathbf{r}_{C/B}=2\omega_{BC}\mathbf{i}",
        ],
        "solution_lines": [
            r"\mathbf{v}_C=8(\cos45^\circ\,\mathbf{i}-\sin45^\circ\,\mathbf{j})=(5.657\,\mathbf{i}-5.657\,\mathbf{j})\ \text{m/s}",
            r"\mathbf{v}_B=v_B\,\mathbf{j}",
            r"\mathbf{r}_{C/B}=(0\,\mathbf{i}-2\,\mathbf{j})\ \text{m}",
            r"\mathbf{v}_C=\mathbf{v}_B+\omega_{BC}\mathbf{k}\times\mathbf{r}_{C/B}=\mathbf{v}_B+(2\omega_{BC}\,\mathbf{i})",
            r"i:\ 5.657=2\omega_{BC}\Rightarrow \omega_{BC}=2.828\ \text{rad/s}",
            r"j:\ -5.657=v_B",
            r"v_{By}=2\omega_{AB}=-5.657\Rightarrow\omega_{AB}=-2.828\ \text{rad/s (clockwise)}",
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
            "Bar AB is pinned at fixed A, has length 0.200 m, and is at 45\u00b0 above +x. "
            "Its angular velocity is \u03c9_AB = 6 rad/s counterclockwise. "
            "Link BC has length 0.500 m and extends from B at 30\u00b0 below +x. "
            "Point C is a horizontal slider. Determine the angular "
            "velocity of link BC and the velocity of slider C. Report positive angular velocity as CCW "
            "and positive slider velocity to the right."
        ),
        "givens": ["A is fixed", "AB = 0.200 m at 45\u00b0 above +x", "BC = 0.500 m at 30\u00b0 below +x", "\u03c9_AB = 6 rad/s CCW", "C is a horizontal slider"],
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
                    "v = \u03b1r",
                    "v = |\u03c9|r",
                    "v = \u03c9\u00b2r",
                    "v = r/\u03c9",
                ],
                "correct": "v = |\u03c9|r",
                "why": r"At that instant, speed is $v=|\omega|r$ about the finite IC; determine the sense separately."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity of BC (CCW positive)", "key": "omegaBC", "value": -1.9595917942265424, "tol": 0.03, "unit": "rad/s"},
            {"label": "Velocity of C (rightward positive)", "key": "vC", "value": -1.3384260859804926, "tol": 0.03, "unit": "m/s"},
        ],
        "vector_lines": [
            r"\mathbf{r}_{B/A}=0.200(\cos45^\circ\,\mathbf{i}+\sin45^\circ\,\mathbf{j})=(0.1414\,\mathbf{i}+0.1414\,\mathbf{j})\ \text{m}",
            r"\mathbf{v}_B=\omega_{AB}\mathbf{k}\times\mathbf{r}_{B/A}=6\mathbf{k}\times(0.1414\mathbf{i}+0.1414\mathbf{j})=(-0.8485\,\mathbf{i}+0.8485\,\mathbf{j})\ \text{m/s}",
            r"\mathbf{r}_{C/B}=0.500(\cos(-30^\circ)\,\mathbf{i}+\sin(-30^\circ)\,\mathbf{j})=(0.433\,\mathbf{i}-0.250\,\mathbf{j})\ \text{m}",
            r"\omega_{BC}\mathbf{k}\times\mathbf{r}_{C/B}=(0.250\omega_{BC})\mathbf{i}+(0.433\omega_{BC})\mathbf{j}",
            r"\mathbf{v}_C=u\mathbf{i}\qquad (\text{slider C has no }j\text{-component})",
        ],
        "solution_lines": [
            r"v_B=\omega_{AB}AB=(6)(0.200)=1.20\ \text{m/s}",
            r"\mathbf{v}_B \text{ is perpendicular to }AB,\quad \mathbf{v}_C\text{ is horizontal}",
            r"\text{Locate the IC by drawing lines perpendicular to }\mathbf{v}_B\text{ and }\mathbf{v}_C",
            r"r_{B/IC}=\sqrt{2}(0.500\cos30^\circ)=0.61237\ \mathrm{m}",
            r"r_{C/IC}=0.500\cos30^\circ+0.500\sin30^\circ=0.68301\ \mathrm{m}",
            r"|\omega_{BC}|=\frac{1.20}{0.61237}=1.95959\ \mathrm{rad/s}\quad\text{(clockwise)}",
            r"|v_C|=|\omega_{BC}|r_{C/IC}=1.33843\ \mathrm{m/s}\quad\text{(leftward)}",
            r"\mathbf{v}_C=\mathbf{v}_B+\omega_{BC}\mathbf{k}\times\mathbf{r}_{C/B}",
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
            "Two fixed-centre pulleys are connected by an inextensible open belt with no slip. "
            "Pulley A has radius 0.200 m and rotates at \u03c9_A = 12 rad/s counterclockwise. "
            "Pulley B has radius 0.125 m. Determine the angular velocity of B (CCW positive)."
        ),
        "givens": ["r_A = 0.200 m", "r_B = 0.125 m", "\u03c9_A = 12 rad/s CCW", "Fixed centres; inextensible open belt, no slip"],
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
                    "\u03c9_A = \u03c9_B",
                    "\u03c9_A / r_A = \u03c9_B / r_B",
                    "\u03c9_A r_A = \u03c9_B r_B",
                    "\u03c9_A r_B = \u03c9_B r_A\u00b2",
                ],
                "correct": "\u03c9_A r_A = \u03c9_B r_B",
                "why": "Equal tangential speeds give \u03c9_A r_A = \u03c9_B r_B."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity \u03c9_B", "key": "omegaB", "value": 19.2, "tol": 0.05, "unit": "rad/s"},
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
        "givens": ["N_A = 20", "N_B = 60", "N_C = 30", "N_D = 90", "\u03c9_A = 18 rad/s clockwise"],
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
                "why": "If they are on the same shaft, they rotate together with the same \u03c9."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the signed gear-speed relationship for one external mesh (CCW positive).",
                "options": [
                    "\u03c9_1 N_1 = -\u03c9_2 N_2",
                    "\u03c9_1 / N_1 = \u03c9_2 / N_2",
                    "\u03c9_1 N_2 = \u03c9_2 / N_1",
                    "\u03c9_1 = \u03c9_2 always",
                ],
                "correct": "\u03c9_1 N_1 = -\u03c9_2 N_2",
                "why": r"With CCW positive, $\omega_1N_1=-\omega_2N_2$. The equal positive products apply to speed magnitudes."
            }
        ],
        "solve_outputs": [
            {"label": "Angular velocity magnitude of gear D", "key": "omegaD", "value": 2.0, "tol": 0.02, "unit": "rad/s"},
        ],
        "solution_lines": [
            r"\text{Use CCW positive: }\omega_A=-18\ \mathrm{rad/s}",
            r"\omega_B=-\omega_A\frac{N_A}{N_B}=-(-18)\frac{20}{60}=+6\ \text{rad/s}",
            r"\omega_C=\omega_B=6\ \text{rad/s}",
            r"\omega_D=-\omega_C\frac{N_C}{N_D}=-6\frac{30}{90}=-2\ \text{rad/s},\quad |\omega_D|=2\ \mathrm{rad/s}",
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
            "A disk rotates about a fixed axis. At point P on the rim, r = 0.30 m, \u03c9 = 6 rad/s CCW and "
            "\u03b1 = 4 rad/s\u00b2 CCW at the instant shown. Determine the magnitudes of the tangential acceleration, normal acceleration, "
            "and resultant acceleration of point P."
        ),
        "givens": ["r = 0.30 m", "\u03c9 = 6 rad/s CCW", "\u03b1 = 4 rad/s\u00b2 CCW"],
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
                    "a_t = \u03c9r and a_n = \u03b1r",
                    "a_t = \u03b1r and a_n = \u03c9\u00b2r",
                    "a_t = \u03c9\u00b2r and a_n = \u03b1r",
                    "a_t = v/r and a_n = \u03b1\u00b2r",
                ],
                "correct": "a_t = \u03b1r and a_n = \u03c9\u00b2r",
                "why": "Tangential acceleration depends on \u03b1, while normal acceleration depends on \u03c9\u00b2."
            }
        ],
        "solve_outputs": [
            {"label": "Tangential acceleration a_t", "key": "at", "value": 1.2, "tol": 0.02, "unit": "m/s\u00b2"},
            {"label": "Normal acceleration a_n", "key": "an", "value": 10.8, "tol": 0.03, "unit": "m/s\u00b2"},
            {"label": "Resultant acceleration |a|", "key": "ares", "value": math.hypot(1.2, 10.8), "tol": 0.03, "unit": "m/s\u00b2"},
        ],
        "solution_lines": [
            r"a_t=\alpha r=(4)(0.30)=1.20\ \text{m/s}^2",
            r"a_n=\omega^2 r=(6^2)(0.30)=10.8\ \text{m/s}^2",
            r"|a|=\sqrt{a_t^2+a_n^2}=\sqrt{1.20^2+10.8^2}=10.87\ \text{m/s}^2",
        ],
        "teaching_point": "Even if \u03b1 were zero, the normal component could still exist because it depends on \u03c9\u00b2.",
    },
    {
        "id": "A2",
        "topic": "Acceleration analysis",
        "level": 2,
        "title": "Relative acceleration with a vertical slider",
        "difficulty": "Moderate",
        "diagram": "slider_acceleration",
        "description": (
            "Link AB has length 0.50 m and is inclined 30\u00b0 above the horizontal. Point A moves horizontally "
            "to the right at a constant speed of 1.0 m/s, so a_A = 0. Point B is constrained to move vertically. "
            "Complete the velocity step first, then determine the angular acceleration of the link and the acceleration of B. "
            "Use counterclockwise positive and upward positive."
        ),
        "givens": ["AB = 0.50 m", "\u03b8 = 30\u00b0", "v_A = 1.0 m/s constant", "a_A = 0", "B is a vertical slider"],
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
                    "The velocity analysis and angular velocity \u03c9",
                    "The moment of inertia",
                    "The work done by the link",
                ],
                "correct": "The velocity analysis and angular velocity \u03c9",
                "why": "The normal term uses \u03c9\u00b2, so the velocity analysis must be done first."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-acceleration equation.",
                "options": [
                    "a_B = a_A + \u03b1 \u00d7 r_B/A - \u03c9\u00b2 r_B/A",
                    "a_B = v_A + \u03b1 \u00d7 r_B/A - \u03c9\u00b2 r_B/A",
                    "a_B = a_A + \u03c9 \u00d7 r_B/A",
                    "a_B = \u03b1r_B/A",
                ],
                "correct": "a_B = a_A + \u03b1 \u00d7 r_B/A - \u03c9\u00b2 r_B/A",
                "why": "For a rigid body in plane motion, acceleration has tangential and normal relative terms."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration \u03b1_AB (CCW positive)", "key": "alphaAB", "value": -16.0 * math.sqrt(3.0), "tol": 0.05, "unit": "rad/s\u00b2"},
            {"label": "Acceleration of B (upward positive)", "key": "aB", "value": -16.0, "tol": 0.05, "unit": "m/s\u00b2"},
        ],
        "vector_lines": [
            r"\mathbf{r}_{B/A}=0.50(\cos30^\circ\,\mathbf{i}+\sin30^\circ\,\mathbf{j})=(0.433\,\mathbf{i}+0.250\,\mathbf{j})\ \text{m}",
            r"\alpha_{AB}\mathbf{k}\times\mathbf{r}_{B/A}=(-0.250\alpha_{AB})\mathbf{i}+(0.433\alpha_{AB})\mathbf{j}",
            r"-\omega_{AB}^2\mathbf{r}_{B/A}=-16(0.433\mathbf{i}+0.250\mathbf{j})=(-6.928\mathbf{i}-4.000\mathbf{j})",
        ],
        "solution_lines": [
            r"\text{From the velocity step: }\omega_{AB}=4.00\ \text{rad/s}",
            r"\mathbf{r}_{B/A}=(0.433\,\mathbf{i}+0.250\,\mathbf{j})\ \text{m}",
            r"\mathbf{a}_B=\mathbf 0+\alpha_{AB}\mathbf{k}\times\mathbf{r}_{B/A}-\omega_{AB}^2\mathbf{r}_{B/A}",
            r"\mathbf{a}_B=(-0.25\alpha_{AB}-6.928)\mathbf{i}+(0.433\alpha_{AB}-4.000)\mathbf{j}",
            r"a_{Bx}=0\Rightarrow -0.25\alpha_{AB}-6.928=0 \Rightarrow \alpha_{AB}=-27.713\ \text{rad/s}^2",
            r"a_{By}=0.433(-27.713)-4=-16.0\ \text{m/s}^2",
        ],
        "teaching_point": "Acceleration analysis is not complete without the normal term. That is the most common omission.",
    },
    {
        "id": "A3",
        "topic": "Acceleration analysis",
        "level": 3,
        "title": "Crossed-belt acceleration transfer",
        "difficulty": "Moderate",
        "diagram": "belt_acceleration",
        "description": (
            "An inextensible crossed belt connects fixed-centre pulleys A and B without slip, so they rotate in opposite directions. "
            "Pulley A has radius 0.200 m and starts from rest with constant angular acceleration \u03b1_A = 3 rad/s\u00b2 CCW. "
            "Pulley B has radius 0.125 m. Determine the magnitudes of \u03c9_B, \u03b1_B, and the tangential and normal acceleration components "
            "of a point P on the rim of B at t = 3 s."
        ),
        "givens": ["r_A = 0.200 m", "r_B = 0.125 m", "\u03b1_A = 3 rad/s\u00b2 CCW", "\u03c9_A(0)=0", "t = 3 s", "Fixed centres; inextensible crossed belt, no slip"],
        "direction_questions": [
            {
                "q": "For this crossed belt, pulley B rotates:",
                "options": [
                    "In the same direction as A",
                    "In the opposite direction to A",
                    "With zero angular speed",
                    "Only counterclockwise",
                ],
                "correct": "In the opposite direction to A",
                "why": "A crossed belt on parallel pulley axes reverses the direction of rotation."
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
                "q": "Choose the signed no-slip acceleration relation for this crossed belt (CCW positive).",
                "options": [
                    "\u03c9_A\u00b2r_A = \u03c9_B\u00b2r_B",
                    "\u03b1_A r_A = -\u03b1_B r_B",
                    "\u03b1_A = \u03b1_B",
                    "a_nA = a_nB",
                ],
                "correct": "\u03b1_A r_A = -\u03b1_B r_B",
                "why": "A crossed belt reverses the signed angular acceleration. The tangential acceleration magnitudes are equal."
            }
        ],
        "solve_outputs": [
            {"label": "Angular speed magnitude of pulley B at t = 3 s", "key": "omegaB", "value": 14.4, "tol": 0.05, "unit": "rad/s"},
            {"label": "Angular acceleration magnitude of pulley B", "key": "alphaB", "value": 4.8, "tol": 0.03, "unit": "rad/s\u00b2"},
            {"label": "Tangential acceleration of point P on B", "key": "at", "value": 0.6, "tol": 0.02, "unit": "m/s\u00b2"},
            {"label": "Normal acceleration of point P on B", "key": "an", "value": 25.92, "tol": 0.05, "unit": "m/s\u00b2"},
        ],
        "solution_lines": [
            r"\omega_A=\alpha_A t=(3)(3)=9\ \text{rad/s}",
            r"\text{CCW positive: }\omega_A r_A=-\omega_B r_B\Rightarrow\omega_B=-\frac{9(0.200)}{0.125}=-14.4\ \mathrm{rad/s}\ \text{(CW)}",
            r"\alpha_A r_A=-\alpha_B r_B\Rightarrow\alpha_B=-\frac{3(0.200)}{0.125}=-4.8\ \mathrm{rad/s^2}\ \text{(CW)}",
            r"a_t=|\alpha_B|r_B=(4.8)(0.125)=0.60\ \mathrm{m/s^2}",
            r"a_n=\omega_B^2r_B=(14.4^2)(0.125)=25.92\ \mathrm{m/s^2}",
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
            "A is fixed. Link AB extends horizontally to the right and link BC vertically downward, with lengths AB = 2 m and BC = 2 m. "
            "From the velocity step, slider C is known to move down a 45\u00b0 groove at 8 m/s, giving "
            "\u03c9_AB = -2.828427 rad/s and \u03c9_BC = 2.828427 rad/s (approximately). If slider C has acceleration "
            "3.0 m/s\u00b2 down the same 45\u00b0 groove, determine the angular accelerations \u03b1_AB and \u03b1_BC. "
            "Use counterclockwise as positive."
        ),
        "givens": ["A is fixed", "AB = 2 m", "BC = 2 m", "v_C = 8 m/s down-right along the 45\u00b0 groove", r"$\omega_{AB}=-2\sqrt{2}\ \mathrm{rad/s}$", r"$\omega_{BC}=+2\sqrt{2}\ \mathrm{rad/s}$", "a_C = 3 m/s\u00b2 down-right along the same groove"],
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
                    "Because \u03b1 depends on kinetic energy",
                    "Because the normal terms use the known angular velocities \u03c9",
                    "Because it makes the drawing prettier",
                    "Because only velocity gives the link lengths",
                ],
                "correct": "Because the normal terms use the known angular velocities \u03c9",
                "why": "The normal relative acceleration terms contain \u03c9\u00b2."
            }
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-acceleration equation for link BC.",
                "options": [
                    "a_C = a_B + \u03b1_BC \u00d7 r_C/B - \u03c9_BC\u00b2 r_C/B",
                    "a_C = v_B + \u03b1_BC \u00d7 r_C/B - \u03c9_BC\u00b2 r_C/B",
                    "a_C = a_B + \u03c9_BC \u00d7 r_C/B",
                    "a_C = \u03b1_BC r_C/B only",
                ],
                "correct": "a_C = a_B + \u03b1_BC \u00d7 r_C/B - \u03c9_BC\u00b2 r_C/B",
                "why": "You need both the tangential and normal relative terms."
            }
        ],
        "solve_outputs": [
            {"label": "Angular acceleration \u03b1_AB (CCW positive)", "key": "alphaAB", "value": -(8.0 + 3.0 / (2.0 * math.sqrt(2.0))), "tol": 0.04, "unit": "rad/s\u00b2"},
            {"label": "Angular acceleration \u03b1_BC (CCW positive)", "key": "alphaBC", "value": 8.0 + 3.0 / (2.0 * math.sqrt(2.0)), "tol": 0.04, "unit": "rad/s\u00b2"},
        ],
        "vector_lines": [
            r"\mathbf{a}_C=3(\cos45^\circ\,\mathbf{i}-\sin45^\circ\,\mathbf{j})=(2.121\,\mathbf{i}-2.121\,\mathbf{j})\ \text{m/s}^2",
            r"\mathbf{a}_B=\alpha_{AB}\mathbf{k}\times(2\mathbf{i})-\omega_{AB}^2(2\mathbf{i})=(-16)\mathbf{i}+(2\alpha_{AB})\mathbf{j}",
            r"\mathbf{r}_{C/B}=-2\mathbf{j}\ \text{m}",
            r"\alpha_{BC}\mathbf{k}\times\mathbf{r}_{C/B}=2\alpha_{BC}\mathbf{i},\qquad -\omega_{BC}^2\mathbf{r}_{C/B}=+16\mathbf{j}",
        ],
        "solution_lines": [
            r"\mathbf{a}_C=3(\cos45^\circ\,\mathbf{i}-\sin45^\circ\,\mathbf{j})=(2.121\,\mathbf{i}-2.121\,\mathbf{j})\ \text{m/s}^2",
            r"\mathbf{a}_B=\alpha_{AB}\mathbf{k}\times(2\mathbf{i})-\omega_{AB}^2(2\mathbf{i})=(-16)\mathbf{i}+(2\alpha_{AB})\mathbf{j}",
            r"\mathbf{r}_{C/B}=(0\mathbf{i}-2\mathbf{j})\ \text{m}",
            r"\alpha_{BC}\mathbf{k}\times\mathbf{r}_{C/B}=(2\alpha_{BC})\mathbf{i}",
            r"-\omega_{BC}^2\mathbf{r}_{C/B}=(0\mathbf{i}+16\mathbf{j})",
            r"\mathbf{a}_C=\mathbf{a}_B+(2\alpha_{BC})\mathbf{i}+16\mathbf{j}",
            r"i:\ 2.121=-16+2\alpha_{BC}\Rightarrow \alpha_{BC}=9.061\ \text{rad/s}^2",
            r"j:\ -2.121=2\alpha_{AB}+16\Rightarrow \alpha_{AB}=-9.061\ \text{rad/s}^2",
        ],
        "teaching_point": "The clean method is always the same: velocity first, identify constraints, then acceleration with tangential and normal components.",
    },
]


# Randomised two-link activity.  The lengths and prescribed motion of AB stay
# constant.  Only the three displayed angles vary.  Discrete angle sets make
# it possible to exhaustively validate every combination at startup.
RANDOM_AB_ANGLES = (70, 80, 90, 100, 110)
RANDOM_BC_ANGLES = (25, 35, 45, 55, 65)       # below the negative x-axis
RANDOM_GUIDE_ANGLES = (15, 25, 35, 45, 55)    # positive motion: down-left
RANDOM_L_AB = 2.00
RANDOM_L_BC = 1.75
RANDOM_OMEGA_AB = 4.00
RANDOM_ALPHA_AB = 5.00


def _vec2(value, name="vector"):
    """Return one finite planar vector with a stable, explicit (2,) shape."""
    vector = np.asarray(value, dtype=float)
    if vector.shape != (2,):
        raise ValueError(name + " must have shape (2,), received " + repr(vector.shape) + ".")
    if not np.all(np.isfinite(vector)):
        raise ValueError(name + " must contain only finite values.")
    return vector


def _cross2d(left, right):
    """Return the scalar z-component of the cross product of two 2-D vectors.

    NumPy's np.cross previously accepted two length-2 arrays and returned a
    zero-dimensional scalar.  That compatibility path is deprecated/removed
    in newer NumPy releases, so compute the planar determinant explicitly.
    """
    left = _vec2(left, "left planar vector")
    right = _vec2(right, "right planar vector")
    return float(left[0] * right[1] - left[1] * right[0])


def _unit_from_degrees(angle_deg):
    angle = math.radians(float(angle_deg))
    return _vec2([math.cos(angle), math.sin(angle)], "unit direction")


def _perp(vector):
    """Return k cross vector, using the same CCW convention in every figure."""
    vector = _vec2(vector)
    return np.array([-vector[1], vector[0]])


def _solve_slider_link(r, v_base, guide, a_base=None):
    """Solve planar rigid-link motion with one endpoint on a fixed straight guide."""
    r, v_base, guide = _vec2(r), _vec2(v_base), _vec2(guide)
    matrix = np.column_stack((guide, -_perp(r)))
    speed, omega = np.linalg.solve(matrix, v_base)
    result = {
        "v": speed * guide, "omega": float(omega),
        "v_relative": omega * _perp(r),
    }
    if a_base is not None:
        normal = -(omega ** 2) * r
        acceleration, alpha = np.linalg.solve(matrix, _vec2(a_base) + normal)
        result.update(a=acceleration * guide, alpha=float(alpha),
                      a_t=alpha * _perp(r), a_n=normal)
    return result


def solve_guided_problem(problem_id):
    """Derive the guided targets and plot vectors from their physical givens.

    This calculation does not read the stored answer keys. In particular, the
    IC example is checked with a separate relative-velocity solution.
    """
    if problem_id in ("V1", "A1"):
        r = 0.30 * _unit_from_degrees(50.0 if problem_id == "V1" else 55.0)
        v = 6.0 * _perp(r)
        a_t, a_n = 4.0 * _perp(r), -36.0 * r
        outputs = ({"vP": float(np.linalg.norm(v))} if problem_id == "V1" else
                   {"at": float(np.linalg.norm(a_t)), "an": float(np.linalg.norm(a_n)),
                    "ares": float(np.linalg.norm(a_t + a_n))})
        return dict(r_op=r, v_p=v, a_t=a_t, a_n=a_n, a_p=a_t + a_n, outputs=outputs)

    if problem_id in ("V2", "A2"):
        r = 0.50 * _unit_from_degrees(30.0)
        v_a = np.array([2.0 if problem_id == "V2" else 1.0, 0.0])
        motion = _solve_slider_link(r, v_a, [0.0, 1.0], [0.0, 0.0])
        outputs = ({"omegaAB": motion["omega"], "vB": float(motion["v"][1])}
                   if problem_id == "V2" else
                   {"alphaAB": motion["alpha"], "aB": float(motion["a"][1])})
        return dict(r_ba=r, v_a=v_a, v_b=motion["v"], v_ba=motion["v_relative"],
                    omega_ab=motion["omega"], alpha_ab=motion["alpha"],
                    a_b=motion["a"], a_ba_t=motion["a_t"], a_ba_n=motion["a_n"],
                    outputs=outputs)

    if problem_id in ("V3", "A4"):
        r_ba, r_cb = np.array([2.0, 0.0]), np.array([0.0, -2.0])
        guide = _unit_from_degrees(-45.0)
        v_c, a_c = 8.0 * guide, 3.0 * guide
        matrix = np.column_stack((_perp(r_ba), _perp(r_cb)))
        omega_ab, omega_bc = np.linalg.solve(matrix, v_c)
        v_b, v_cb = omega_ab * _perp(r_ba), omega_bc * _perp(r_cb)
        a_bn, a_cbn = -(omega_ab ** 2) * r_ba, -(omega_bc ** 2) * r_cb
        alpha_ab, alpha_bc = np.linalg.solve(matrix, a_c - a_bn - a_cbn)
        a_bt, a_cbt = alpha_ab * _perp(r_ba), alpha_bc * _perp(r_cb)
        outputs = ({"omegaAB": float(omega_ab), "omegaBC": float(omega_bc)}
                   if problem_id == "V3" else
                   {"alphaAB": float(alpha_ab), "alphaBC": float(alpha_bc)})
        return dict(r_ba=r_ba, r_cb=r_cb, v_b=v_b, v_cb=v_cb, v_c=v_c,
                    omega_ab=float(omega_ab), omega_bc=float(omega_bc),
                    alpha_ab=float(alpha_ab), alpha_bc=float(alpha_bc),
                    a_b=a_bt + a_bn, a_b_t=a_bt, a_b_n=a_bn,
                    a_cb_t=a_cbt, a_cb_n=a_cbn, a_c=a_c, outputs=outputs)

    if problem_id == "V4":
        r_ba = 0.200 * _unit_from_degrees(45.0)
        r_cb = 0.500 * _unit_from_degrees(-30.0)
        v_b = 6.0 * _perp(r_ba)
        motion = _solve_slider_link(r_cb, v_b, [1.0, 0.0])
        ic = r_ba + _perp(v_b) / motion["omega"]
        return dict(r_ba=r_ba, r_cb=r_cb, v_b=v_b, v_c=motion["v"],
                    v_cb=motion["v_relative"], omega_bc=motion["omega"], ic=ic,
                    outputs={"omegaBC": motion["omega"], "vC": float(motion["v"][0])})

    if problem_id in ("V5", "A3"):
        r_a, r_b = 0.200, 0.125
        omega_a = 12.0 if problem_id == "V5" else 3.0 * 3.0
        direction = 1.0 if problem_id == "V5" else -1.0
        omega_b = direction * omega_a * r_a / r_b
        alpha_b = direction * 3.0 * r_a / r_b
        a_t = np.array([-alpha_b * r_b, 0.0])  # P is at the top of B.
        a_n = np.array([0.0, -(omega_b ** 2) * r_b])
        outputs = ({"omegaB": omega_b} if problem_id == "V5" else
                   {"omegaB": abs(omega_b), "alphaB": abs(alpha_b),
                    "at": float(np.linalg.norm(a_t)), "an": float(np.linalg.norm(a_n))})
        return dict(omega_a=omega_a, omega_b=omega_b, alpha_b=alpha_b,
                    a_t=a_t, a_n=a_n, a_p=a_t + a_n, outputs=outputs)

    if problem_id == "V6":
        omega_a = -18.0
        omega_b = -omega_a * 20.0 / 60.0
        omega_c = omega_b
        omega_d = -omega_c * 30.0 / 90.0
        return dict(omega_a=omega_a, omega_b=omega_b, omega_c=omega_c,
                    omega_d=omega_d, outputs={"omegaD": abs(omega_d)})
    raise ValueError("Unknown guided problem: " + str(problem_id))


def _random_combination_valid(theta_ab_deg, theta_bc_down_deg, guide_down_deg):
    e_ab = _unit_from_degrees(theta_ab_deg)
    e_bc = _unit_from_degrees(180.0 + float(theta_bc_down_deg))
    guide = _unit_from_degrees(180.0 + float(guide_down_deg))
    C = RANDOM_L_AB * e_ab + RANDOM_L_BC * e_bc
    return (
        abs(float(np.dot(guide, e_bc))) >= 0.45
        and C[1] > 0.12
        and float(np.linalg.norm(C)) > 0.35
    )


def solve_random_two_link(theta_ab_deg, theta_bc_down_deg, guide_down_deg):
    """Solve one instantaneous AB-BC geometry using CCW-positive vectors.

    theta_ab_deg is measured CCW from +x.  The BC and guide angles are both
    measured below the negative x-axis, so their absolute angles are
    180 degrees plus the supplied values.  Positive slider motion follows the
    down-left guide arrow displayed at C.
    """
    theta_bc_abs = 180.0 + float(theta_bc_down_deg)
    guide_abs = 180.0 + float(guide_down_deg)
    e_ab = _unit_from_degrees(theta_ab_deg)
    n_ab = np.array([-e_ab[1], e_ab[0]])
    e_bc = _unit_from_degrees(theta_bc_abs)
    n_bc = np.array([-e_bc[1], e_bc[0]])
    guide = _unit_from_degrees(guide_abs)

    r_ba = RANDOM_L_AB * e_ab
    r_cb = RANDOM_L_BC * e_bc
    A = np.array([0.0, 0.0])
    B = A + r_ba
    C = B + r_cb
    denominator = float(np.dot(guide, e_bc))
    if abs(denominator) < 0.45:
        raise ValueError("Guide is too close to perpendicular to BC for a stable activity.")
    if C[1] <= 0.12 or np.linalg.norm(C - A) <= 0.35:
        raise ValueError("Generated geometry does not meet the diagram-clearance rules.")

    # Member AB: fixed-axis rotation about A.
    v_b = RANDOM_OMEGA_AB * RANDOM_L_AB * n_ab
    a_b_t = RANDOM_ALPHA_AB * RANDOM_L_AB * n_ab
    a_b_n = -(RANDOM_OMEGA_AB ** 2) * RANDOM_L_AB * e_ab
    a_b = a_b_t + a_b_n

    # Member BC: slider compatibility.  Dotting the vector equation with e_BC
    # removes the unknown rotational (normal-to-link) velocity term.
    v_c_signed = float(np.dot(v_b, e_bc) / denominator)
    v_c = v_c_signed * guide
    omega_bc = float(np.dot(v_c - v_b, n_bc) / RANDOM_L_BC)
    v_cb = omega_bc * RANDOM_L_BC * n_bc

    # The fixed straight guide gives a_C = a_C_signed * guide.  Dotting the
    # acceleration equation with e_BC removes alpha_BC.
    a_c_signed = float(
        (np.dot(a_b, e_bc) - (omega_bc ** 2) * RANDOM_L_BC) / denominator
    )
    a_c = a_c_signed * guide
    a_cb_n = -(omega_bc ** 2) * RANDOM_L_BC * e_bc
    alpha_bc = float(np.dot(a_c - a_b - a_cb_n, n_bc) / RANDOM_L_BC)
    a_cb_t = alpha_bc * RANDOM_L_BC * n_bc

    return {
        "theta_ab": float(theta_ab_deg),
        "theta_bc_down": float(theta_bc_down_deg),
        "theta_bc_abs": theta_bc_abs,
        "guide_down": float(guide_down_deg),
        "guide_abs": guide_abs,
        "A": A, "B": B, "C": C,
        "e_ab": e_ab, "n_ab": n_ab, "e_bc": e_bc, "n_bc": n_bc,
        "guide": guide, "r_ba": r_ba, "r_cb": r_cb,
        "v_b": v_b, "v_c": v_c, "v_cb": v_cb,
        "a_b_t": a_b_t, "a_b_n": a_b_n, "a_b": a_b,
        "a_cb_t": a_cb_t, "a_cb_n": a_cb_n, "a_c": a_c,
        "v_c_signed": v_c_signed, "a_c_signed": a_c_signed,
        "omega_bc": omega_bc, "alpha_bc": alpha_bc,
        "denominator": denominator,
    }


def _vec_latex(vector, unit):
    return (
        f"({vector[0]:.4f}\\,\\mathbf{{i}}{vector[1]:+.4f}\\,\\mathbf{{j}})"
        f"\\ \\mathrm{{{unit}}}"
    )


def make_random_two_link_problem(seed):
    """Create a deterministic problem state from the displayed Question ID."""
    rng = np.random.default_rng(int(seed))
    candidates = [
        (theta, beta, guide)
        for theta in RANDOM_AB_ANGLES
        for beta in RANDOM_BC_ANGLES
        for guide in RANDOM_GUIDE_ANGLES
        if _random_combination_valid(theta, beta, guide)
    ]
    theta_ab, theta_bc, guide_angle = candidates[int(rng.integers(0, len(candidates)))]
    data = solve_random_two_link(theta_ab, theta_bc, guide_angle)

    rb = data["r_ba"]
    rc = data["r_cb"]
    d = data["guide"]
    vb = data["v_b"]
    vc = data["v_c"]
    vcb = data["v_cb"]
    abt = data["a_b_t"]
    abn = data["a_b_n"]
    ab = data["a_b"]
    act = data["a_cb_t"]
    acn = data["a_cb_n"]
    ac = data["a_c"]
    omega_bc = data["omega_bc"]
    alpha_bc = data["alpha_bc"]
    v_c_signed = data["v_c_signed"]
    a_c_signed = data["a_c_signed"]
    den = data["denominator"]

    sign_omega = "counterclockwise" if omega_bc >= 0.0 else "clockwise"
    sign_alpha = "counterclockwise" if alpha_bc >= 0.0 else "clockwise"
    sign_vc = "along the displayed +s_C arrow" if v_c_signed >= 0.0 else "opposite the displayed +s_C arrow"
    sign_ac = "along the displayed +s_C arrow" if a_c_signed >= 0.0 else "opposite the displayed +s_C arrow"

    groups = [
        (
            "1. Sign convention and geometry",
            [
                r"+x\text{ is right},\quad +y\text{ is up},\quad +\mathbf{k}\text{ and positive }\omega,\alpha\text{ are CCW}",
                rf"\mathbf r_{{B/A}}={RANDOM_L_AB:.2f}(\cos {theta_ab}^\circ\,\mathbf i+\sin {theta_ab}^\circ\,\mathbf j)={_vec_latex(rb, 'm')}",
                rf"\mathbf r_{{C/B}}={RANDOM_L_BC:.2f}(\cos {180 + theta_bc}^\circ\,\mathbf i+\sin {180 + theta_bc}^\circ\,\mathbf j)={_vec_latex(rc, 'm')}",
                rf"\mathbf d_C=(\cos {180 + guide_angle}^\circ\,\mathbf i+\sin {180 + guide_angle}^\circ\,\mathbf j)=({d[0]:.4f}\mathbf i{d[1]:+.4f}\mathbf j)",
                r"\mathbf{e}_{BC}=\mathbf{r}_{C/B}/L_{BC},\quad\mathbf{n}_{BC}=\mathbf{k}\times\mathbf{e}_{BC}",
                rf"\mathbf v_C=\dot s_C\mathbf d_C,\quad \mathbf a_C=\ddot s_C\mathbf d_C,\quad \mathbf d_C\cdot\mathbf e_{{BC}}={den:.4f}\neq0",
            ],
        ),
        (
            "2. Member AB: velocity of B",
            [
                rf"\boldsymbol\omega_{{AB}}={RANDOM_OMEGA_AB:.2f}\mathbf k\ \mathrm{{rad/s}}",
                r"\mathbf{v}_B=\mathbf{v}_A+\boldsymbol\omega_{AB}\times\mathbf{r}_{B/A},\qquad \mathbf{v}_A=\mathbf0",
                rf"\mathbf v_B={RANDOM_OMEGA_AB:.2f}\mathbf k\times({_vec_latex(rb, 'm')})={_vec_latex(vb, 'm/s')}",
                rf"|\mathbf v_B|={np.linalg.norm(vb):.4f}\ \mathrm{{m/s}},\qquad \mathbf v_B\perp AB",
            ],
        ),
        (
            "3. Member BC: relative velocity and x-y equations",
            [
                r"\mathbf{v}_C=\mathbf{v}_B+\boldsymbol\omega_{BC}\times\mathbf{r}_{C/B}",
                rf"\dot s_C({d[0]:.4f}\mathbf i{d[1]:+.4f}\mathbf j)=({_vec_latex(vb, 'm/s')})+\omega_{{BC}}\mathbf k\times({_vec_latex(rc, 'm')})",
                rf"x:\quad {d[0]:.4f}\dot s_C={vb[0]:.4f}{(-rc[1]):+.4f}\omega_{{BC}}",
                rf"y:\quad {d[1]:.4f}\dot s_C={vb[1]:.4f}{rc[0]:+.4f}\omega_{{BC}}",
                rf"\dot s_C=\frac{{\mathbf v_B\cdot\mathbf e_{{BC}}}}{{\mathbf d_C\cdot\mathbf e_{{BC}}}}={v_c_signed:.4f}\ \mathrm{{m/s}}",
                rf"\omega_{{BC}}=\frac{{(\mathbf v_C-\mathbf v_B)\cdot\mathbf n_{{BC}}}}{{L_{{BC}}}}={omega_bc:.4f}\ \mathrm{{rad/s}}\quad({sign_omega})",
                rf"\mathbf v_{{C/B}}=\omega_{{BC}}\mathbf k\times\mathbf r_{{C/B}}={_vec_latex(vcb, 'm/s')}",
                rf"\mathbf v_C={_vec_latex(vc, 'm/s')},\quad |\mathbf v_C|={abs(v_c_signed):.4f}\ \mathrm{{m/s}}\quad({sign_vc})",
            ],
        ),
        (
            "4. Member AB: acceleration of B",
            [
                rf"\boldsymbol\alpha_{{AB}}={RANDOM_ALPHA_AB:.2f}\mathbf k\ \mathrm{{rad/s^2}}",
                r"\mathbf{a}_B=\mathbf{a}_A+\boldsymbol\alpha_{AB}\times\mathbf{r}_{B/A}-\omega_{AB}^2\mathbf{r}_{B/A},\qquad \mathbf{a}_A=\mathbf0",
                rf"\mathbf a^t_{{B/A}}=\boldsymbol\alpha_{{AB}}\times\mathbf r_{{B/A}}={_vec_latex(abt, 'm/s^2')},\quad |a^t_{{B/A}}|={np.linalg.norm(abt):.4f}\ \mathrm{{m/s^2}}",
                rf"\mathbf a^n_{{B/A}}=-\omega_{{AB}}^2\mathbf r_{{B/A}}={_vec_latex(abn, 'm/s^2')},\quad |a^n_{{B/A}}|={np.linalg.norm(abn):.4f}\ \mathrm{{m/s^2}}",
                rf"\mathbf a_B=\mathbf a^t_{{B/A}}+\mathbf a^n_{{B/A}}={_vec_latex(ab, 'm/s^2')}",
                rf"|\mathbf a_B|={np.linalg.norm(ab):.4f}\ \mathrm{{m/s^2}}",
            ],
        ),
        (
            "5. Member BC: relative acceleration and x-y equations",
            [
                r"\mathbf{a}_C=\mathbf{a}_B+\boldsymbol\alpha_{BC}\times\mathbf{r}_{C/B}-\omega_{BC}^2\mathbf{r}_{C/B}",
                rf"x:\quad {d[0]:.4f}\ddot s_C={ab[0]:.4f}{(-rc[1]):+.4f}\alpha_{{BC}}{(-omega_bc**2*rc[0]):+.4f}",
                rf"y:\quad {d[1]:.4f}\ddot s_C={ab[1]:.4f}{rc[0]:+.4f}\alpha_{{BC}}{(-omega_bc**2*rc[1]):+.4f}",
                rf"\ddot s_C=\frac{{\mathbf a_B\cdot\mathbf e_{{BC}}-\omega_{{BC}}^2L_{{BC}}}}{{\mathbf d_C\cdot\mathbf e_{{BC}}}}={a_c_signed:.4f}\ \mathrm{{m/s^2}}",
                rf"\alpha_{{BC}}=\frac{{(\mathbf a_C-\mathbf a_B-\mathbf a^n_{{C/B}})\cdot\mathbf n_{{BC}}}}{{L_{{BC}}}}={alpha_bc:.4f}\ \mathrm{{rad/s^2}}\quad({sign_alpha})",
                rf"\mathbf a^t_{{C/B}}=\alpha_{{BC}}\mathbf k\times\mathbf r_{{C/B}}={_vec_latex(act, 'm/s^2')},\quad |a^t_{{C/B}}|={np.linalg.norm(act):.4f}\ \mathrm{{m/s^2}}",
                rf"\mathbf a^n_{{C/B}}=-\omega_{{BC}}^2\mathbf r_{{C/B}}={_vec_latex(acn, 'm/s^2')},\quad |a^n_{{C/B}}|={np.linalg.norm(acn):.4f}\ \mathrm{{m/s^2}}",
                rf"\mathbf a_C=\mathbf a_B+\mathbf a^t_{{C/B}}+\mathbf a^n_{{C/B}}={_vec_latex(ac, 'm/s^2')}",
                rf"|\mathbf a_C|={abs(a_c_signed):.4f}\ \mathrm{{m/s^2}}\quad({sign_ac})",
            ],
        ),
        (
            "6. Numerical closure checks",
            [
                rf"\mathbf v_B+\mathbf v_{{C/B}}-\mathbf v_C={_vec_latex(vb + vcb - vc, 'm/s')}",
                rf"\mathbf a_B+\mathbf a^t_{{C/B}}+\mathbf a^n_{{C/B}}-\mathbf a_C={_vec_latex(ab + act + acn - ac, 'm/s^2')}",
            ],
        ),
    ]

    return {
        "id": "R-" + str(int(seed)),
        "topic": "Combined velocity and acceleration",
        "level": "Random",
        "title": "Randomized two-member AB-BC mechanism",
        "difficulty": "Challenging",
        "diagram": "random_two_link",
        "attempt_seed": int(seed),
        "kinematics": data,
        "description": (
            f"Point A is fixed. Member AB ({RANDOM_L_AB:.2f} m) is at {theta_ab}\u00b0 counterclockwise from +x. "
            f"Member BC ({RANDOM_L_BC:.2f} m) is at {theta_bc}\u00b0 below the negative x-axis. "
            f"Slider C is restricted to the straight guide whose positive direction is {guide_angle}\u00b0 below the negative x-axis. "
            f"At this instant, \u03c9_AB = {RANDOM_OMEGA_AB:.2f} rad/s CCW and \u03b1_AB = {RANDOM_ALPHA_AB:.2f} rad/s\u00b2 CCW. "
            "Determine the velocities and accelerations of B and C and the angular velocity and angular acceleration of BC."
        ),
        "givens": [
            f"Question ID = {int(seed)} (reproduces this exact randomized problem)",
            f"AB = {RANDOM_L_AB:.2f} m; BC = {RANDOM_L_BC:.2f} m",
            f"Angle of AB = {theta_ab}\u00b0 from +x",
            f"Angle of BC = {theta_bc}\u00b0 below -x",
            f"Positive guide direction at C = {guide_angle}\u00b0 below -x",
            f"\u03c9_AB = {RANDOM_OMEGA_AB:.2f} rad/s CCW; \u03b1_AB = {RANDOM_ALPHA_AB:.2f} rad/s\u00b2 CCW",
        ],
        "direction_questions": [
            {
                "q": "What is the direction of velocity of point B?",
                "options": ["Along AB", "Perpendicular to AB", "Along BC", "Along the guide at C"],
                "correct": "Perpendicular to AB",
                "why": "AB rotates about fixed point A, so v_B is perpendicular to AB.",
            },
            {
                "q": "What is the permitted direction of velocity and acceleration of C?",
                "options": ["Along its straight guide", "Perpendicular to its guide", "Always horizontally", "Unrestricted by the guide"],
                "correct": "Along its straight guide",
                "why": "A slider in a fixed straight guide can have velocity and acceleration only along the guide.",
            },
            {
                "q": "Where does the relative normal acceleration a_n(C/B) point?",
                "options": ["From C toward B", "From B toward C", "Perpendicular to BC", "It is always zero"],
                "correct": "From C toward B",
                "why": "The relative normal term is -omega_BC squared times r_C/B, so it points from C toward B.",
            },
        ],
        "equation_questions": [
            {
                "q": "Choose the correct relative-velocity equation for member BC.",
                "options": [
                    "v_C = v_B + \u03c9_BC \u00d7 r_C/B",
                    "v_C = v_B + \u03b1_BC \u00d7 r_C/B",
                    "v_C = a_B + \u03c9_BC \u00d7 r_C/B",
                    "v_C = \u03c9_AB r_C/B only",
                ],
                "correct": "v_C = v_B + \u03c9_BC \u00d7 r_C/B",
                "why": "Points B and C lie on the same rigid member BC.",
            },
            {
                "q": "Choose the complete relative-acceleration equation for member BC.",
                "options": [
                    "a_C = a_B + \u03b1_BC \u00d7 r_C/B - \u03c9_BC\u00b2 r_C/B",
                    "a_C = a_B + \u03c9_BC \u00d7 r_C/B",
                    "a_C = a_B + \u03b1_BC \u00d7 r_C/B",
                    "a_C = \u03c9_BC\u00b2 r_C/B only",
                ],
                "correct": "a_C = a_B + \u03b1_BC \u00d7 r_C/B - \u03c9_BC\u00b2 r_C/B",
                "why": "Both tangential and normal relative-acceleration terms are required.",
            },
        ],
        "solve_outputs": [
            {"label": "Speed of point B", "key": "vBmag", "value": float(np.linalg.norm(vb)), "tol": 0.03, "unit": "m/s"},
            {"label": "Angular velocity \u03c9_BC (CCW positive)", "key": "omegaBC", "value": omega_bc, "tol": 0.03, "unit": "rad/s"},
            {"label": "Velocity of C (positive along the +s_C arrow)", "key": "vC", "value": v_c_signed, "tol": 0.04, "unit": "m/s"},
            {"label": "Acceleration magnitude of point B", "key": "aBmag", "value": float(np.linalg.norm(ab)), "tol": 0.05, "unit": "m/s\u00b2"},
            {"label": "Angular acceleration \u03b1_BC (CCW positive)", "key": "alphaBC", "value": alpha_bc, "tol": 0.05, "unit": "rad/s\u00b2"},
            {"label": "Acceleration of C (positive along the +s_C arrow)", "key": "aC", "value": a_c_signed, "tol": 0.06, "unit": "m/s\u00b2"},
        ],
        "vector_lines": [
            groups[0][1][1], groups[0][1][2], groups[0][1][3],
        ],
        "solution_groups": groups,
        "solution_lines": [line for _, lines in groups for line in lines],
        "teaching_point": (
            "The slider constraint supplies the direction of both v_C and a_C. "
            "The velocity analysis must be completed before acceleration because the normal term for BC uses \u03c9_BC\u00b2. "
            "A negative signed result means the real sense is opposite to the assumed positive arrow or CCW convention."
        ),
    }


def validate_randomized_activity():
    """Exhaustively verify all permitted angle combinations and vector closure."""
    valid_count = 0
    for theta_ab in RANDOM_AB_ANGLES:
        for theta_bc in RANDOM_BC_ANGLES:
            for guide_angle in RANDOM_GUIDE_ANGLES:
                if not _random_combination_valid(theta_ab, theta_bc, guide_angle):
                    continue
                data = solve_random_two_link(theta_ab, theta_bc, guide_angle)
                valid_count += 1
                vector_names = (
                    "A", "B", "C", "e_ab", "n_ab", "e_bc", "n_bc", "guide",
                    "r_ba", "r_cb", "v_b", "v_c", "v_cb", "a_b_t", "a_b_n",
                    "a_b", "a_cb_t", "a_cb_n", "a_c",
                )
                vectors = {name: _vec2(data[name], name) for name in vector_names}
                scalar_names = (
                    "theta_ab", "theta_bc_down", "theta_bc_abs", "guide_down",
                    "guide_abs", "v_c_signed", "a_c_signed", "omega_bc",
                    "alpha_bc", "denominator",
                )
                if not all(math.isfinite(float(data[name])) for name in scalar_names):
                    raise RuntimeError("Non-finite randomized two-link scalar result.")
                if float(np.linalg.norm(vectors["v_b"] + vectors["v_cb"] - vectors["v_c"])) > 1.0e-9:
                    raise RuntimeError("Randomized relative-velocity closure failed.")
                if float(np.linalg.norm(vectors["a_b"] + vectors["a_cb_t"] + vectors["a_cb_n"] - vectors["a_c"])) > 1.0e-8:
                    raise RuntimeError("Randomized relative-acceleration closure failed.")
                if abs(_cross2d(vectors["guide"], vectors["v_c"])) > 1.0e-9:
                    raise RuntimeError("Randomized slider velocity violates its guide.")
                if abs(_cross2d(vectors["guide"], vectors["a_c"])) > 1.0e-8:
                    raise RuntimeError("Randomized slider acceleration violates its guide.")
                # Independent component solve: [d_C, -k cross r_C/B] [u,w] = v_B.
                matrix = np.column_stack((vectors["guide"], -_perp(vectors["r_cb"])))
                speed, omega = np.linalg.solve(matrix, vectors["v_b"])
                acceleration, alpha = np.linalg.solve(
                    matrix, vectors["a_b"] - omega ** 2 * vectors["r_cb"]
                )
                if not np.allclose(
                    [speed, omega, acceleration, alpha],
                    [data["v_c_signed"], data["omega_bc"], data["a_c_signed"], data["alpha_bc"]],
                    rtol=1.0e-11, atol=1.0e-10,
                ):
                    raise RuntimeError("Independent randomized component solve failed.")
    if valid_count < 100:
        raise RuntimeError("Too few valid randomized two-link geometries.")
    return True


def validate_problem_catalog():
    """Validate all ten instructional states and their independent targets."""
    expected_ids = ["V1", "V2", "V3", "V4", "V5", "V6", "A1", "A2", "A3", "A4"]
    actual_ids = [problem["id"] for problem in PROBLEMS]
    if actual_ids != expected_ids:
        raise RuntimeError("Problem catalog mismatch: " + repr(actual_ids))

    supported_diagrams = {
        "fixed_velocity", "slider_velocity", "linked_velocity", "ic_velocity",
        "belt_velocity", "gear_train", "fixed_acceleration", "slider_acceleration",
        "belt_acceleration", "linked_acceleration",
    }
    for problem in PROBLEMS:
        if problem["diagram"] not in supported_diagrams:
            raise RuntimeError("Unsupported diagram for " + problem["id"])
        if not problem["description"] or not problem["solution_lines"]:
            raise RuntimeError("Incomplete problem state for " + problem["id"])
        for group_name in ("direction_questions", "equation_questions"):
            for item in problem[group_name]:
                if item["correct"] not in item["options"]:
                    raise RuntimeError("Invalid answer key in " + problem["id"])
                if len(set(item["options"])) != len(item["options"]):
                    raise RuntimeError("Duplicate choices in " + problem["id"])
        for output in problem["solve_outputs"]:
            if not math.isfinite(float(output["value"])) or float(output["tol"]) <= 0:
                raise RuntimeError("Invalid numeric target in " + problem["id"])

    for problem in PROBLEMS:
        computed = solve_guided_problem(problem["id"])["outputs"]
        if {out["key"] for out in problem["solve_outputs"]} != set(computed):
            raise RuntimeError("Target count mismatch for " + problem["id"])
        for output in problem["solve_outputs"]:
            stored_value = float(output["value"])
            computed_value = float(computed[output["key"]])
            if not math.isclose(stored_value, computed_value, rel_tol=1.0e-10, abs_tol=1.0e-9):
                raise RuntimeError(
                    "Independent target check failed for " + problem["id"] +
                    ": stored=" + repr(stored_value) + ", computed=" + repr(computed_value)
                )

    findings = _find_text_corruption(PROBLEMS, "PROBLEMS")
    if findings:
        raise RuntimeError("Runtime encoding check failed: " + "; ".join(findings[:8]))
    return True


validate_problem_catalog()
validate_randomized_activity()


def get_problem(topic, level):
    for prob in PROBLEMS:
        if prob["topic"] == topic and prob["level"] == level:
            return prob
    return None


def vector_legend_html(topic):
    """Legend used only with worked-solution diagrams."""
    items = [
        ("Known / absolute motion", COLORS["known"]),
        ("Relative motion", COLORS["relative"]),
        ("Tangential acceleration", COLORS["tangent"]),
        ("Normal acceleration", COLORS["normal"]),
        ("Resultant / final vector", COLORS["resultant"]),
    ]
    chips = "".join(
        f'<span class="legend-chip"><span class="legend-box" style="background:{colour}"></span>{label}</span>'
        for label, colour in items
    )
    return f'<div class="legend-row">{chips}</div>'


def draw_arrow(ax, start, end, color, label=None, lw=2.2, mutation=14,
               ls="-", alpha=1.0, label_offset=(0.0, 0.10), zorder=5):
    """Draw one labelled vector with its label offset from the shaft."""
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    arrow = FancyArrowPatch(
        start, end, arrowstyle="->", mutation_scale=mutation,
        linewidth=lw, color=color, linestyle=ls, alpha=alpha, zorder=zorder,
    )
    ax.add_patch(arrow)
    if label:
        midpoint = (start + end) / 2.0
        ax.text(
            midpoint[0] + label_offset[0], midpoint[1] + label_offset[1], label,
            color=color, fontsize=10, weight="bold", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=0.78),
            zorder=zorder + 1,
        )
    return arrow


def draw_rotation_arrow(ax, centre, radius, sense, color, label,
                        start_deg=25.0, sweep_deg=245.0, label_offset=(0.0, 0.0),
                        alpha=1.0):
    """Draw a mathematically unambiguous CCW (+1) or CW (-1) curved arrow."""
    centre = np.asarray(centre, dtype=float)
    angles = np.radians(np.linspace(start_deg, start_deg + sense * sweep_deg, 100))
    points = centre + radius * np.column_stack((np.cos(angles), np.sin(angles)))
    ax.plot(points[:, 0], points[:, 1], color=color, lw=2.0, alpha=alpha, zorder=4)
    draw_arrow(ax, points[-3], points[-1], color, lw=2.0, mutation=13,
               alpha=alpha, zorder=5)
    label_point = centre + np.array([0.0, radius + 0.18]) + np.asarray(label_offset)
    ax.text(
        label_point[0], label_point[1], label, color=color, fontsize=9.5,
        weight="bold", ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.76),
        zorder=6,
    )


def draw_pin(ax, point, label, label_offset=(-0.12, -0.24), fixed=False):
    """Draw a pin; optionally add a compact fixed-support symbol."""
    point = np.asarray(point, dtype=float)
    ax.plot(*point, "o", color="#111827", ms=6.5, zorder=6)
    ax.text(point[0] + label_offset[0], point[1] + label_offset[1], label,
            fontsize=11, weight="bold", zorder=7)
    if fixed:
        ax.plot([point[0] - 0.25, point[0], point[0] + 0.25],
                [point[1] - 0.34, point[1] - 0.08, point[1] - 0.34],
                color=COLORS["link"], lw=1.5, zorder=2)
        ax.plot([point[0] - 0.34, point[0] + 0.34],
                [point[1] - 0.35, point[1] - 0.35],
                color=COLORS["guide"], lw=1.5, zorder=2)


def draw_angle_arc(ax, vertex, radius, start_deg, end_deg, label,
                   color=None, label_radius=None):
    color = color or COLORS["construct"]
    angles = np.radians(np.linspace(start_deg, end_deg, 60))
    vertex = np.asarray(vertex, dtype=float)
    ax.plot(vertex[0] + radius * np.cos(angles),
            vertex[1] + radius * np.sin(angles), color=color, lw=1.7, zorder=3)
    middle = math.radians((start_deg + end_deg) / 2.0)
    rr = label_radius if label_radius is not None else radius + 0.18
    ax.text(vertex[0] + rr * math.cos(middle),
            vertex[1] + rr * math.sin(middle), label,
            color=color, fontsize=9.5, ha="center", va="center", zorder=4)


def finish_axis(ax, xlim, ylim, transparent=False):
    """Apply consistent geometry, margins, and either opaque or transparent canvas."""
    face = "none" if transparent else "#ffffff"
    ax.figure.patch.set_facecolor(face)
    ax.set_facecolor(face)
    ax.figure.patch.set_alpha(0.0 if transparent else 1.0)
    ax.patch.set_alpha(0.0 if transparent else 1.0)
    for label in ax.texts:
        if label.get_color() in (None, "auto", "black", "k", "#000000"):
            label.set_color("#0f172a")
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.figure.tight_layout(pad=0.25)


def _slider_geometry(ax):
    A = np.array([0.35, 0.55])
    length = 2.55
    theta = math.radians(30.0)
    B = A + length * np.array([math.cos(theta), math.sin(theta)])
    ax.plot([B[0] - 0.28, B[0] - 0.28], [B[1] - 1.08, B[1] + 1.08],
            color=COLORS["guide"], lw=2.0, zorder=1)
    ax.plot([B[0] + 0.28, B[0] + 0.28], [B[1] - 1.08, B[1] + 1.08],
            color=COLORS["guide"], lw=2.0, zorder=1)
    ax.add_patch(Rectangle((B[0] - 0.19, B[1] - 0.27), 0.38, 0.54,
                           fill=False, ec=COLORS["link"], lw=2.0, zorder=3))
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=2.8, zorder=2)
    draw_pin(ax, A, "A", (-0.15, -0.27))
    draw_pin(ax, B, "B", (0.12, 0.05))
    ax.plot([A[0], A[0] + 1.10], [A[1], A[1]], color=COLORS["construct"],
            lw=1.2, ls="--", zorder=1)
    draw_angle_arc(ax, A, 0.56, 0.0, 30.0, "30\u00b0", COLORS["construct"], 0.80)
    midpoint = (A + B) / 2.0
    ax.text(midpoint[0] - 0.03, midpoint[1] + 0.22, "AB = 0.50 m",
            fontsize=9.7, color=COLORS["link"], rotation=30, ha="center")
    ax.text(B[0] + 0.44, B[1] - 0.02, "vertical guide", fontsize=9.0,
            color=COLORS["construct"], rotation=90, va="center")
    return A, B, theta


def _linked_geometry(ax):
    A = np.array([0.8, 3.1])
    # Both 2 m links use the same drawing scale.
    B = A + np.array([2.6, 0.0])
    C = B + np.array([0.0, -2.6])
    # Slider groove is drawn as two parallel rails; its centreline passes through C.
    rail_x = np.array([C[0] - 1.05, C[0] + 1.75])
    centre_y = C[1] - (rail_x - C[0])
    offset = 0.17 * math.sqrt(2.0)
    ax.plot(rail_x, centre_y + offset, color=COLORS["guide"], lw=2.0, zorder=1)
    ax.plot(rail_x, centre_y - offset, color=COLORS["guide"], lw=2.0, zorder=1)
    slider_angle = -45.0
    ax.add_patch(Rectangle((C[0] - 0.23, C[1] - 0.14), 0.46, 0.28,
                           angle=slider_angle, rotation_point="center",
                           fill=False, ec=COLORS["link"], lw=1.8, zorder=3))
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=2.8, zorder=2)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS["link"], lw=2.8, zorder=2)
    draw_pin(ax, A, "A", (-0.14, 0.15), fixed=True)
    draw_pin(ax, B, "B", (0.10, 0.13))
    draw_pin(ax, C, "C", (0.12, -0.05))
    ax.text((A[0] + B[0]) / 2.0 + 0.52, A[1] + 0.28, "AB = 2 m",
            fontsize=10.2, color=COLORS["link"], ha="center")
    ax.text(B[0] - 0.34, (B[1] + C[1]) / 2.0, "BC = 2 m",
            fontsize=10.2, color=COLORS["link"], rotation=90, va="center")
    vertex = C + np.array([0.90, -0.90])
    ax.plot([vertex[0], vertex[0] + 0.70], [vertex[1], vertex[1]],
            color=COLORS["construct"], lw=1.1, ls="--")
    draw_angle_arc(ax, vertex, 0.42, -45.0, 0.0, "45\u00b0",
                   COLORS["construct"], 0.66)
    ax.text(4.35, -1.08, "inclined groove", fontsize=9.0, color=COLORS["construct"])
    return A, B, C


def _ic_geometry(ax):
    scale = 6.0
    A = np.array([0.65, 0.72])
    B = A + (0.200 * scale) * np.array([math.cos(math.radians(45.0)), math.sin(math.radians(45.0))])
    C = B + (0.500 * scale) * np.array([math.cos(math.radians(-30.0)), math.sin(math.radians(-30.0))])
    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=2.8)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS["link"], lw=2.8)
    draw_pin(ax, A, "A", (-0.14, -0.27), fixed=True)
    draw_pin(ax, B, "B", (0.10, 0.15))
    draw_pin(ax, C, "C", (0.08, 0.20))
    ax.plot([C[0] - 0.92, C[0] + 0.72], [C[1] - 0.22, C[1] - 0.22], color=COLORS["guide"], lw=2)
    ax.plot([C[0] - 0.92, C[0] + 0.72], [C[1] + 0.22, C[1] + 0.22], color=COLORS["guide"], lw=2)
    ax.add_patch(Rectangle((C[0] - 0.23, C[1] - 0.16), 0.46, 0.32,
                           fill=False, ec=COLORS["link"], lw=2))
    ax.text((A[0] + B[0]) / 2.0 + 0.12, (A[1] + B[1]) / 2.0 - 0.28,
            "AB = 0.200 m", fontsize=9.5, color=COLORS["link"], rotation=45, ha="center")
    ax.text((B[0] + C[0]) / 2.0, (B[1] + C[1]) / 2.0 + 0.28,
            "BC = 0.500 m", fontsize=9.5, color=COLORS["link"], rotation=-30, ha="center")
    ax.plot([A[0], A[0] + 0.75], [A[1], A[1]], color=COLORS["construct"], lw=1.1, ls="--")
    draw_angle_arc(ax, A, 0.42, 0.0, 45.0, "45\u00b0", COLORS["construct"], 0.64)
    ax.plot([B[0], B[0] + 0.78], [B[1], B[1]], color=COLORS["construct"], lw=1.1, ls="--")
    draw_angle_arc(ax, B, 0.48, -30.0, 0.0, "30\u00b0", COLORS["construct"], 0.70)
    ax.text(C[0] - 0.55, C[1] - 0.48, "horizontal guide", fontsize=8.9, color=COLORS["construct"])
    return A, B, C


def _belt_tangent_segments(A, rA, B, rB, crossed):
    """Return exact external (open) or internal (crossed) tangent endpoints."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    distance = float(np.linalg.norm(B - A))
    if rA <= 0 or rB <= 0 or distance <= rA + rB:
        raise ValueError("Belt pulleys must have positive radii and separate, non-overlapping rims.")
    direction = (B - A) / distance
    perpendicular = np.array([-direction[1], direction[0]])
    segments = []
    if crossed:
        cosine = (rA + rB) / distance
        sine = math.sqrt(max(0.0, 1.0 - cosine ** 2))
        for sign in (1.0, -1.0):
            normal = cosine * direction + sign * sine * perpendicular
            segments.append((A + rA * normal, B - rB * normal))
    else:
        cosine = (rA - rB) / distance
        sine = math.sqrt(max(0.0, 1.0 - cosine ** 2))
        for sign in (1.0, -1.0):
            normal = cosine * direction + sign * sine * perpendicular
            segments.append((A + rA * normal, B + rB * normal))
    return segments


def _belt_geometry(ax, crossed=False):
    A = np.array([1.75, 2.05])
    B = np.array([6.15, 2.05])
    rA = 0.92
    rB = rA * 0.125 / 0.200
    ax.add_patch(Circle(A, rA, fill=False, ec=COLORS["link"], lw=2.5, zorder=2))
    ax.add_patch(Circle(B, rB, fill=False, ec=COLORS["link"], lw=2.5, zorder=2))
    for start, end in _belt_tangent_segments(A, rA, B, rB, crossed):
        ax.plot([start[0], end[0]], [start[1], end[1]], color=COLORS["guide"], lw=2.5, zorder=1)
    draw_pin(ax, A, "A", (-0.10, -0.08))
    draw_pin(ax, B, "B", (-0.10, -0.08))
    ax.plot([A[0], A[0] + rA], [A[1], A[1]], color=COLORS["construct"], lw=1.3)
    ax.plot([B[0], B[0] + rB], [B[1], B[1]], color=COLORS["construct"], lw=1.3)
    ax.text(A[0] + rA / 2.0, A[1] + 0.12, "0.200 m", fontsize=9.2,
            color=COLORS["link"], ha="center")
    ax.text(B[0] + 0.08, B[1] - 0.34, "0.125 m", fontsize=9.2,
            color=COLORS["link"], ha="center")
    ax.text(3.58, 3.35, "crossed belt (no slip)" if crossed else "open belt (no slip)",
            fontsize=9.7, color=COLORS["construct"], ha="center")
    return A, rA, B, rB


def _gear_geometry(ax):
    # Pitch radii are proportional to tooth counts: 20:60 and 30:90.
    centres = {
        "A": np.array([1.00, 2.25]),
        "B": np.array([2.80, 2.25]),
        "C": np.array([2.80, 2.25]),
        "D": np.array([5.20, 2.25]),
    }
    radii = {"A": 0.45, "B": 1.35, "C": 0.60, "D": 1.80}
    for name in ("A", "B", "D", "C"):
        centre = centres[name]
        radius = radii[name]
        ax.add_patch(Circle(centre, radius, fill=False, ec=COLORS["link"], lw=2.3, zorder=2))
    ax.plot(*centres["B"], "o", color="#111827", ms=6, zorder=6)
    ax.plot(*centres["A"], "o", color="#111827", ms=5, zorder=6)
    ax.plot(*centres["D"], "o", color="#111827", ms=5, zorder=6)
    ax.text(centres["A"][0] - 0.10, centres["A"][1] - 0.08, "A", fontsize=11, weight="bold")
    ax.text(centres["B"][0] - 0.34, centres["B"][1] + 0.84, "B", fontsize=11, weight="bold")
    ax.text(centres["C"][0] + 0.20, centres["C"][1] - 0.42, "C", fontsize=11, weight="bold")
    ax.text(centres["D"][0] - 0.10, centres["D"][1] - 0.08, "D", fontsize=11, weight="bold")
    ax.plot([1.45, 1.45], [2.15, 2.35], color=COLORS["tangent"], lw=3.0, zorder=7)
    ax.plot([3.40, 3.40], [2.15, 2.35], color=COLORS["tangent"], lw=3.0, zorder=7)
    ax.text(0.66, 1.62, "20 teeth", fontsize=9.2, color=COLORS["link"])
    ax.text(2.30, 3.72, "60 teeth", fontsize=9.2, color=COLORS["link"])
    ax.text(2.42, 1.50, "30 teeth", fontsize=9.2, color=COLORS["link"])
    ax.text(5.52, 0.58, "90 teeth", fontsize=9.2, color=COLORS["link"])
    ax.text(2.80, 2.05, "same shaft", fontsize=8.5, color=COLORS["construct"], ha="center")
    ax.text(1.45, 4.02, "external mesh", fontsize=8.7, color=COLORS["construct"], ha="center")
    ax.text(3.40, 4.02, "external mesh", fontsize=8.7, color=COLORS["construct"], ha="center")
    return centres, radii


def _random_two_link_geometry(ax, problem, transparent=False):
    """Draw the randomized geometry and only its prescribed motion data."""
    data = problem["kinematics"]
    A, B, C = data["A"], data["B"], data["C"]
    guide = data["guide"]
    guide_normal = np.array([-guide[1], guide[0]])

    # Two guide rails and a small slider centred at C.
    for offset in (-0.12, 0.12):
        p1 = C - 1.25 * guide + offset * guide_normal
        p2 = C + 1.25 * guide + offset * guide_normal
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=COLORS["guide"], lw=2.0, zorder=1)
    phi = data["guide_abs"]
    ax.add_patch(Rectangle(
        (C[0] - 0.24, C[1] - 0.09), 0.48, 0.18,
        angle=phi, rotation_point="center", fill=False,
        ec=COLORS["link"], lw=1.9, zorder=3,
    ))

    ax.plot([A[0], B[0]], [A[1], B[1]], color=COLORS["link"], lw=3.0, zorder=2)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=COLORS["link"], lw=3.0, zorder=2)
    draw_pin(ax, A, "A", (0.10, -0.27), fixed=True)
    draw_pin(ax, B, "B", (0.10, 0.10))
    draw_pin(ax, C, "C", (-0.28, 0.13))

    theta_ab = data["theta_ab"]
    theta_bc = data["theta_bc_down"]
    guide_down = data["guide_down"]
    if not transparent:
        ax.plot([A[0], A[0] + 0.92], [A[1], A[1]], color=COLORS["construct"], lw=1.1, ls="--")
        draw_angle_arc(ax, A, 0.48, 0.0, theta_ab, rf"$\theta_{{AB}}={theta_ab:.0f}^\circ$",
                       COLORS["construct"], 0.76)
        ax.plot([B[0], B[0] - 0.90], [B[1], B[1]], color=COLORS["construct"], lw=1.1, ls="--")
        draw_angle_arc(ax, B, 0.44, 180.0, 180.0 + theta_bc,
                       rf"$\theta_{{BC}}={theta_bc:.0f}^\circ$", COLORS["construct"], 0.95)

    # Dimension labels are offset from the link centrelines.
    mid_ab = (A + B) / 2.0
    mid_bc = (B + C) / 2.0
    ab_label = mid_ab - 0.22 * data["n_ab"]
    bc_label = mid_bc + 0.42 * data["e_bc"] - 0.20 * data["n_bc"]
    if not transparent:
        ax.text(ab_label[0], ab_label[1], f"AB = {RANDOM_L_AB:.2f} m",
                fontsize=9.5, color=COLORS["link"], rotation=theta_ab,
                ha="center", va="center")
        ax.text(bc_label[0], bc_label[1], f"BC = {RANDOM_L_BC:.2f} m",
                fontsize=9.5, color=COLORS["link"], rotation=theta_bc,
                ha="center", va="center")

    # The guide arrow is a constraint datum, not a solved velocity vector.
    reference_offset = 0.42 * guide_normal if transparent else np.zeros(2)
    arrow_start = C + reference_offset - 0.12 * guide
    arrow_end = C + reference_offset + 0.68 * guide
    draw_arrow(ax, arrow_start, arrow_end, COLORS["construct"] if transparent else COLORS["known"],
               r"$+s_C$", lw=1.7, label_offset=(0.08, -0.16))
    if not transparent:
        ref = C + 0.72 * np.array([-1.0, 0.0])
        ax.plot([C[0], ref[0]], [C[1], ref[1]], color=COLORS["construct"], lw=1.0, ls="--")
        draw_angle_arc(ax, C, 0.38, 180.0, 180.0 + guide_down,
                       rf"$\gamma_C={guide_down:.0f}^\circ$", COLORS["known"], 0.61)

        draw_rotation_arrow(ax, A + np.array([1.00, -0.02]), 0.28, +1, COLORS["known"],
                            rf"$\omega_{{AB}}={RANDOM_OMEGA_AB:.0f}$", start_deg=-55, sweep_deg=190,
                            label_offset=(0.05, -0.10), alpha=0.92)
        draw_rotation_arrow(ax, A + np.array([1.54, -0.02]), 0.24, +1, COLORS["tangent"],
                            rf"$\alpha_{{AB}}={RANDOM_ALPHA_AB:.0f}$", start_deg=-55, sweep_deg=175,
                            label_offset=(0.05, -0.10), alpha=0.92)
        ax.text(A[0] + 0.30, A[1] - 0.76, r"$\omega$ in rad/s; $\alpha$ in rad/s$^2$",
                fontsize=8.6, color=COLORS["construct"])

    points = np.vstack([A, B, C, C - 1.25 * guide, C + 1.25 * guide])
    finish_axis(
        ax,
        (float(points[:, 0].min() - 0.72), float(points[:, 0].max() + 1.92)),
        (float(points[:, 1].min() - 0.72), float(points[:, 1].max() + 0.72)),
        transparent=transparent,
    )
    return A, B, C


def _schematic_vector_end(start, vector, length=0.85):
    magnitude = float(np.linalg.norm(vector))
    if magnitude <= 1.0e-12:
        return np.asarray(start, dtype=float)
    return np.asarray(start, dtype=float) + length * np.asarray(vector, dtype=float) / magnitude


def draw_random_two_link(problem, stage="question"):
    """Draw bare question geometry or a transparent velocity/acceleration view."""
    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    transparent = stage != "question"
    A, B, C = _random_two_link_geometry(ax, problem, transparent=transparent)
    data = problem["kinematics"]
    midpoint = (B + C) / 2.0

    if stage == "velocity":
        draw_arrow(ax, B + np.array([0.12, 0.05]),
                   _schematic_vector_end(B + np.array([0.12, 0.05]), data["v_b"], 0.92),
                   COLORS["known"], rf"$|\mathbf{{v}}_B|={np.linalg.norm(data['v_b']):.2f}\ \mathrm{{m/s}}$",
                   label_offset=(-0.18, 0.14))
        draw_arrow(ax, C + np.array([-0.05, -0.05]),
                   _schematic_vector_end(C + np.array([-0.05, -0.05]), data["v_c"], 0.92),
                   COLORS["resultant"], rf"$|\mathbf{{v}}_C|={abs(data['v_c_signed']):.2f}\ \mathrm{{m/s}}$",
                   label_offset=(0.10, -0.16))
        rel_start = midpoint + np.array([-0.55, 0.10])
        draw_arrow(ax, rel_start, _schematic_vector_end(rel_start, data["v_cb"], 0.82),
                   COLORS["relative"], r"$\mathbf{v}_{C/B}$", label_offset=(0.18, 0.10))
        draw_rotation_arrow(ax, midpoint + np.array([0.70, 0.40]), 0.27,
                            +1 if data["omega_bc"] >= 0.0 else -1, COLORS["relative"],
                            rf"$\omega_{{BC}}={data['omega_bc']:.2f}$", start_deg=-45, sweep_deg=185,
                            label_offset=(0.34, -0.10), alpha=0.90)
    elif stage == "acceleration":
        draw_arrow(ax, B + np.array([0.10, 0.03]),
                   _schematic_vector_end(B + np.array([0.10, 0.03]), data["a_b"], 0.92),
                   COLORS["known"], r"$\mathbf{a}_B$", label_offset=(-0.18, 0.14))
        draw_arrow(ax, C + np.array([-0.05, -0.04]),
                   _schematic_vector_end(C + np.array([-0.05, -0.04]), data["a_c"], 0.92),
                   COLORS["resultant"], r"$\mathbf{a}_C$", label_offset=(0.10, -0.16))
        t_start = midpoint + np.array([-0.65, 0.30])
        n_start = midpoint + np.array([0.42, -0.28])
        draw_arrow(ax, t_start, _schematic_vector_end(t_start, data["a_cb_t"], 0.70),
                   COLORS["tangent"], r"$\mathbf{a}^{t}_{C/B}$", label_offset=(0.16, 0.12))
        draw_arrow(ax, n_start, _schematic_vector_end(n_start, data["a_cb_n"], 0.70),
                   COLORS["normal"], r"$\mathbf{a}^{n}_{C/B}$", label_offset=(-0.16, -0.12))
        draw_rotation_arrow(ax, midpoint + np.array([0.90, 0.30]), 0.26,
                            +1 if data["alpha_bc"] >= 0.0 else -1, COLORS["tangent"],
                            rf"$\alpha_{{BC}}={data['alpha_bc']:.2f}$", start_deg=-45, sweep_deg=185,
                            label_offset=(0.36, -0.10), alpha=0.90)
    if stage != "question":
        # Allow room for direction arrows that extend beyond the bare geometry.
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        finish_axis(ax, (xmin - 0.45, xmax + 0.25), (ymin - 0.45, ymax + 0.45), transparent=True)
    return fig


def draw_random_vector_polygon(problem, quantity):
    """Draw an actual-value head-to-tail closure polygon for the random attempt."""
    data = problem["kinematics"]
    if quantity == "velocity":
        vectors = [data["v_b"], data["v_cb"]]
        labels = [r"$\mathbf{v}_B$", r"$\mathbf{v}_{C/B}$"]
        colors = [COLORS["known"], COLORS["relative"]]
        resultant = data["v_c"]
        result_label = r"$\mathbf{v}_C$"
        title = r"Velocity polygon: $\mathbf{v}_C=\mathbf{v}_B+\mathbf{v}_{C/B}$"
    else:
        vectors = [data["a_b"], data["a_cb_t"], data["a_cb_n"]]
        labels = [r"$\mathbf{a}_B$", r"$\mathbf{a}^{t}_{C/B}$", r"$\mathbf{a}^{n}_{C/B}$"]
        colors = [COLORS["known"], COLORS["tangent"], COLORS["normal"]]
        resultant = data["a_c"]
        result_label = r"$\mathbf{a}_C$"
        title = r"Acceleration polygon: $\mathbf{a}_C=\mathbf{a}_B+\mathbf{a}^t_{C/B}+\mathbf{a}^n_{C/B}$"

    if not np.allclose(np.sum(vectors, axis=0), resultant, rtol=1.0e-10, atol=1.0e-9):
        raise RuntimeError("Vector polygon does not close.")
    return draw_vector_chain(
        vectors, labels, colors, title,
        unit="m/s" if quantity == "velocity" else "m/s^2", resultant_label=result_label,
    )


def draw_fixed_velocity(solution=False):
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    O = np.array([0.0, 0.0])
    theta = math.radians(50.0)
    P = np.array([math.cos(theta), math.sin(theta)])
    ax.add_patch(Circle(O, 1.0, fill=False, ec=COLORS["link"], lw=2.4))
    draw_pin(ax, O, "O", (-0.15, -0.23), fixed=True)
    draw_pin(ax, P, "P", (0.09, 0.03))
    ax.plot([O[0], P[0]], [O[1], P[1]], color=COLORS["guide"], lw=2.0)
    ax.text(0.31, 0.45, "r = 0.30 m", fontsize=9.6, color=COLORS["link"], rotation=50, ha="center")
    draw_rotation_arrow(ax, O, 0.43, +1, COLORS["known"], r"$\omega=6\ \mathrm{rad/s}$", start_deg=-65, sweep_deg=210)
    if solution:
        tangent = np.array([-math.sin(theta), math.cos(theta)])
        draw_arrow(ax, P, P + 0.78 * tangent, COLORS["resultant"], r"$v_P=1.80\ \mathrm{m/s}$",
                   label_offset=(0.18, 0.08))
        ax.text(1.20, 0.48, r"$\mathbf{v}_P\perp OP$", fontsize=9.2, color=COLORS["resultant"])
    finish_axis(ax, (-1.35, 2.02), (-1.28, 1.55), transparent=solution)
    return fig


def draw_fixed_acceleration(solution=False):
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    O = np.array([0.0, 0.0])
    theta = math.radians(55.0)
    P = np.array([math.cos(theta), math.sin(theta)])
    ax.add_patch(Circle(O, 1.0, fill=False, ec=COLORS["link"], lw=2.4))
    draw_pin(ax, O, "O", (-0.15, -0.23), fixed=True)
    draw_pin(ax, P, "P", (0.09, 0.04))
    ax.plot([O[0], P[0]], [O[1], P[1]], color=COLORS["guide"], lw=2.0)
    ax.text(0.28, 0.48, "r = 0.30 m", fontsize=9.6, color=COLORS["link"], rotation=55, ha="center")
    draw_rotation_arrow(ax, O, 0.38, +1, COLORS["known"], r"$\omega=6$", start_deg=-75, sweep_deg=190,
                        label_offset=(-0.22, -0.06))
    draw_rotation_arrow(ax, O, 0.62, +1, COLORS["tangent"], r"$\alpha=4$", start_deg=115, sweep_deg=145,
                        label_offset=(-0.65, -0.55))
    ax.text(-1.22, -1.04, r"$\omega$ in rad/s; $\alpha$ in rad/s$^2$", fontsize=8.8, color=COLORS["construct"])
    if solution:
        data = solve_guided_problem("A1")
        scale = 0.085  # One common scale for all three acceleration vectors.
        draw_arrow(ax, P, P + scale * data["a_t"], COLORS["tangent"], r"$a_t=1.20$",
                   label_offset=(0.16, 0.08))
        draw_arrow(ax, P, P + scale * data["a_n"], COLORS["normal"], r"$a_n=10.8$",
                   label_offset=(-0.02, -0.13))
        draw_arrow(ax, P, P + scale * data["a_p"], COLORS["resultant"], r"$\mathbf{a}_P$",
                   label_offset=(-0.19, 0.13), ls="--")

    finish_axis(ax, (-1.42, 2.02), (-1.28, 1.62), transparent=solution)
    return fig


def draw_slider_velocity(accel=False, solution=False):
    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    A, B, theta = _slider_geometry(ax)
    midpoint = (A + B) / 2.0
    if accel:
        draw_arrow(ax, A + np.array([-0.05, -0.33]), A + np.array([0.86, -0.33]),
                   COLORS["known"], r"$v_A=1.0\ \mathrm{m/s}$", label_offset=(0.0, -0.13))
        ax.text(A[0] - 0.04, A[1] + 0.25, r"$a_A=0$ (constant speed)", fontsize=9.0,
                color=COLORS["known"])
        if solution:
            perpendicular = np.array([-math.sin(theta), math.cos(theta)])
            toward_A = (A - B) / np.linalg.norm(A - B)
            draw_arrow(ax, B + np.array([0.55, 0.18]), B + np.array([0.55, -0.98]),
                       COLORS["resultant"], r"$a_B=-16.0\ \mathrm{m/s^2}$", label_offset=(0.25, 0.0))
            draw_arrow(ax, midpoint + np.array([-0.10, 0.10]),
                       midpoint + np.array([-0.10, 0.10]) - 0.92 * perpendicular,
                       COLORS["tangent"], r"$a^t_{B/A}$", label_offset=(-0.10, -0.10))
            draw_arrow(ax, B + np.array([-0.08, -0.04]), B + np.array([-0.08, -0.04]) + 1.00 * toward_A,
                       COLORS["normal"], r"$a^n_{B/A}$", label_offset=(0.06, -0.14))
    else:
        draw_arrow(ax, A + np.array([-0.05, -0.33]), A + np.array([1.02, -0.33]),
                   COLORS["known"], r"$v_A=2.0\ \mathrm{m/s}$", label_offset=(0.0, -0.13))
        if solution:
            draw_arrow(ax, B + np.array([0.55, -0.12]), B + np.array([0.55, 1.02]),
                       COLORS["resultant"], r"$v_B=3.46\ \mathrm{m/s}$", label_offset=(0.18, 0.02))
            perpendicular = np.array([-math.sin(theta), math.cos(theta)])
            relative_start = midpoint + np.array([0.38, -0.48])
            draw_arrow(ax, relative_start, relative_start + 0.95 * perpendicular,
                       COLORS["relative"], r"$v_{B/A}$", label_offset=(0.20, -0.02))
            rotation_centre = midpoint + np.array([-0.62, 0.62])
            draw_rotation_arrow(ax, rotation_centre, 0.30, +1, COLORS["resultant"], r"$\omega_{AB}=8.0$",
                                start_deg=-35, sweep_deg=185, label_offset=(0.0, -0.08))
    finish_axis(ax, (-0.32, 4.08), (-0.02, 2.92), transparent=solution)
    return fig


def draw_linked_velocity(accel=False, solution=False):
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    A, B, C = _linked_geometry(ax)
    data = solve_guided_problem("A4" if accel else "V3")
    if accel:
        draw_arrow(ax, C + np.array([0.18, -0.02]), C + np.array([1.08, -0.92]),
                   COLORS["known"], r"$a_C=3.0\ \mathrm{m/s^2}$", label_offset=(0.20, -0.08))
        # Angular velocities are given from the preceding velocity step.
        draw_rotation_arrow(ax, (A + B) / 2.0, 0.34, -1, COLORS["known"], r"$\omega_{AB}=-2.828$",
                            start_deg=120, sweep_deg=190, label_offset=(-0.42, -0.08), alpha=0.92)
        draw_rotation_arrow(ax, (B + C) / 2.0, 0.32, +1, COLORS["known"], r"$\omega_{BC}=2.828$",
                            start_deg=-55, sweep_deg=190, label_offset=(0.65, -0.02), alpha=0.92)
        if solution:
            start = B + np.array([0.65, 0.08])
            draw_arrow(ax, start, _schematic_vector_end(start, data["a_b"], 1.12),
                       COLORS["resultant"], r"$a_B$", label_offset=(0.14, 0.0))
            start = (B + C) / 2.0 + np.array([-1.25, 0.35])
            draw_arrow(ax, start, _schematic_vector_end(start, data["a_cb_t"], 0.98),
                       COLORS["tangent"], r"$a^t_{C/B}$", label_offset=(0.0, 0.13))
            start = (B + C) / 2.0 + np.array([-0.85, -0.75])
            draw_arrow(ax, start, _schematic_vector_end(start, data["a_cb_n"], 0.94),
                       COLORS["normal"], r"$a^n_{C/B}$", label_offset=(-0.25, 0.0))
    else:
        draw_arrow(ax, C + np.array([0.18, -0.02]), C + np.array([1.10, -0.94]),
                   COLORS["known"], r"$v_C=8.0\ \mathrm{m/s}$", label_offset=(0.20, -0.08))
        if solution:
            start = B + np.array([0.60, 0.06])
            draw_arrow(ax, start, _schematic_vector_end(start, data["v_b"], 1.12),
                       COLORS["resultant"], r"$v_B$", label_offset=(0.12, 0.0))
            start = (B + C) / 2.0 + np.array([-1.38, -0.05])
            draw_arrow(ax, start, _schematic_vector_end(start, data["v_cb"], 1.00),
                       COLORS["relative"], r"$v_{C/B}$", label_offset=(0.0, 0.13))
            draw_rotation_arrow(ax, (A + B) / 2.0, 0.34, -1, COLORS["resultant"], r"$\omega_{AB}=-2.828$",
                                start_deg=120, sweep_deg=190, label_offset=(-0.42, -0.08))
            draw_rotation_arrow(ax, (B + C) / 2.0, 0.32, +1, COLORS["resultant"], r"$\omega_{BC}=2.828$",
                                start_deg=-55, sweep_deg=190, label_offset=(0.65, -0.02))
    finish_axis(ax, (0.05, 6.15), (-1.32, 4.12), transparent=solution)
    return fig


def draw_ic_velocity(solution=False):
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    A, B, C = _ic_geometry(ax)
    draw_rotation_arrow(ax, A, 0.42, +1, COLORS["known"], r"$\omega_{AB}=6\ \mathrm{rad/s}$",
                        start_deg=-75, sweep_deg=175, label_offset=(-0.20, -0.05))
    if solution:
        vB_direction = np.array([-1.0, 1.0]) / math.sqrt(2.0)
        draw_arrow(ax, B, B + 0.95 * vB_direction, COLORS["known"], r"$|v_B|=1.20$",
                   label_offset=(-0.25, 0.24))
        draw_arrow(ax, C + np.array([0.0, 0.34]), C + np.array([-1.18, 0.34]),
                   COLORS["resultant"], r"$|v_C|=1.338$", label_offset=(0.0, 0.13))
        data = solve_guided_problem("V4")
        IC = A + 6.0 * data["ic"]
        ax.plot([C[0], C[0]], [C[1], IC[1]], color=COLORS["construct"], lw=1.6, ls="--")
        ax.plot([B[0], IC[0]], [B[1], IC[1]], color=COLORS["construct"], lw=1.6, ls="--")
        ax.plot(*IC, "o", color=COLORS["relative"], ms=6, zorder=6)
        ax.text(IC[0] + 0.10, IC[1] + 0.02, "IC", fontsize=10.5, weight="bold", color=COLORS["relative"])
        ax.text(C[0] + 0.12, (C[1] + IC[1]) / 2.0, r"$r_{C/IC}$", fontsize=9.1, color=COLORS["construct"])
        middle = (B + IC) / 2.0
        ax.text(middle[0] - 0.23, middle[1] + 0.10, r"$r_{B/IC}$", fontsize=9.1,
                color=COLORS["construct"], rotation=45)
        draw_rotation_arrow(ax, IC, 0.40, -1, COLORS["resultant"], r"$\omega_{BC}=-1.960\ \mathrm{rad/s}$",
                            start_deg=110, sweep_deg=185, label_offset=(-0.45, -0.10))
    finish_axis(ax, (-0.15, 6.10), (-1.02, 5.12 if solution else 3.05), transparent=solution)
    return fig


def draw_belt_velocity(accel=False, solution=False):
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    A, rA, B, rB = _belt_geometry(ax, crossed=accel)
    if accel:
        draw_rotation_arrow(ax, A, 0.58, +1, COLORS["known"], r"$\alpha_A=3\ \mathrm{rad/s^2}$",
                            start_deg=-55, sweep_deg=200, label_offset=(-0.20, 0.02))
        P = B + np.array([0.0, rB])
        draw_pin(ax, P, "P", (0.11, 0.05))
        ax.text(0.55, 0.37, r"$\omega_A(0)=0,\quad t=3\ \mathrm{s}$", fontsize=9.1, color=COLORS["known"])
        if solution:
            draw_rotation_arrow(ax, B, 0.38, -1, COLORS["resultant"],
                                r"$\omega_B=-14.4,\ \alpha_B=-4.8$", start_deg=125, sweep_deg=200,
                                label_offset=(0.05, -0.10))
            for start, end in _belt_tangent_segments(A, rA, B, rB, True):
                midpoint = (start + end) / 2.0
                tangent = (end - start) / np.linalg.norm(end - start)
                # Orient each span from its actual contact velocity at A.
                contact_velocity = _perp(start - A)  # A rotates CCW.
                tangent *= 1.0 if np.dot(contact_velocity, tangent) > 0.0 else -1.0
                draw_arrow(ax, midpoint - 0.45 * tangent, midpoint + 0.45 * tangent,
                           COLORS["relative"], None, lw=1.9, alpha=0.88)
    else:
        draw_rotation_arrow(ax, A, 0.58, +1, COLORS["known"], r"$\omega_A=12\ \mathrm{rad/s}$",
                            start_deg=-55, sweep_deg=200, label_offset=(-0.18, 0.02))
        if solution:
            draw_rotation_arrow(ax, B, 0.38, +1, COLORS["resultant"], r"$\omega_B=19.2\ \mathrm{rad/s}$",
                                start_deg=-55, sweep_deg=200, label_offset=(0.10, -0.08))
            for start, end in _belt_tangent_segments(A, rA, B, rB, False):
                midpoint = (start + end) / 2.0
                tangent = (end - start) / np.linalg.norm(end - start)
                contact_velocity = _perp(start - A)
                tangent *= 1.0 if np.dot(contact_velocity, tangent) > 0.0 else -1.0
                draw_arrow(ax, midpoint - 0.48 * tangent, midpoint + 0.48 * tangent,
                           COLORS["relative"], r"$v_{belt}=2.40\ \mathrm{m/s}$" if midpoint[1] > A[1] else None,
                           lw=1.9, label_offset=(0.0, 0.13), alpha=0.88)
    finish_axis(ax, (0.35, 7.35), (0.15, 3.88), transparent=solution)
    return fig


def draw_gear_train(solution=False):
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    centres, radii = _gear_geometry(ax)
    draw_rotation_arrow(ax, centres["A"], 0.29, -1, COLORS["known"], r"$\omega_A=18\ \mathrm{rad/s\ CW}$",
                        start_deg=115, sweep_deg=190, label_offset=(-0.38, -0.08))
    if solution:
        draw_rotation_arrow(ax, centres["B"], 0.94, +1, COLORS["relative"], r"$\omega_B=\omega_C=6\ \mathrm{rad/s}$",
                            start_deg=-55, sweep_deg=175, label_offset=(0.28, 0.05), alpha=0.90)
        draw_rotation_arrow(ax, centres["D"], 1.32, -1, COLORS["resultant"], r"$\omega_D=2.0\ \mathrm{rad/s\ CW}$",
                            start_deg=115, sweep_deg=180, label_offset=(0.45, -0.02), alpha=0.92)
        ax.text(0.60, 0.12, "Each external mesh reverses direction; the common B-C shaft does not.",
                fontsize=8.9, color=COLORS["construct"])
    ax.text(0.60, -0.21, "Pitch-circle projection: A-B and C-D occupy separate axial planes.",
            fontsize=8.7, color=COLORS["construct"])
    finish_axis(ax, (-0.62, 7.32), (-0.40, 4.35), transparent=solution)
    return fig


def draw_vector_chain(vectors, labels, colors, title, xlim=None, ylim=None,
                      unit="", resultant_label=r"$\mathrm{resultant}$"):
    """Draw a head-to-tail polygon with actual components and one common scale."""
    vectors = [_vec2(vector) for vector in vectors]
    points = np.vstack([np.zeros(2), np.cumsum(vectors, axis=0)])
    span = max(1.0, float(np.ptp(points, axis=0).max()))
    margin = 0.23 * span
    if xlim is None:
        xlim = (float(points[:, 0].min() - margin), float(points[:, 0].max() + margin))
    if ylim is None:
        ylim = (float(points[:, 1].min() - margin), float(points[:, 1].max() + margin))
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    origin = np.array([0.0, 0.0])
    cursor = origin.copy()
    for vector, label, color in zip(vectors, labels, colors):
        next_point = cursor + vector
        offset = 0.055 * span * _perp(vector) / max(np.linalg.norm(vector), 1.0e-12)
        arrow_size = min(15.0, max(4.0, 15.0 * math.sqrt(np.linalg.norm(vector) / span)))
        draw_arrow(ax, cursor, next_point, color, label, lw=2.4,
                   label_offset=offset, mutation=arrow_size)
        cursor = next_point
    result_offset = -0.085 * span * _perp(cursor) / max(np.linalg.norm(cursor), 1.0e-12)
    draw_arrow(ax, origin, cursor, COLORS["resultant"], resultant_label, lw=2.0,
               ls="--", alpha=0.80, label_offset=result_offset)
    ax.axhline(0.0, color=COLORS["guide"], lw=1.0, ls=":", alpha=0.75)
    ax.axvline(0.0, color=COLORS["guide"], lw=1.0, ls=":", alpha=0.75)
    ax.set_title(title, fontsize=10.2, color=COLORS["construct"], weight="bold", pad=12)
    ax.text(0.01, 0.01, r"$+x$ right; $+y$ up" + (r"; $\mathrm{" + unit + "}$" if unit else ""),
            transform=ax.transAxes, fontsize=8.5, color=COLORS["construct"])
    finish_axis(ax, xlim, ylim, transparent=True)
    return fig


def draw_local_acceleration_components_A3():
    """At the top of B, the real resultant is almost vertically downward."""
    data = solve_guided_problem("A3")
    return draw_vector_chain(
        [data["a_t"], data["a_n"]],
        [r"$a_t=0.60$", r"$a_n=25.92$"],
        [COLORS["tangent"], COLORS["normal"]],
        "Point P at top of B: true acceleration scale",
        (-8.5, 10.0), (-29.5, 4.5), unit="m/s^2", resultant_label=r"$\mathbf{a}_P$",
    )


def draw_component_diagram(problem_id):
    """Return a separate pedagogical vector/component diagram where it adds value."""
    data = solve_guided_problem(problem_id)
    if problem_id == "V2":
        return draw_vector_chain(
            [data["v_a"], data["v_ba"]],
            [r"$\mathbf{v}_A$", r"$\mathbf{v}_{B/A}$"],
            [COLORS["known"], COLORS["relative"]],
            r"Velocity polygon: $\mathbf{v}_B=\mathbf{v}_A+\mathbf{v}_{B/A}$",
            unit="m/s", resultant_label=r"$\mathbf{v}_B$",
        )
    if problem_id == "V3":
        return draw_vector_chain(
            [data["v_b"], data["v_cb"]],
            [r"$\mathbf{v}_B$", r"$\mathbf{v}_{C/B}$"],
            [COLORS["known"], COLORS["relative"]],
            r"Velocity polygon: $\mathbf{v}_C=\mathbf{v}_B+\mathbf{v}_{C/B}$",
            unit="m/s", resultant_label=r"$\mathbf{v}_C$",
        )
    if problem_id == "V4":
        return draw_vector_chain(
            [data["v_b"], data["v_cb"]],
            [r"$\mathbf{v}_B$", r"$\mathbf{v}_{C/B}$"],
            [COLORS["known"], COLORS["relative"]],
            "Component check: the slider result is horizontal",
            unit="m/s", resultant_label=r"$\mathbf{v}_C$",
        )
    if problem_id == "A1":
        return draw_vector_chain(
            [data["a_t"], data["a_n"]],
            [r"$\mathbf{a}_t$", r"$\mathbf{a}_n$"],
            [COLORS["tangent"], COLORS["normal"]],
            "Actual components at P in the shown x-y frame",
            unit="m/s^2", resultant_label=r"$\mathbf{a}_P$",
        )
    if problem_id == "A2":
        return draw_vector_chain(
            [data["a_ba_t"], data["a_ba_n"]],
            [r"$\mathbf{a}^t_{B/A}$", r"$\mathbf{a}^n_{B/A}$"],
            [COLORS["tangent"], COLORS["normal"]],
            "Acceleration polygon: horizontal parts cancel",
            unit="m/s^2", resultant_label=r"$\mathbf{a}_B$",
        )
    if problem_id == "A3":
        return draw_local_acceleration_components_A3()
    if problem_id == "A4":
        return draw_vector_chain(
            [data["a_b"], data["a_cb_t"], data["a_cb_n"]],
            [r"$\mathbf{a}_B$", r"$\mathbf{a}^t_{C/B}$", r"$\mathbf{a}^n_{C/B}$"],
            [COLORS["known"], COLORS["tangent"], COLORS["normal"]],
            r"Acceleration polygon: $\mathbf{a}_C=\mathbf{a}_B+\mathbf{a}^t_{C/B}+\mathbf{a}^n_{C/B}$",
            unit="m/s^2", resultant_label=r"$\mathbf{a}_C$",
        )
    return None


def render_problem_figure(problem):
    """Render only geometry, dimensions, constraints, angles, and given motion."""
    diagram = problem["diagram"]
    if diagram == "fixed_velocity":
        fig = draw_fixed_velocity(solution=False)
    elif diagram == "fixed_acceleration":
        fig = draw_fixed_acceleration(solution=False)
    elif diagram == "slider_velocity":
        fig = draw_slider_velocity(accel=False, solution=False)
    elif diagram == "slider_acceleration":
        fig = draw_slider_velocity(accel=True, solution=False)
    elif diagram == "linked_velocity":
        fig = draw_linked_velocity(accel=False, solution=False)
    elif diagram == "linked_acceleration":
        fig = draw_linked_velocity(accel=True, solution=False)
    elif diagram == "ic_velocity":
        fig = draw_ic_velocity(solution=False)
    elif diagram == "belt_velocity":
        fig = draw_belt_velocity(accel=False, solution=False)
    elif diagram == "belt_acceleration":
        fig = draw_belt_velocity(accel=True, solution=False)
    elif diagram == "gear_train":
        fig = draw_gear_train(solution=False)
    elif diagram == "random_two_link":
        fig = draw_random_two_link(problem, stage="question")
    else:
        fig, _ = plt.subplots()
    _show_figure(fig)


def _show_figure(fig):
    """Release figure managers as well as artists after each Streamlit render."""
    try:
        st.pyplot(fig, clear_figure=True, width="stretch")
    finally:
        plt.close(fig)


def _solution_mechanism_figure(problem):
    diagram = problem["diagram"]
    if diagram == "fixed_velocity":
        return draw_fixed_velocity(solution=True)
    if diagram == "fixed_acceleration":
        return draw_fixed_acceleration(solution=True)
    if diagram == "slider_velocity":
        return draw_slider_velocity(accel=False, solution=True)
    if diagram == "slider_acceleration":
        return draw_slider_velocity(accel=True, solution=True)
    if diagram == "linked_velocity":
        return draw_linked_velocity(accel=False, solution=True)
    if diagram == "linked_acceleration":
        return draw_linked_velocity(accel=True, solution=True)
    if diagram == "ic_velocity":
        return draw_ic_velocity(solution=True)
    if diagram == "belt_velocity":
        return draw_belt_velocity(accel=False, solution=True)
    if diagram == "belt_acceleration":
        return draw_belt_velocity(accel=True, solution=True)
    if diagram == "gear_train":
        return draw_gear_train(solution=True)
    if diagram == "random_two_link":
        return draw_random_two_link(problem, stage="velocity")
    fig, _ = plt.subplots()
    return fig


def render_solution_diagrams(problem):
    """Render solution-only figures with transparent canvases and no overlays."""
    st.markdown("### Solution diagrams")
    st.caption(
        "Mechanism arrows show directions; their lengths are schematic unless stated otherwise. "
        "The separate head-to-tail polygons use the calculated components and a common scale, "
        "with +x right and +y up."
    )
    if problem["diagram"] == "random_two_link":
        st.markdown("**Velocity analysis**")
        left, right = st.columns(2, gap="large")
        with left:
            st.caption("Mechanism with absolute and relative velocity vectors")
            _show_figure(draw_random_two_link(problem, stage="velocity"))
        with right:
            st.caption("Head-to-tail velocity closure using the calculated values")
            _show_figure(draw_random_vector_polygon(problem, "velocity"))
        st.markdown("**Acceleration analysis**")
        left, right = st.columns(2, gap="large")
        with left:
            st.caption("Mechanism with tangential, normal, and absolute acceleration vectors")
            _show_figure(draw_random_two_link(problem, stage="acceleration"))
        with right:
            st.caption("Head-to-tail acceleration closure using the calculated values")
            _show_figure(draw_random_vector_polygon(problem, "acceleration"))
        st.markdown(vector_legend_html(problem["topic"]), unsafe_allow_html=True)
        return

    component = draw_component_diagram(problem["id"])
    if component is None:
        _show_figure(_solution_mechanism_figure(problem))
    else:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("**Motion and constraint diagram**")
            _show_figure(_solution_mechanism_figure(problem))
        with right:
            st.markdown("**Component / construction diagram**")
            _show_figure(component)
    st.markdown(vector_legend_html(problem["topic"]), unsafe_allow_html=True)

def render_learn_tab(topic):
    st.markdown("## Main points and formulas")
    st.markdown(
        """
        <div class="info">
        Use this tab before solving. The goal is to teach a method:
        first identify the motion constraints, then choose the correct equation,
        and only after that substitute the numbers.
        All sliders here have fixed straight guides. Belts are inextensible and do not slip;
        pulley and gear centres are fixed.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if topic == "Combined velocity and acceleration":
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("### Randomized two-link method")
            st.markdown(
                r"""
                1. Adopt **+x right, +y up, and counterclockwise positive**.  
                2. Use fixed-axis rotation of AB to find $\mathbf{v}_B$ and $\mathbf{a}_B$.  
                3. Let $s_C$ be displacement along the guide and $\mathbf{d}_C$ its fixed unit direction. Then $\mathbf{v}_C=\dot s_C\mathbf{d}_C$ and $\mathbf{a}_C=\ddot s_C\mathbf{d}_C$.  
                4. Apply relative velocity to BC and solve the two component equations for $\dot s_C$ and $\omega_{BC}$.  
                5. Use that $\omega_{BC}$ in the relative-acceleration equation, including both tangential and normal terms.  
                6. Check that the velocity and acceleration vector polygons close.
                """
            )
            st.markdown("### Vector equations")
            st.latex(r"\mathbf{v}_B=\boldsymbol\omega_{AB}\times\mathbf{r}_{B/A}")
            st.latex(r"\mathbf{v}_C=\mathbf{v}_B+\boldsymbol\omega_{BC}\times\mathbf{r}_{C/B}")
            st.latex(r"\mathbf{a}_B=\boldsymbol\alpha_{AB}\times\mathbf{r}_{B/A}-\omega_{AB}^{2}\mathbf{r}_{B/A}")
            st.latex(r"\mathbf{a}_C=\mathbf{a}_B+\boldsymbol\alpha_{BC}\times\mathbf{r}_{C/B}-\omega_{BC}^{2}\mathbf{r}_{C/B}")
        with right:
            st.markdown("### Sign and direction reminders")
            st.markdown(
                r"""
                - $\mathbf{v}_B$ is perpendicular to AB.  
                - $\mathbf{v}_{C/B}$ is perpendicular to BC.  
                - $\mathbf{a}^t_{C/B}$ is perpendicular to BC.  
                - $\mathbf{a}^n_{C/B}$ points from C toward B.  
                - Both $\mathbf{v}_C$ and $\mathbf{a}_C$ lie along the fixed straight guide.  
                - A negative $\omega$ or $\alpha$ means clockwise. A negative slider scalar means opposite the displayed positive guide arrow.
                """
            )
            st.warning(
                r"**Do velocity first.** The normal acceleration of C relative to B contains "
                r"the calculated value $\omega_{BC}^{2}$. Skipping the velocity analysis "
                r"makes the acceleration calculation incomplete."
            )
            st.markdown("### Reproducibility")
            st.markdown(
                "Every randomized question displays a **Question ID**. Entering the same "
                "Question ID reproduces the same AB angle, BC angle, guide direction, "
                "calculations, answers, and diagrams."
            )
        return

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
                4. **Resolve angled vectors into** $\mathbf{i}$ **and** $\mathbf{j}$ **components**.  
                5. **Solve the scalar equations** and then check whether the sign and direction make physical sense.  
                """
            )

            st.markdown("### Core equations")
            st.latex(r"\mathbf{v}_B=\mathbf{v}_A+\boldsymbol\omega\times\mathbf{r}_{B/A}")
            st.latex(r"v=|\omega|r \qquad \text{(speed in fixed-axis rotation)}")
            st.latex(r"\omega_A r_A=\omega_B r_B\ \text{(open belt)},\qquad\omega_A r_A=-\omega_B r_B\ \text{(crossed belt)}")
            st.latex(r"\omega_1 N_1=-\omega_2 N_2\ \text{(external gears; CCW positive)}")
            st.latex(r"|\omega_1|N_1=|\omega_2|N_2\ \text{(gear-speed magnitudes)}")
            st.latex(r"v=|\omega|\,r_{/IC} \qquad \text{(speed about a finite IC)}")

            st.markdown("### Important direction rules")
            st.markdown(
                """
                - For rotation about a **fixed pivot**, absolute velocity is **perpendicular to the radius from that pivot**.  
                - When the base point moves, apply the perpendicular rule to the **relative velocity**, then add the base-point velocity.  
                - For a slider in a **fixed straight guide**, velocity lies **along that guide**.  
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
                - **Pure translation** &#8594; every point has the **same velocity vector**.  
                - **Fixed-axis rotation** &#8594; use $v=|\omega|r$ for speed at each point.  
                - **Two points on one moving link** &#8594; use the **relative-velocity equation**.  
                - **Slider-link with known directions** &#8594; the **IC method** is often fastest for velocity only.  
                - **Belts / pulleys** &#8594; use **equal tangential belt speed**.  
                - **Gears** &#8594; use **equal pitch-line speed** and the correct direction reversal.  
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
                1. **Do the velocity analysis first** if any normal term depends on $\omega$.  
                2. **Mark the acceleration constraints** of fixed points, sliders, pulleys, and shared pins.  
                3. **Split the relative acceleration into tangential and normal parts**.  
                4. **Write the full vector equation**, not only one part.  
                5. **Resolve into** $\mathbf{i}$ **and** $\mathbf{j}$ **components** and solve.  
                """
            )

            st.markdown("### Core equations")
            st.latex(r"\mathbf{a}_B=\mathbf{a}_A+\boldsymbol\alpha\times\mathbf{r}_{B/A}-\omega^2\mathbf{r}_{B/A}")
            st.latex(r"a_t=|\alpha|r \qquad \text{(tangential magnitude)}")
            st.latex(r"a_n=\omega^2 r=\dfrac{v^2}{r}")
            st.latex(r"\alpha_A r_A=\alpha_B r_B\ \text{(open belt)},\qquad\alpha_A r_A=-\alpha_B r_B\ \text{(crossed belt)}")
            st.caption(
                "In a_n = v squared / r, v is speed relative to the centre/base point. "
                "For a moving link, use the relative speed, not the endpoint's absolute speed. "
                "The full relative acceleration need not point toward the base: only its normal term does."
            )

            st.markdown("### Direction rules")
            st.markdown(
                r"""
                - Tangential acceleration $a_t$ is **perpendicular** to the radius or link.  
                - Normal acceleration $a_n$ points **toward the centre / base point**.  
                - For a link $AB$, the relative normal acceleration of $B$ with respect to $A$ points **from B toward A**.  
                - Slider acceleration lies **along a fixed straight guide**; a curved guide also produces a normal component.  
                """
            )

        with col2:
            st.markdown("### Big teaching idea")
            st.markdown(
                r"""
                Acceleration analysis is harder than velocity analysis because the relative term has
                **two rotational parts**:
                - a **tangential component** from angular acceleration $\alpha$
                - a **normal component** from angular velocity $\omega$
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
                - Forgetting the normal term $\omega^2 r$.  
                - Writing $\alpha^2 r$ instead of $\omega^2 r$.  
                - Drawing the normal acceleration **away from** the centre instead of **toward** it.  
                - Treating the IC as a fixed centre for acceleration.  
                - Forgetting that for pulleys / belts, the **tangential** acceleration relationship transfers through no-slip, but the **normal** acceleration is not generally the same because $a_n=v^2/r$.  
                - Ignoring slider direction constraints.  
                - Mixing tangential and normal parts into one undefined arrow.  
                """
            )

            st.markdown("### Quick teaching reminders")
            st.markdown(
                r"""
                - Always label which part is **tangential** and which part is **normal**.  
                - If you know the belt speed is the same on two pulleys, that does **not** mean the normal accelerations are the same; different radii give different $v^2/r$.  
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
        This question figure shows only geometry, dimensions, constraints, angles,
        and motion data given in the problem. Solution vectors are deliberately hidden.
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_problem_figure(problem)
    st.caption("Bare-minimum question diagram - no inferred or answer vectors are shown.")
    st.markdown("---")

    for i, item in enumerate(problem["direction_questions"]):
        st.markdown(f"**{i+1}.** " + format_math_text(item["q"]))
        display_options = _display_options(item["options"], equation=False)
        displayed_response = st.radio(
            f"Direction question {i+1}",
            display_options,
            key=f"{problem['id']}_dir_{i}",
            label_visibility="collapsed",
        )
        response = item["options"][display_options.index(displayed_response)]
        if mode == "Practice":
            if response == item["correct"]:
                st.success("Correct. " + format_math_text(item["why"]))
            else:
                st.error("Not yet. " + format_math_text(item["why"]))


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
    reference_col, question_col = st.columns([0.82, 1.18], gap="large")
    with reference_col:
        st.markdown("### Given geometry")
        render_problem_figure(problem)
        st.caption("Only the givens needed to select the equation are shown.")
    with question_col:
        st.markdown("### Equation choice")
        for i, item in enumerate(problem["equation_questions"]):
            st.markdown(f"**{i+1}.** " + format_math_text(item["q"]))
            display_options = _display_options(item["options"], equation=True)
            displayed_response = st.radio(
                f"Equation question {i+1}",
                display_options,
                key=f"{problem['id']}_eq_{i}",
                label_visibility="collapsed",
            )
            response = item["options"][display_options.index(displayed_response)]
            if mode == "Practice":
                if response == item["correct"]:
                    st.success("Correct. " + format_math_text(item["why"]))
                else:
                    st.error("Try again. " + format_math_text(item["why"]))


def render_problem_tab(problem):
    c1, c2 = st.columns([1.0, 1.1], gap="large")
    with c1:
        st.markdown("## Current problem")
        st.caption(f"{problem['topic']} | Level {problem['level']} | Difficulty: {problem['difficulty']}")
        st.markdown(format_math_text(problem["description"]))
        render_given_values(problem["givens"])
    with c2:
        st.markdown("### Bare-minimum question diagram")
        render_problem_figure(problem)
        st.caption(
            "Shows only the geometry, dimensions, constraints, angles, and given motion. "
            "All inferred velocity, acceleration, relative-motion, displacement, and component vectors are reserved for the Solution tab."
        )


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
            st.markdown(format_math_text("**" + out["label"] + "**") + " (" + unit_markdown(out["unit"]) + ")")
            entered[out["key"]] = st.number_input(
                "Enter numerical value",
                key=f"{problem['id']}_{out['key']}",
                format="%.4f",
                label_visibility="collapsed",
            )

    if st.button("Check final answers", key=f"check_{problem['id']}"):
        checks = []
        for out in problem["solve_outputs"]:
            ok = is_close(entered[out["key"]], out["value"], out["tol"])
            checks.append(ok)
            if ok:
                st.success(format_math_text(out["label"]) + ": correct.")
            else:
                if mode == "Practice":
                    st.error(
                        format_math_text(out["label"])
                        + f": not yet. Expected approximately {out['value']:.4f} "
                        + unit_markdown(out["unit"])
                        + "."
                    )
                else:
                    st.error(
                        format_math_text(out["label"])
                        + ": not yet. Check the sign convention and component equations."
                    )

        if all(checks):
            solved = st.session_state.setdefault("solved", set())
            if problem["id"] not in solved:
                solved.add(problem["id"])
                st.session_state["xp"] = st.session_state.get("xp", 0) + 40
            st.success("Excellent \u2014 this mechanism is solved correctly.")
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
    if problem["topic"] == "Combined velocity and acceleration":
        st.markdown(
            "Use fixed-axis rotation for AB, enforce the straight-guide constraint at C, "
            "solve relative velocity for BC, and then use that angular velocity in the full "
            "relative-acceleration equation."
        )
    elif problem["topic"] == "Velocity analysis":
        st.markdown("Classify the motion, mark the velocity directions, choose the compatibility relation, and solve the components.")
    else:
        st.markdown("Complete velocity analysis first, then add the tangential and normal acceleration components.")

    render_solution_diagrams(problem)

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
    if problem.get("solution_groups"):
        for group_title, lines in problem["solution_groups"]:
            st.markdown("#### " + group_title)
            for line in lines:
                st.latex(line)
    else:
        for line in problem["solution_lines"]:
            st.latex(line)

    st.markdown("### Teaching point")
    st.info(format_math_text(problem["teaching_point"]))


def sidebar_controls():
    st.sidebar.markdown("## Mode")
    mode = st.sidebar.radio(
        "Choose activity",
        ["Practice", "Self-test"],
        help="Practice gives immediate guidance. Self-test hides the worked solution until you reveal it."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Activity")
    activity = st.sidebar.selectbox(
        "Choose activity type",
        ["Guided problem bank", "Randomized AB-BC mechanism"],
        help="The randomized activity combines relative velocity and acceleration in one reproducible attempt.",
    )

    if activity == "Guided problem bank":
        st.sidebar.markdown("### Practice setup")
        topic = st.sidebar.radio(
            "Topic",
            ["Velocity analysis", "Acceleration analysis"],
        )
        levels = sorted([p["level"] for p in PROBLEMS if p["topic"] == topic])
        level = st.sidebar.selectbox("Level", levels)
        names = {p["level"]: p["title"] for p in PROBLEMS if p["topic"] == topic}
        st.sidebar.caption(f"Problem: {names[level]}")
        problem = get_problem(topic, level)
    else:
        st.sidebar.markdown("### Randomized question")
        if "random_ab_bc_seed" not in st.session_state:
            st.session_state["random_ab_bc_seed"] = 20261121
        if st.sidebar.button("Generate a new random problem", key="new_random_ab_bc"):
            current = int(st.session_state["random_ab_bc_seed"])
            st.session_state["random_ab_bc_seed"] = (1664525 * current + 1013904223) % 900000000 + 1
        seed = st.sidebar.number_input(
            "Question ID (reproduces the same random problem)",
            min_value=1,
            max_value=999999999,
            step=1,
            key="random_ab_bc_seed",
            help="Enter or share this Question ID to reproduce the same AB angle, BC angle, C-guide angle, calculations, answers, and diagrams.",
        )
        problem = make_random_two_link_problem(int(seed))
        data = problem["kinematics"]
        st.sidebar.caption(format_math_text(
            f"AB angle: {data['theta_ab']:.0f}\u00b0 | "
            f"BC angle: {data['theta_bc_down']:.0f}\u00b0 below -x | "
            f"C guide: {data['guide_down']:.0f}\u00b0 below -x"
        ))
        st.sidebar.caption("Problem: " + problem["title"])

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
    st.sidebar.caption("Build: " + APP_BUILD_ID)

    return mode, problem


render_header()
mode, problem = sidebar_controls()
topic = problem["topic"]

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
