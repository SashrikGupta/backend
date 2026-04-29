"""
Premium dark-mode CSS styles for the Streamlit Chat Application.

Provides a glassmorphism-inspired dark theme with modern typography,
gradient accents, and micro-animations for a polished UI.
"""


def get_custom_css() -> str:
    """Return the full custom CSS string for the Streamlit app."""
    return """
    <style>
    /* ─────────────── Google Fonts ─────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ─────────────── Global ─────────────── */
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-tertiary: #1a1a2e;
        --bg-glass: rgba(26, 26, 46, 0.6);
        --bg-glass-hover: rgba(26, 26, 46, 0.85);
        --text-primary: #e8e8f0;
        --text-secondary: #9d9db5;
        --text-muted: #6b6b80;
        --accent-purple: #7c3aed;
        --accent-blue: #3b82f6;
        --accent-gradient: linear-gradient(135deg, #7c3aed, #3b82f6);
        --accent-gradient-hover: linear-gradient(135deg, #8b5cf6, #60a5fa);
        --border-subtle: rgba(255, 255, 255, 0.06);
        --border-accent: rgba(124, 58, 237, 0.3);
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        --shadow-glow: 0 0 20px rgba(124, 58, 237, 0.15);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
        --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ─────────────── Main Container ─────────────── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: var(--bg-primary) !important;
        color: var(--text-primary);
    }

    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        max-width: 900px !important;
    }

    /* ─────────────── Sidebar ─────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: var(--text-secondary) !important;
    }

    /* ─────────────── Session Cards ─────────────── */
    .session-card {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 12px 16px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: var(--transition);
    }

    .session-card:hover {
        background: var(--bg-glass-hover);
        border-color: var(--border-accent);
        box-shadow: var(--shadow-glow);
        transform: translateY(-1px);
    }

    .session-card.active {
        background: var(--bg-glass-hover);
        border-color: var(--accent-purple);
        box-shadow: var(--shadow-glow);
    }

    .session-card .session-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-primary);
        font-weight: 500;
    }

    .session-card .session-meta {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: 4px;
    }

    .product-badge {
        display: inline-block;
        background: var(--accent-gradient);
        color: white;
        font-size: 0.68rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 100px;
        margin-left: 6px;
        letter-spacing: 0.03em;
    }

    /* ─────────────── Chat Messages ─────────────── */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
    }

    div[data-testid="stChatMessage"] {
        padding: 0.75rem 0 !important;
    }

    /* Human messages */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: transparent !important;
    }

    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 12px 16px;
    }

    /* AI messages */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
        background: rgba(124, 58, 237, 0.05);
        border: 1px solid rgba(124, 58, 237, 0.1);
        border-radius: var(--radius-md);
        padding: 12px 16px;
    }

    /* ─────────────── Chat Input ─────────────── */
    .stChatInput {
        background: var(--bg-secondary) !important;
    }

    .stChatInput > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-lg) !important;
        transition: var(--transition);
    }

    .stChatInput > div:focus-within {
        border-color: var(--accent-purple) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    .stChatInput textarea {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ─────────────── Buttons ─────────────── */
    /* Primary buttons (New Session, Start Session) */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button,
    .stButton > button[kind="primaryFormSubmit"] {
        background: var(--accent-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: var(--transition) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover,
    .stButton > button[kind="primaryFormSubmit"]:hover {
        background: var(--accent-gradient-hover) !important;
        box-shadow: var(--shadow-md), var(--shadow-glow) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="primary"]:active,
    .stFormSubmitButton > button:active,
    .stButton > button[kind="primaryFormSubmit"]:active {
        transform: translateY(0) !important;
    }

    /* Secondary / normal buttons */
    .stButton > button:not([kind="primary"]):not([kind="primaryFormSubmit"]),
    .stFormSubmitButton > button:not([kind="primarySubmit"]) {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: var(--transition) !important;
    }

    .stButton > button:not([kind="primary"]):not([kind="primaryFormSubmit"]):hover {
        background: var(--bg-glass-hover) !important;
        border-color: var(--border-accent) !important;
    }

    /* Sidebar secondary buttons (Session history) - make them left-aligned and clickable-area-friendly */
    section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
        width: 100%;
        justify-content: flex-start !important;
        padding: 0.75rem 1rem !important;
        border-radius: var(--radius-md) !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.4rem !important;
    }

    /* ─────────────── Inputs / Selects ─────────────── */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition) !important;
    }

    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-purple) !important;
        box-shadow: var(--shadow-glow) !important;
    }

    /* ─────────────── Dividers ─────────────── */
    hr {
        border-color: var(--border-subtle) !important;
        margin: 1rem 0 !important;
    }

    /* ─────────────── Expander ─────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-tertiary) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    /* ─────────────── Spinner ─────────────── */
    .stSpinner > div {
        border-top-color: var(--accent-purple) !important;
    }

    /* ─────────────── File Uploader ─────────────── */
    .stFileUploader > div {
        background: var(--bg-tertiary) !important;
        border: 1px dashed var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ─────────────── Toast ─────────────── */
    .stToast {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-md) !important;
    }

    /* ─────────────── Typing Animation ─────────────── */
    @keyframes pulse-glow {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }

    .thinking-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        color: var(--text-muted);
        font-size: 0.85rem;
    }

    .thinking-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent-purple);
        animation: pulse-glow 1.4s ease-in-out infinite;
    }

    .thinking-dot:nth-child(2) { animation-delay: 0.2s; }
    .thinking-dot:nth-child(3) { animation-delay: 0.4s; }

    /* ─────────────── Welcome Screen ─────────────── */
    .welcome-container {
        text-align: center;
        padding: 4rem 2rem;
    }

    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .welcome-subtitle {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* ─────────────── Product Selection Form ─────────────── */
    [data-testid="stForm"] {
        background: var(--bg-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-xl) !important;
        padding: 2.5rem !important;
        max-width: 550px;
        margin: 0 auto;
        box-shadow: var(--shadow-lg);
    }
    
    [data-testid="stForm"] h3 {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* ─────────────── Scrollbar ─────────────── */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--bg-tertiary);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* ─────────────── Status indicator ─────────────── */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }

    .status-dot.online { background: #22c55e; }
    .status-dot.processing { background: #f59e0b; animation: pulse-glow 1s ease-in-out infinite; }
    .status-dot.error { background: #ef4444; }

    /* ─────────────── Image display ─────────────── */
    .stImage {
        border-radius: var(--radius-md) !important;
        overflow: hidden;
    }

    .stImage img {
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-md);
    }
    </style>
    """
