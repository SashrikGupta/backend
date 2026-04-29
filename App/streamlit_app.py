"""
Streamlit Chat Application for Product Review Analysis.

Integrates with the LangGraph MainGraph backend to provide:
- Session initialization with product ID selection
- Multi-turn conversational interface
- Session persistence with image artifact handling
- Sidebar session management and resume
"""

import sys
import os
from pathlib import Path

# Ensure the project root (backend/) is on sys.path so that
# "from App.*" and "from Core.*" imports work on Streamlit Cloud.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import re
import streamlit as st
from dotenv import load_dotenv

# ── Load environment before any Core imports ──
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=False)

# On Streamlit Cloud, secrets are set via the dashboard.
# Bridge them into os.environ so Core/LLMS/factory.py can read them.
_SECRET_KEYS = [
    "GEMINI_KEY_COLLECTION",
    "GROQ_KEY_COLLECTION",
    "OPEN_ROUTER_KEY_COLLECTION",
    "E2B_API_KEY",
    "LANGSMITH_API_KEY",
    "LANGSMITH_TRACING_V2",
    "LANGSMITH_PROJECT",
    "LANGSMITH_ENDPOINT",
]
try:
    for _key in _SECRET_KEYS:
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = str(st.secrets[_key])
except Exception:
    pass  # st.secrets unavailable locally — .env handles it

from langchain.messages import HumanMessage, AIMessage  # noqa: E402

from App.session_manager import (  # noqa: E402
    create_session,
    save_message,
    load_session,
    rehydrate_messages,
    list_sessions,
    generate_run_id,
    SESSIONS_DIR,
)
from App.styles import get_custom_css  # noqa: E402
from pathlib import Path

# Avatar Icons
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
USER_AVATAR = str(ASSETS_DIR / "user_avatar.png")
AI_AVATAR = str(ASSETS_DIR / "ai_avatar.png")



# ─────────────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Review Insight AI",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Inject custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# Graph Initialization (Cached — runs once per app lifecycle)
# ─────────────────────────────────────────────────────────────────────


@st.cache_resource(show_spinner="Initializing AI models...")
def init_graph():
    """
    Build the LangGraph main graph and the runtime config needed
    by the tools (sandbox_graph, plot_agent).

    Returns:
        (compiled_graph, runtime_config_dict)
    """
    from Core.Workflows.MainGraph import build_main_graph
    from Core.LLMS import build_llm_factory
    from Core.Workflows.SandBoxGraph import get_sandbox_graph
    from Core.Workflows.PlotGraph import get_plotting_agent

    # Build the compiled graph
    graph = build_main_graph()

    # Build runtime config separately (tools access these via config["configurable"])
    llm_factory = build_llm_factory()
    sandbox_graph = get_sandbox_graph(llm_factory["coder_llm_data_analysis"][0])
    sandbox_graph_plot = get_sandbox_graph(llm_factory["coder_llm_plotting"][0])
    plot_agent = get_plotting_agent(
        sandbox_graph=sandbox_graph_plot,
        prompt_llm=llm_factory["planner_llm"][0],
        image_llm=llm_factory["image_llm"][0],
    )

    runtime_config = {
        "configurable": {
            "sandbox_graph": sandbox_graph,
            "plot_agent": plot_agent,
        }
    }

    return graph, runtime_config


# ─────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────


