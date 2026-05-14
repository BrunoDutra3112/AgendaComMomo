import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date
import pytz

# ── CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nossa Agenda 💕",
    page_icon="💕",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── RESTAURA SESSÃO ─────────────────────────────────────────────────────
if "access_token" in st.session_state:
    try:
        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )
    except:
        pass

BR_TZ = pytz.timezone("America/Sao_Paulo")

CATEGORIAS = {
    "💕 Encontro": "encontro",
    "🍽️ Restaurante": "restaurante",
    "✈️ Viagem": "viagem",
    "🎬 Cinema": "cinema",
    "🎂 Aniversário": "aniversario",
    "🛍️ Compras": "compras",
    "🏠 Casa": "casa",
    "📅 Outro": "outro",
}

# ── CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
}

.stApp {
    background: linear-gradient(135deg, #fff5f7 0%, #fef9f0 50%, #f0f4ff 100%);
}

.main-title {
    font-size: 2.6rem;
    text-align: center;
    color: #b5405a;
    margin-bottom: 0.2rem;
}

.sub-title {
    text-align: center;
    color: #a07080;
    margin-bottom: 2rem;
}

.event-card {
    background: white;
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.8rem;
    border-left: 4px solid #f48fb1;
    box-shadow: 0 2px 12px rgba(180,80,100,0.07);
}

.event-card.past {
    border-left-color: #ccc;
    opacity: 0.65;
}

.event-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #2d1f2e;
}

.event-meta {
    font-size: 0.82rem;
    color: #8a6575;
}

.section-header {
    font-size: 1.4rem;
    color: #b5405a;
    margin: 1.5rem 0 0.8rem;
    border-bottom: 1px solid #f8d7e0;
    padding-bottom: 0.4rem;
}

div[data-testid="stButton"] button {
    border-radius: 12px !important;
    border: none !important;
}

div[data-testid="stForm"] {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(180,80,100,0.08);
}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────────────
def get_user():
    return st.session_state.get("user")

def ensure_profile(user_id, email, nome=None):
    try:
        profile = (
            supabase.table("profiles")
            .select("*")
            .eq("id", user_id)
            .execute()
        )

        if not profile.data:
            supabase.table("profiles").insert({
                "id": user_id,
                "nome": nome or email.split("@")[0],
                "email": email,
            }).execute()

            return nome or email.split("@")[0]

        return profile.data[0]["nome"]

    except Exception:
        return nome or email.split("@")[0]

def sign_up(email, password, nome):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if res.user:
            ensure_profile(res.user.id, email, nome)
            return True, "Conta criada! Verifique seu e-mail."

        return False, "Erro ao criar conta."

    except Exception as e:
        return False, str(e)

