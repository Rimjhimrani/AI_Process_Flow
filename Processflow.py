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
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e8e8f0;
}

/* App background */
.stApp {
    background: #0a0a0f;
}

/* Header */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 2rem;
}
.main-header h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    background: linear-gradient(135deg, #a78bfa, #38bdf8, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -1px;
}
.main-header p {
    color: #6b7280;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

/* Cards */
.card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

/* Prompt quality badge */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.badge-weak   { background: #3f1212; color: #f87171; border: 1px solid #7f1d1d; }
.badge-medium { background: #3f2a08; color: #fbbf24; border: 1px solid #92400e; }
.badge-strong { background: #083f1e; color: #34d399; border: 1px solid #065f46; }

/* Mode toggle buttons */
.stRadio > div { gap: 0.5rem; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d0d14;
    border-right: 1px solid #1e1e2e;
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.6rem 1.5rem;
    transition: opacity 0.2s;
    width: 100%;
}
.stButton > button:hover { opacity: 0.85; }

/* Select box */
.stSelectbox > div > div {
    background: #111118 !important;
    border-color: #1e1e2e !important;
    color: #e8e8f0 !important;
    border-radius: 8px !important;
}

/* Info / warning / success boxes */
.stAlert {
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* Code blocks */
.stCodeBlock {
    border-radius: 8px !important;
    border: 1px solid #1e1e2e !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #111118;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e1e2e;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #6b7280;
    border-radius: 6px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #1e1e2e !important;
    color: #a78bfa !important;
}

/* Divider */
hr { border-color: #1e1e2e !important; }

/* Mermaid container */
.mermaid-wrapper {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    overflow-x: auto;
}

/* Step badges */
.step-badge {
    background: #1e1e2e;
    border: 1px solid #2d2d40;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #c4b5fd;
}

/* Clarity meter */
.clarity-bar-bg {
    background: #1e1e2e;
    border-radius: 20px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin: 0.5rem 0;
}
.clarity-bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 0.5s ease;
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
    <div class="mermaid-wrapper">
      <div id="mermaid-graph" style="text-align:center;"></div>
    </div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {{
          primaryColor: '#1e1e2e',
          primaryTextColor: '#e8e8f0',
          primaryBorderColor: '#a78bfa',
          lineColor: '#6b7280',
          secondaryColor: '#111118',
          tertiaryColor: '#0a0a0f',
          edgeLabelBackground: '#1e1e2e',
          clusterBkg: '#1e1e2e',
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
            st.markdown(f"""<div style="font-family:'Space Mono',monospace;font-size:0.7rem;
                color:#6b7280;padding:0.4rem 0;border-bottom:1px solid #1e1e2e;">
                {i+1}. {h['input'][:40]}…</div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#6b7280;font-size:0.8rem;'>No history yet.</p>", unsafe_allow_html=True)

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>DiagramAI</h1>
  <p>Powered by Google Gemini · Turn vague ideas into clear system diagrams</p>
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
                <span style="font-family:'Space Mono',monospace;font-size:0.8rem;color:#6b7280;">
                  Prompt Clarity
                </span>
                <span class="badge {badge_cls}">{label.upper()} · {clarity}%</span>
              </div>
              <div class="clarity-bar-bg">
                <div class="clarity-bar-fill" style="width:{clarity}%;background:{bar_color};"></div>
              </div>
              {'<p style="font-family:Space Mono,monospace;font-size:0.75rem;color:#f87171;margin-top:0.3rem;">⚠️ Prompt is vague — Gemini will auto-improve it before generating.</p>' if clarity < 40 else ''}
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
                st.markdown(f"""<div style="font-family:'Space Mono',monospace;font-size:0.8rem;
                    color:#c4b5fd;line-height:1.6;">{st.session_state.auto_refined}</div>""",
                    unsafe_allow_html=True)

        # System breakdown
        if st.session_state.last_steps:
            st.markdown("#### 🧩 System Breakdown")
            if hasattr(st.session_state, 'last_actors') and st.session_state.get("last_actors"):
                st.markdown(f"""<p style="font-family:'Space Mono',monospace;font-size:0.78rem;
                    color:#6b7280;margin-bottom:0.3rem;">👤 ACTORS</p>""", unsafe_allow_html=True)
                actors_str = " · ".join([f"<span style='color:#a78bfa'>{a}</span>"
                                         for a in st.session_state.get("last_actors",[])])
                st.markdown(f"<p style='font-size:0.85rem;'>{actors_str}</p>", unsafe_allow_html=True)

            st.markdown(f"""<p style="font-family:'Space Mono',monospace;font-size:0.78rem;
                color:#6b7280;margin:0.6rem 0 0.3rem;">📋 PROCESS STEPS</p>""", unsafe_allow_html=True)
            for step in st.session_state.last_steps:
                st.markdown(f'<div class="step-badge">→ {step}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### 📊 Diagram Output")
        if st.session_state.last_mermaid:
            st.markdown(f"""<p style="font-family:'Space Mono',monospace;font-size:0.78rem;
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
            <div style="height:400px;display:flex;align-items:center;justify-content:center;
                border:1px dashed #1e1e2e;border-radius:12px;">
              <div style="text-align:center;color:#6b7280;">
                <div style="font-size:3rem;margin-bottom:1rem;">🧠</div>
                <p style="font-family:'Space Mono',monospace;font-size:0.85rem;">
                  Your diagram will appear here
                </p>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GUIDED MODE
# ─────────────────────────────────────────────
else:
    st.markdown("#### 🧭 Guided System Builder")
    st.markdown("""<p style="font-family:'Space Mono',monospace;font-size:0.8rem;color:#6b7280;
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
            <p style="font-family:'Space Mono',monospace;font-size:0.8rem;color:#a78bfa;margin:0 0 0.5rem;">
            Question {step+1} of {total}</p>
            <p style="font-size:1.05rem;font-weight:600;margin:0;">{q_text}</p>
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
                <span style="color:#6b7280;">{q_text}</span><br/>
                <span style="color:#e8e8f0;">{val}</span>
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
