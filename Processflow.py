import streamlit as st
import google.generativeai as genai
import re
import json

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DiagramAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f0f4ff;
    color: #1a1a2e;
}
.stApp { background: #f0f4ff; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 2px solid #e2e8f0;
}
section[data-testid="stSidebar"] * { color: #1a1a2e !important; }
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
section[data-testid="stSidebar"] h3 {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6366f1 !important;
    margin-bottom: 0.5rem;
}

/* ── Sidebar inputs ── */
section[data-testid="stSidebar"] input {
    background: #f8faff !important;
    border: 2px solid #c7d2fe !important;
    border-radius: 8px !important;
    color: #1a1a2e !important;
    font-size: 0.88rem !important;
}
section[data-testid="stSidebar"] input:focus {
    border-color: #6366f1 !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #f8faff !important;
    border: 2px solid #c7d2fe !important;
    border-radius: 8px !important;
    color: #1a1a2e !important;
}
/* Sidebar radio labels */
section[data-testid="stSidebar"] .stRadio label { color: #1a1a2e !important; font-size: 0.9rem; }

/* ── Main header ── */
.main-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    margin-bottom: 2rem;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(99,102,241,0.25);
}
.main-header h1 {
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    color: #ffffff;
    margin: 0;
    letter-spacing: -1px;
    text-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.main-header p {
    color: rgba(255,255,255,0.85);
    font-size: 1rem;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* ── Section headings ── */
h4 { color: #1a1a2e !important; font-weight: 700 !important; }

/* ── Main text inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 2px solid #c7d2fe !important;
    border-radius: 12px !important;
    color: #1a1a2e !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}
/* Input labels */
.stTextArea label, .stTextInput label { color: #374151 !important; font-weight: 600 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
}

/* ── Select box (main) ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 2px solid #c7d2fe !important;
    border-radius: 10px !important;
    color: #1a1a2e !important;
}
.stSelectbox label { color: #374151 !important; font-weight: 600 !important; }

/* ── Radio ── */
.stRadio label { color: #1a1a2e !important; font-size: 0.95rem !important; }
.stRadio > div { gap: 0.75rem; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #e0e7ff;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6366f1;
    border-radius: 8px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #4f46e5 !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.15) !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; font-size: 0.88rem !important; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.badge-weak   { background: #fee2e2; color: #dc2626; border: 1.5px solid #fca5a5; }
.badge-medium { background: #fef3c7; color: #d97706; border: 1.5px solid #fcd34d; }
.badge-strong { background: #dcfce7; color: #16a34a; border: 1.5px solid #86efac; }

/* ── Clarity bar ── */
.clarity-bar-bg {
    background: #e0e7ff;
    border-radius: 20px;
    height: 10px;
    width: 100%;
    overflow: hidden;
    margin: 0.5rem 0;
}
.clarity-bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 0.5s ease;
}

/* ── Step badges ── */
.step-badge {
    background: #ffffff;
    border: 1.5px solid #c7d2fe;
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 0.65rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.88rem;
    color: #374151;
    font-weight: 500;
}

/* ── Card ── */
.card {
    background: #ffffff;
    border: 1.5px solid #c7d2fe;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 12px rgba(99,102,241,0.08);
}
.card p { color: #1a1a2e !important; }

/* ── Mermaid wrapper ── */
.mermaid-wrapper {
    background: #ffffff;
    border: 2px solid #e0e7ff;
    border-radius: 14px;
    padding: 1.5rem;
    overflow-x: auto;
    box-shadow: 0 2px 12px rgba(99,102,241,0.08);
}

/* ── Empty state ── */
.empty-state {
    height: 380px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed #c7d2fe;
    border-radius: 14px;
    background: #ffffff;
}

/* ── Progress bar ── */
.stProgress > div > div { background: #6366f1 !important; border-radius: 20px; }
.stProgress > div { background: #e0e7ff !important; border-radius: 20px; }

/* ── Code block ── */
.stCodeBlock { border: 1.5px solid #c7d2fe !important; border-radius: 10px !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: #f0f4ff !important;
    color: #6366f1 !important;
    border: 2px solid #c7d2fe !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}
.stDownloadButton > button:hover {
    background: #e0e7ff !important;
    border-color: #6366f1 !important;
    transform: none !important;
}

/* ── Divider ── */
hr { border-color: #e0e7ff !important; }

/* ── Expander ── */
.streamlit-expanderHeader { color: #4f46e5 !important; font-weight: 600 !important; }
.streamlit-expanderContent { background: #f8faff !important; border-radius: 0 0 10px 10px; }

/* ── History items ── */
.history-item {
    font-size: 0.78rem;
    color: #6b7280;
    padding: 0.4rem 0;
    border-bottom: 1px solid #e0e7ff;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for key, val in {
    "guided_step": 0,
    "guided_answers": {},
    "last_diagram": "",
    "last_mermaid": "",
    "last_steps": [],
    "last_clarity": 0,
    "history": [],
    "api_key": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
GUIDED_QUESTIONS = [
    ("system_name",  "What is the name of the system you want to design?"),
    ("system_type",  "Is it an online system, offline system, or both?"),
    ("actors",       "Who are the main users/actors? (e.g. Customer, Admin, Doctor)"),
    ("core_actions", "What are the 3–5 main actions or processes in this system?"),
    ("goal",         "What is the final output or goal of the system?"),
]

def compute_clarity(text: str) -> int:
    """Return 0-100 clarity score."""
    score = 0
    words = text.split()
    if len(words) >= 5:  score += 20
    if len(words) >= 10: score += 20
    action_verbs = ["manage","create","process","send","receive","order","register",
                    "login","pay","track","generate","submit","approve","notify","update"]
    if any(v in text.lower() for v in action_verbs): score += 20
    actors = ["user","admin","customer","patient","doctor","staff","manager","employee"]
    if any(a in text.lower() for a in actors): score += 20
    system_words = ["system","app","platform","portal","dashboard","service","module"]
    if any(s in text.lower() for s in system_words): score += 20
    return min(score, 100)

def clarity_label(score: int):
    if score < 40:  return "weak",  "badge-weak"
    if score < 70:  return "medium","badge-medium"
    return "strong","badge-strong"

def get_bar_color(score: int):
    if score < 40:  return "#f87171"
    if score < 70:  return "#fbbf24"
    return "#34d399"

def build_gemini_prompt(user_input: str, diagram_type: str) -> str:
    dtype_map = {
        "Flowchart":      "flowchart TD",
        "Sequence":       "sequenceDiagram",
        "Entity-Relation":"erDiagram",
        "Class Diagram":  "classDiagram",
    }
    mermaid_hint = dtype_map.get(diagram_type, "flowchart TD")
    return f"""You are an expert system architect and Mermaid.js diagram specialist.

The user wants to design: "{user_input}"
Diagram type requested: {diagram_type}

Your task:
1. Expand and clarify the system if the description is vague.
2. Identify Actors, Inputs, Outputs, and Main Processes.
3. Generate valid Mermaid.js diagram code using "{mermaid_hint}" syntax.
4. List the step-by-step process flow (max 8 steps).

Return ONLY valid JSON in this exact structure (no markdown fences, no extra text):
{{
  "system_title": "...",
  "actors": ["...", "..."],
  "processes": ["...", "..."],
  "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
  "mermaid_code": "flowchart TD\\n    A[...] --> B[...]\\n    ..."
}}

Rules for mermaid_code:
- Must be valid Mermaid syntax
- Use double backslash n (\\n) for newlines inside the JSON string
- No backticks inside the JSON value
- For sequenceDiagram: use participant and ->>/-->> arrows
- For flowchart: use --> arrows and descriptive node labels
- Keep it clean, readable, max 15 nodes
"""

def refine_bad_prompt(raw: str) -> str:
    return f"""You are a helpful system design assistant.

The user gave a very short or vague system description: "{raw}"

Your job:
1. Make reasonable assumptions about what this system does.
2. Expand it into a clear, detailed one-paragraph description.
3. Return ONLY the improved description as plain text (no JSON, no bullet points).
"""

def call_gemini(api_key: str, prompt: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def extract_json(text: str) -> dict:
    # Strip markdown fences if Gemini still wraps it
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    return json.loads(text)

def render_mermaid(code: str):
    """Render Mermaid diagram via CDN in an HTML component."""
    escaped = code.replace("`", r"\`")
    html = f"""
    <div class="mermaid-wrapper" style="background:#fff;border:2px solid #e0e7ff;border-radius:14px;padding:1.5rem;overflow-x:auto;">
      <div id="mermaid-graph" style="text-align:center;"></div>
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{
        startOnLoad: false,
        theme: 'default',
        themeVariables: {{
          primaryColor: '#e0e7ff',
          primaryTextColor: '#1a1a2e',
          primaryBorderColor: '#6366f1',
          lineColor: '#6366f1',
          secondaryColor: '#f0f4ff',
          tertiaryColor: '#faf5ff',
          edgeLabelBackground: '#f0f4ff',
          clusterBkg: '#f0f4ff',
          fontFamily: 'Inter, sans-serif',
        }}
      }});
      const code = `{escaped}`;
      const {{ svg }} = await mermaid.render('graphDiv', code);
      document.getElementById('mermaid-graph').innerHTML = svg;
    </script>
    """
    st.components.v1.html(html, height=520, scrolling=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 Gemini API Key")
    api_input = st.text_input(
        "Enter your API key",
        type="password",
        placeholder="AIza...",
        value=st.session_state.api_key,
        help="Get a free key at https://aistudio.google.com/app/apikey"
    )
    if api_input:
        st.session_state.api_key = api_input

    st.markdown("---")
    st.markdown("### 📐 Diagram Type")
    diagram_type = st.selectbox(
        "Choose diagram type",
        ["Flowchart", "Sequence", "Entity-Relation", "Class Diagram"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### ⚡ Mode")
    mode = st.radio(
        "Mode",
        ["🤖 Auto (Smart Fix)", "🧭 Guided (Step-by-Step)"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📜 History")
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-5:])):
            st.markdown(f"""<div class="history-item">
                {i+1}. {h['input'][:40]}…</div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#9ca3af;font-size:0.82rem;'>No history yet.</p>", unsafe_allow_html=True)

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🧠 DiagramAI</h1>
  <p>Powered by Google Gemini &nbsp;·&nbsp; Turn vague ideas into clear system diagrams</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AUTO MODE
# ─────────────────────────────────────────────
if "Auto" in mode:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 💬 Describe Your System")
        user_input = st.text_area(
            "System description",
            placeholder="e.g. hospital management system, online food delivery, library management...",
            height=120,
            label_visibility="collapsed"
        )

        if user_input:
            clarity = compute_clarity(user_input)
            label, badge_cls = clarity_label(clarity)
            bar_color = get_bar_color(clarity)

            st.markdown(f"""
            <div style="margin-bottom:1rem;">
              <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.4rem;">
                <span style="font-size:0.82rem;color:#6b7280;font-weight:600;">
                  Prompt Clarity
                </span>
                <span class="badge {badge_cls}">{label.upper()} · {clarity}%</span>
              </div>
              <div class="clarity-bar-bg">
                <div class="clarity-bar-fill" style="width:{clarity}%;background:{bar_color};"></div>
              </div>
              {'<p style="font-size:0.8rem;color:#dc2626;margin-top:0.4rem;font-weight:500;">⚠️ Prompt is vague — Gemini will auto-improve it before generating.</p>' if clarity < 40 else ''}
            </div>
            """, unsafe_allow_html=True)

        generate_btn = st.button("✨ Generate Diagram", use_container_width=True)

        if generate_btn:
            if not st.session_state.api_key:
                st.error("Please enter your Gemini API key in the sidebar.")
            elif not user_input.strip():
                st.warning("Please enter a system description.")
            else:
                with st.spinner("🧠 Analyzing prompt..."):
                    clarity = compute_clarity(user_input)
                    final_input = user_input

                    # Auto-refine weak prompts
                    if clarity < 40:
                        try:
                            refined = call_gemini(
                                st.session_state.api_key,
                                refine_bad_prompt(user_input)
                            )
                            final_input = refined
                            st.session_state["auto_refined"] = refined
                        except Exception as e:
                            st.error(f"Gemini error during refinement: {e}")
                            st.stop()
                    else:
                        st.session_state.pop("auto_refined", None)

                with st.spinner("⚙️ Generating diagram..."):
                    try:
                        raw = call_gemini(
                            st.session_state.api_key,
                            build_gemini_prompt(final_input, diagram_type)
                        )
                        data = extract_json(raw)
                        st.session_state.last_diagram  = data.get("system_title", final_input)
                        st.session_state.last_mermaid  = data.get("mermaid_code", "")
                        st.session_state.last_steps    = data.get("steps", [])
                        st.session_state.last_actors   = data.get("actors", [])
                        st.session_state.last_processes= data.get("processes", [])
                        st.session_state.last_clarity  = clarity
                        st.session_state.history.append({
                            "input":   user_input,
                            "title":   data.get("system_title",""),
                            "mermaid": data.get("mermaid_code",""),
                        })
                    except Exception as e:
                        st.error(f"Gemini error: {e}")
                        st.stop()

        # Show refined prompt notice
        if "auto_refined" in st.session_state:
            with st.expander("🔧 Auto-Improved Prompt (click to see)"):
                st.markdown(f"""<div style="font-size:0.88rem;color:#374151;
                    line-height:1.7;padding:0.5rem;">{st.session_state.auto_refined}</div>""",
                    unsafe_allow_html=True)

        # System breakdown
        if st.session_state.last_steps:
            st.markdown("#### 🧩 System Breakdown")
            if hasattr(st.session_state, 'last_actors') and st.session_state.get("last_actors"):
                st.markdown(f"""<p style="font-size:0.78rem;font-weight:700;
                    color:#6366f1;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.3rem;">👤 Actors</p>""", unsafe_allow_html=True)
                actors_str = " · ".join([f"<span style='color:#4f46e5;font-weight:600;background:#e0e7ff;padding:2px 10px;border-radius:20px;'>{a}</span>"
                                         for a in st.session_state.get("last_actors",[])])
                st.markdown(f"<p style='font-size:0.85rem;'>{actors_str}</p>", unsafe_allow_html=True)

            st.markdown(f"""<p style="font-size:0.78rem;font-weight:700;
                color:#6366f1;text-transform:uppercase;letter-spacing:0.05em;margin:0.8rem 0 0.3rem;">📋 Process Steps</p>""", unsafe_allow_html=True)
            for step in st.session_state.last_steps:
                st.markdown(f'<div class="step-badge">→ {step}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📊 Diagram Output")
        if st.session_state.last_mermaid:
            st.markdown(f"""<p style="font-size:0.82rem;font-weight:600;
                color:#6b7280;margin-bottom:0.8rem;">
                🖼️ {st.session_state.last_diagram}</p>""", unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["🗺️ Visual Diagram", "📝 Mermaid Code"])
            with tab1:
                render_mermaid(st.session_state.last_mermaid)
            with tab2:
                st.code(st.session_state.last_mermaid, language="text")
                st.download_button(
                    "⬇️ Download Mermaid Code",
                    data=st.session_state.last_mermaid,
                    file_name=f"{st.session_state.last_diagram.replace(' ','_')}.mmd",
                    mime="text/plain",
                    use_container_width=True,
                )
        else:
            st.markdown("""
            <div class="empty-state">
              <div style="text-align:center;color:#9ca3af;">
                <div style="font-size:3.5rem;margin-bottom:1rem;">📊</div>
                <p style="font-size:1rem;font-weight:600;color:#6b7280;margin:0;">
                  Your diagram will appear here
                </p>
                <p style="font-size:0.82rem;color:#9ca3af;margin-top:0.4rem;">
                  Describe your system and click Generate
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GUIDED MODE
# ─────────────────────────────────────────────
else:
    st.markdown("#### 🧭 Guided System Builder")
    st.markdown("""<p style="font-size:0.9rem;color:#6b7280;font-weight:500;
        margin-bottom:1.5rem;">Answer a few questions and we'll build your diagram step by step.</p>""",
        unsafe_allow_html=True)

    # Progress bar
    step = st.session_state.guided_step
    total = len(GUIDED_QUESTIONS)
    progress = step / total
    st.progress(progress, text=f"Step {step}/{total}")

    if step < total:
        q_key, q_text = GUIDED_QUESTIONS[step]
        st.markdown(f"""<div class="card">
            <p style="font-size:0.78rem;font-weight:700;color:#6366f1;
            text-transform:uppercase;letter-spacing:0.06em;margin:0 0 0.5rem;">
            Question {step+1} of {total}</p>
            <p style="font-size:1.05rem;font-weight:700;color:#1a1a2e;margin:0;">{q_text}</p>
        </div>""", unsafe_allow_html=True)

        answer = st.text_input("Your answer", placeholder="Type here...", key=f"guided_{step}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("← Back", use_container_width=True) and step > 0:
                st.session_state.guided_step -= 1
                st.rerun()
        with col_b:
            if st.button("Next →", use_container_width=True):
                if answer.strip():
                    st.session_state.guided_answers[q_key] = answer.strip()
                    st.session_state.guided_step += 1
                    st.rerun()
                else:
                    st.warning("Please provide an answer before continuing.")

    else:
        # All questions answered — build prompt
        answers = st.session_state.guided_answers
        st.markdown("#### ✅ Review Your Answers")
        for q_key, q_text in GUIDED_QUESTIONS:
            val = answers.get(q_key, "—")
            st.markdown(f"""<div class="step-badge">
                <span style="font-size:0.75rem;color:#6b7280;font-weight:600;">{q_text}</span><br/>
                <span style="color:#1a1a2e;font-weight:600;">{val}</span>
            </div>""", unsafe_allow_html=True)

        structured_input = f"""
System: {answers.get('system_name','')}
Type: {answers.get('system_type','')}
Actors: {answers.get('actors','')}
Core Actions: {answers.get('core_actions','')}
Goal: {answers.get('goal','')}
        """.strip()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔁 Start Over", use_container_width=True):
                st.session_state.guided_step = 0
                st.session_state.guided_answers = {}
                st.session_state.last_mermaid = ""
                st.session_state.last_steps = []
                st.rerun()
        with col2:
            if st.button("✨ Generate Diagram", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("Please enter your Gemini API key in the sidebar.")
                else:
                    with st.spinner("⚙️ Building your diagram..."):
                        try:
                            raw = call_gemini(
                                st.session_state.api_key,
                                build_gemini_prompt(structured_input, diagram_type)
                            )
                            data = extract_json(raw)
                            st.session_state.last_diagram   = data.get("system_title", answers.get("system_name",""))
                            st.session_state.last_mermaid   = data.get("mermaid_code", "")
                            st.session_state.last_steps     = data.get("steps", [])
                            st.session_state.last_actors    = data.get("actors", [])
                            st.session_state.last_processes = data.get("processes", [])
                            st.session_state.history.append({
                                "input": answers.get("system_name",""),
                                "title": data.get("system_title",""),
                                "mermaid": data.get("mermaid_code",""),
                            })
                        except Exception as e:
                            st.error(f"Gemini error: {e}")

        if st.session_state.last_mermaid:
            st.markdown("---")
            st.markdown(f"#### 📊 {st.session_state.last_diagram}")
            tab1, tab2 = st.tabs(["🗺️ Visual Diagram", "📝 Mermaid Code"])
            with tab1:
                render_mermaid(st.session_state.last_mermaid)
            with tab2:
                st.code(st.session_state.last_mermaid, language="text")
                st.download_button(
                    "⬇️ Download Mermaid Code",
                    data=st.session_state.last_mermaid,
                    file_name=f"{st.session_state.last_diagram.replace(' ','_')}.mmd",
                    mime="text/plain",
                    use_container_width=True,
                )

            if st.session_state.last_steps:
                st.markdown("#### 📋 Process Steps")
                for step_item in st.session_state.last_steps:
                    st.markdown(f'<div class="step-badge">→ {step_item}</div>', unsafe_allow_html=True)