def _init_session_state():
    """Initialize all required session state keys with defaults."""
    defaults = {
        "current_session_id": None,
        "product_id": None,
        "messages": [],  # Display messages: [{"role": str, "content": str}, ...]
        "langgraph_messages": [],  # LangChain message objects for graph state
        "session_locked": False,  # True once a session is active
        "is_processing": False,  # True while graph is running
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_session_state()


# ─────────────────────────────────────────────────────────────────────
# Message Rendering
# ─────────────────────────────────────────────────────────────────────

# Pattern to find artifact image paths in processed responses
IMAGE_PATH_PATTERN = re.compile(r"(/artifacts/image_\d+\.\w+)")


def render_message_content(session_id: str, content: str):
    """
    Render message content with support for inline artifact images.

    Splits content on image path references and renders text parts
    with st.markdown and image parts with st.image.
    """
    if not session_id:
        st.markdown(content)
        return

    parts = IMAGE_PATH_PATTERN.split(content)

    for part in parts:
        if IMAGE_PATH_PATTERN.match(part):
            # It's an image path — resolve and display
            clean_path = part.lstrip("/")
            full_path = SESSIONS_DIR / session_id / clean_path
            if full_path.exists():
                st.image(str(full_path), use_container_width=True)
            else:
                st.caption(f"*Image not found: {part}*")
        else:
            stripped = part.strip()
            if stripped:
                st.markdown(stripped)


# ─────────────────────────────────────────────────────────────────────
# Sidebar — Session Management
# ─────────────────────────────────────────────────────────────────────


def render_sidebar():
    """Render the sidebar with session list and new session button."""
    with st.sidebar:
        # ── Header ──
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0;">
                <div class="welcome-title" style="font-size: 1.3rem;">Review Insight AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── New Session Button ──
        if st.button("New Session ", use_container_width=True, key="btn_new_session", type="primary"):
            st.session_state.current_session_id = None
            st.session_state.product_id = None
            st.session_state.messages = []
            st.session_state.langgraph_messages = []
            st.session_state.session_locked = False
            st.rerun()

        st.divider()

        # ── Session List ──
        sessions = list_sessions()

        if sessions:
            st.markdown(
                "<p style='color: #9d9db5; font-size: 0.75rem; text-transform: uppercase; "
                "letter-spacing: 0.08em; margin-bottom: 0.5rem;'>Recent Sessions</p>",
                unsafe_allow_html=True,
            )

            for session in sessions:
                sid = session["session_id"]
                pid = session["product_id"]
                msg_count = session["message_count"]
                is_active = sid == st.session_state.current_session_id
                
                if is_active:
                    st.markdown(
                        f"""
                        <div class="session-card active">
                            <div class="session-id">
                                Session {sid[:6]}
                                <span class="product-badge">Product #{pid}</span>
                            </div>
                            <div class="session-meta">
                                {msg_count} message{'s' if msg_count != 1 else ''} • Active
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(
                        f" Session {sid[:6]} (Prod {pid})",
                        key=f"load_{sid}",
                        use_container_width=True,
                    ):
                        _load_existing_session(sid)
                        st.rerun()
        else:
            st.markdown(
                "<p style='color: #6b6b80; text-align: center; padding: 1rem; "
                "font-size: 0.85rem;'>No sessions yet.<br>Start a new one!</p>",
                unsafe_allow_html=True,
            )


def _load_existing_session(session_id: str):
    """Load an existing session into session state."""
    session_data = load_session(session_id)
    if session_data is None:
        st.error(f"Session {session_id} not found.")
        return

    st.session_state.current_session_id = session_id
    st.session_state.product_id = session_data["product_id"]
    st.session_state.session_locked = True

    # Rebuild display messages
    st.session_state.messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in session_data.get("messages", [])
    ]

    # Rehydrate LangChain message objects for graph state
    st.session_state.langgraph_messages = rehydrate_messages(session_data)


# ─────────────────────────────────────────────────────────────────────
# Welcome / Session Initialization Screen
# ─────────────────────────────────────────────────────────────────────


def render_welcome_screen():
    """Render the pre-chat product selection screen."""
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-title">Welcome to Review Insight AI</div>
            <div class="welcome-subtitle">
                Analyze product reviews with AI-powered insights and visualizations.<br>
                Select a product to begin your analysis session.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Product Selection Card ──
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form(key="init_form", clear_on_submit=False):
            st.markdown("<h3 style='text-align: center; font-weight: 600; margin-bottom: 1.5rem;'>Select Product</h3>", unsafe_allow_html=True)

            # Option 1: Enter Product ID
            product_id = st.number_input(
                "Product ID",
                min_value=0,
                value=0,
                step=1,
                help="Enter the product ID to analyze. If no analysis exists, it will be created automatically.",
            )

            st.markdown(
                "<p style='color: #6b6b80; font-size: 0.85rem; text-align: center; margin: 1.5rem 0;'>— OR —</p>",
                unsafe_allow_html=True,
            )

            # Option 2: CSV Upload
            uploaded = st.file_uploader(
                "Upload product CSV",
                type=["csv"],
                help="Upload a CSV file with product review data",
            )

            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

            # Start Session
            submit = st.form_submit_button("Start Session", use_container_width=True, type="primary")
            
            if submit:
                if uploaded is not None:
                    import time
                    with st.spinner("Processing reviews... This may take a while for large datasets."):
                        while True:
                            time.sleep(1)
                session_id = create_session(product_id)
                st.session_state.current_session_id = session_id
                st.session_state.product_id = product_id
                st.session_state.messages = []
                st.session_state.langgraph_messages = []
                st.session_state.session_locked = True
                st.rerun()


# ─────────────────────────────────────────────────────────────────────
# Chat Interface
# ─────────────────────────────────────────────────────────────────────


def render_chat_interface():
    """Render the main chat interface with message history and input."""
    session_id = st.session_state.current_session_id
    product_id = st.session_state.product_id

    # ── Header ──
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
            <div>
                <span style="font-size: 1.1rem; font-weight: 600; color: #e8e8f0;">
                    Session {session_id}
                </span>
                <span class="product-badge" style="margin-left: 8px;">Product #{product_id}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Message History ──
    for msg in st.session_state.messages:
        avatar = USER_AVATAR if msg["role"] == "human" else AI_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            render_message_content(session_id, msg["content"])

    # ── Chat Input ──
    if prompt := st.chat_input(
        "Ask about the product reviews...",
        disabled=st.session_state.is_processing,
    ):
        _handle_user_message(prompt)


def _handle_user_message(user_input: str):
    """Process a new user message through the LangGraph pipeline."""
    session_id = st.session_state.current_session_id
    product_id = st.session_state.product_id

    # ── 1. Display user message immediately ──
    st.session_state.messages.append({"role": "human", "content": user_input})
    with st.chat_message("human", avatar=USER_AVATAR):
        st.markdown(user_input)

    # ── 2. Save human message to history ──
    save_message(session_id, "human", user_input)

    # ── 3. Add to LangGraph message list ──
    human_msg = HumanMessage(content=user_input)
    st.session_state.langgraph_messages.append(human_msg)

    # ── 4. Invoke LangGraph pipeline ──
    with st.chat_message("assistant", avatar=AI_AVATAR):
        # Show thinking indicator
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(
            """
            <div class="thinking-indicator">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <span>Analyzing...</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            st.session_state.is_processing = True

            # Get cached graph and config
            graph, runtime_config = init_graph()

            # Generate run_id for this invocation
            run_id = generate_run_id(session_id)

            # Build the graph input state
            graph_state = {
                "messages": list(st.session_state.langgraph_messages),
                "product_id": product_id,
                "run_id": run_id,
            }

            # Invoke the graph
            result = graph.invoke(graph_state, config=runtime_config)

            # ── 5. Extract the final AI response ──
            # The last message should be the AIMessage from the reporter node
            result_messages = result.get("messages", [])
            ai_response_content = ""

            # Walk backwards to find the last AIMessage (reporter output)
            for msg in reversed(result_messages):
                if isinstance(msg, AIMessage) and msg.content:
                    ai_response_content = msg.content
                    break

            if not ai_response_content:
                ai_response_content = "I wasn't able to generate a response. Please try again."

            # ── 6. Process images in the response ──
            from App.session_manager import process_ai_response

            processed_content = process_ai_response(session_id, ai_response_content)

            # ── 7. Clear thinking indicator and render response ──
            thinking_placeholder.empty()
            render_message_content(session_id, processed_content)

            # ── 8. Update session state ──
            ai_msg = AIMessage(content=processed_content)
            st.session_state.langgraph_messages.append(ai_msg)
            st.session_state.messages.append(
                {"role": "ai", "content": processed_content}
            )

            # ── 9. Save AI response to history ──
            # Note: save_message also processes images, but since we already
            # processed them, we save the processed content directly
            session_dir = SESSIONS_DIR / session_id
            history_path = session_dir / "history.json"

            import json

            with open(history_path, "r") as f:
                history = json.load(f)

            history["messages"].append({
                "role": "ai",
                "content": processed_content,
            })

            with open(history_path, "w") as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"An error occurred: {str(e)}")

            # Still save the error as a system message for debugging
            error_content = f"Error: {str(e)}"
            st.session_state.messages.append(
                {"role": "ai", "content": error_content}
            )

        finally:
            st.session_state.is_processing = False


# ─────────────────────────────────────────────────────────────────────
# Main App Layout
# ─────────────────────────────────────────────────────────────────────


def main():
    """Main entry point — orchestrate sidebar + main content area."""
    render_sidebar()

    if st.session_state.current_session_id is None:
        render_welcome_screen()
    else:
        render_chat_interface()


if __name__ == "__main__":
    main()
else:
    # When run via `streamlit run App/streamlit_app.py`
    main()