def sign_in(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user:
            st.session_state["user"] = res.user
            st.session_state["session"] = res.session

            # salva tokens
            st.session_state["access_token"] = res.session.access_token
            st.session_state["refresh_token"] = res.session.refresh_token

            nome = ensure_profile(res.user.id, email)
            st.session_state["nome"] = nome

            return True, ""

        return False, "E-mail ou senha incorretos."

    except Exception as e:
        return False, str(e)

def sign_out():
    try:
        supabase.auth.sign_out()
    except:
        pass

    for k in [
        "user",
        "session",
        "nome",
        "access_token",
        "refresh_token"
    ]:
        st.session_state.pop(k, None)

def load_events():
    now = datetime.now(BR_TZ).isoformat()

    upcoming = (
        supabase.table("eventos")
        .select("*, profiles(nome)")
        .gte("data_hora", now)
        .order("data_hora")
        .execute()
    )

    past = (
        supabase.table("eventos")
        .select("*, profiles(nome)")
        .lt("data_hora", now)
        .order("data_hora", desc=True)
        .limit(10)
        .execute()
    )

    return upcoming.data or [], past.data or []

def add_event(titulo, descricao, data_hora, categoria, user_id):
    supabase.table("eventos").insert({
        "titulo": titulo,
        "descricao": descricao,
        "data_hora": data_hora.isoformat(),
        "categoria": categoria,
        "user_id": user_id,
    }).execute()

def delete_event(event_id):
    try:
        (
            supabase.table("eventos")
            .delete()
            .eq("id", event_id)
            .execute()
        )

        st.success("Evento deletado! 🗑️")

    except Exception as e:
        st.error(f"Erro ao deletar: {e}")

# ── AUTH ───────────────────────────────────────────────────────────────
def auth_page():
    st.markdown(
        '<div class="main-title">Nossa Agenda 💕</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">o calendário de vocês dois 💕</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_cadastro = st.tabs(["Entrar", "Criar conta"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

            submitted = st.form_submit_button(
                "Entrar 💕",
                use_container_width=True
            )

            if submitted:
                ok, msg = sign_in(email, senha)

                if ok:
                    st.rerun()
                else:
                    st.error(msg)

    with tab_cadastro:
        with st.form("signup_form"):
            nome = st.text_input("Seu nome")
            email2 = st.text_input("E-mail")
            senha2 = st.text_input("Senha", type="password")

            submitted2 = st.form_submit_button(
                "Criar conta",
                use_container_width=True
            )

            if submitted2:
                ok, msg = sign_up(email2, senha2, nome)

                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

# ── MAIN ───────────────────────────────────────────────────────────────
def main_app():
    user = get_user()
    nome = st.session_state.get("nome", "você")

    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            '<div class="main-title">Nossa Agenda 💕</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="sub-title">Olá, {nome}!</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.write("")
        st.write("")

        if st.button("Sair", use_container_width=True):
            sign_out()
            st.rerun()

    # ── NOVO EVENTO ───────────────────────────────────────────────
    with st.expander("➕ Adicionar novo evento"):

        with st.form("novo_evento"):

            titulo = st.text_input("Título do evento *")

            col_a, col_b = st.columns(2)

            with col_a:
                data = st.date_input(
                    "Data *",
                    min_value=date.today()
                )

            with col_b:
                hora = st.time_input("Hora *")

            categoria_label = st.selectbox(
                "Categoria",
                list(CATEGORIAS.keys())
            )

            descricao = st.text_area(
                "Descrição / observações",
                height=80
            )

            salvar = st.form_submit_button(
                "Salvar evento 💕",
                use_container_width=True
            )

            if salvar:
                if not titulo:
                    st.error("Informe um título.")
                else:
                    dt = datetime.combine(data, hora)
                    dt = BR_TZ.localize(dt)

                    add_event(
                        titulo,
                        descricao,
                        dt,
                        CATEGORIAS[categoria_label],
                        user.id
                    )

                    st.success("Evento adicionado! 🎉")
                    st.rerun()

    # ── EVENTOS ─────────────────────────────────────────────────
    upcoming, past = load_events()

    st.markdown(
        '<div class="section-header">📅 Próximos eventos</div>',
        unsafe_allow_html=True
    )

    if not upcoming:
        st.info("Nenhum evento agendado 💕")

    else:
        for ev in upcoming:

            dt = (
                datetime.fromisoformat(ev["data_hora"])
                .astimezone(BR_TZ)
            )

            criador = ev.get("profiles", {})
            criador_nome = criador.get("nome", "?")

            cat_emoji = next(
                (
                    k.split()[0]
                    for k, v in CATEGORIAS.items()
                    if v == ev.get("categoria")
                ),
                "📅"
            )

            c1, c2 = st.columns([5, 1])

            with c1:
                st.markdown(f"""
                <div class="event-card">
                    <div class="event-title">
                        {cat_emoji} {ev['titulo']}
                    </div>

                    <div class="event-meta">
                        📆 {dt.strftime('%d/%m/%Y às %H:%M')}
                        &nbsp;|&nbsp;
                        👤 {criador_nome}
                    </div>

                    {
                        "<div class='event-meta' style='margin-top:4px'>📝 "
                        + ev['descricao']
                        + "</div>"
                        if ev.get('descricao')
                        else ""
                    }
                </div>
                """, unsafe_allow_html=True)

            with c2:
                if ev.get("user_id") == user.id:

                    st.write("")
                    st.write("")

                    if st.button(
                        "🗑️",
                        key=f"del_{ev['id']}",
                        help="Deletar evento"
                    ):
                        delete_event(ev["id"])
                        st.rerun()

    # ── HISTÓRICO ───────────────────────────────────────────────
    if past:

        with st.expander(
            f"🕰️ Histórico ({len(past)} eventos)"
        ):

            for ev in past:

                dt = (
                    datetime.fromisoformat(ev["data_hora"])
                    .astimezone(BR_TZ)
                )

                criador = ev.get("profiles", {})
                criador_nome = criador.get("nome", "?")

                cat_emoji = next(
                    (
                        k.split()[0]
                        for k, v in CATEGORIAS.items()
                        if v == ev.get("categoria")
                    ),
                    "📅"
                )

                st.markdown(f"""
                <div class="event-card past">
                    <div class="event-title">
                        {cat_emoji} {ev['titulo']}
                    </div>

                    <div class="event-meta">
                        📆 {dt.strftime('%d/%m/%Y às %H:%M')}
                        &nbsp;|&nbsp;
                        👤 {criador_nome}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── ROUTER ─────────────────────────────────────────────────────────────
if get_user():
    main_app()
else:
    auth_page()
