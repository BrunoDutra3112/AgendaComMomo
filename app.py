# ── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* FUNDO */
.stApp {
    background: linear-gradient(
        135deg,
        #fff5f7 0%,
        #fef9f0 50%,
        #f0f4ff 100%
    );
}

/* TITULOS */
.main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.7rem;
    text-align: center;
    color: #b5405a;
    margin-bottom: 0.2rem;
}

.sub-title {
    text-align: center;
    color: #7c5d68;
    margin-bottom: 2rem;
    font-size: 1rem;
}

/* LABELS DOS INPUTS */
label,
.stTextInput label,
.stTextArea label,
.stDateInput label,
.stTimeInput label,
.stSelectbox label,
.stMultiSelect label,
.stNumberInput label {
    color: #5e3d48 !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* TEXTO DOS INPUTS */
input,
textarea,
select {
    color: #ffffff !important;
}

/* PLACEHOLDER */
input::placeholder,
textarea::placeholder {
    color: #9d9d9d !important;
}

/* EXPANDER */
.streamlit-expanderHeader {
    color: #5e3d48 !important;
    font-weight: 600 !important;
}

/* CABEÇALHOS */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #b5405a;
    margin-top: 1.8rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #f3cbd5;
    padding-bottom: 0.3rem;
}

/* CARDS */
.event-card {
    background: white;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid #f48fb1;
    box-shadow: 0 3px 14px rgba(0,0,0,0.05);
    transition: 0.2s;
}

.event-card:hover {
    transform: translateY(-2px);
}

.event-card.past {
    opacity: 0.75;
    border-left-color: #cccccc;
}

.event-title {
    font-size: 1.02rem;
    font-weight: 600;
    color: #2d1f2e;
    margin-bottom: 0.25rem;
}

.event-meta {
    font-size: 0.84rem;
    color: #7b6570;
}

/* BOTÕES */
div[data-testid="stButton"] button {
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
}

/* FORM */
div[data-testid="stForm"] {
    background: white;
    border-radius: 22px;
    padding: 1.5rem;
    box-shadow: 0 5px 24px rgba(0,0,0,0.05);
}

/* INPUTS */
.stTextInput input,
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 12px !important;
    border: 1.5px solid #ead4da !important;
    background: #ffffff !important;
    color: #2d1f2e !important;
}

/* TEXTO SELECT */
.stSelectbox div[data-baseweb="select"] * {
    color: #2d1f2e !important;
}

/* TEXTO DATE/TIME */
.stDateInput * ,
.stTimeInput * {
    color: #2d1f2e !important;
}

/* ALERTAS */
.stAlert {
    border-radius: 14px !important;
}

/* TABS */
button[data-baseweb="tab"] {
    color: #6b4a56 !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #b5405a !important;
}

</style>
""", unsafe_allow_html=True)
