import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date
import pytz

# ── CONFIG ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nossa Agenda 💕",
    page_icon="💕",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

BR_TZ = pytz.timezone("America/Sao_Paulo")

# ── RESTAURA SESSÃO ────────────────────────────────────────────
if "access_token" in st.session_state:

    try:

        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"]
        )

    except:
        pass

# ── CATEGORIAS ─────────────────────────────────────────────────
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

# ── CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: linear-gradient(
        135deg,
        #fff5f7 0%,
        #fef9f0 50%,
        #f0f4ff 100%
    );
}

.main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.7rem;
    text-align: center;
    color: #b5405a;
    margin-bottom: 0.2rem;
}

.sub-title {
    text-align: center;
    color: #9a7480;
    margin-bottom: 2rem;
}

.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #b5405a;
    margin-top: 1.8rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #f3cbd5;
    padding-bottom: 0.3rem;
}

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

div[data-testid="stButton"] button {
    border-radius: 12px !important;
    border: none !important;
    font-weight: 600 !important;
}

div[data-testid="stForm"] {
    background: white;
    border-radius: 22px;
    padding: 1.5rem;
    box-shadow: 0 5px 24px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# ── HELPERS ────────────────────────────────────────────────────
def get_user():
    return st.session_state.get("user")

def sign_up(email, password, nome):

    try:

        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if res.user:

            supabase.table("profiles").insert({
                "id": res.user.id,
                "nome": nome,
                "email": email
            }).execute()

            return True, "Conta criada com sucesso!"

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

            st.session_state["access_token"] = (
                res.session.access_token
            )

            st.session_state["refresh_token"] = (
                res.session.refresh_token
            )

            profile = (
                supabase.table("profiles")
                .select("*")
                .eq("id", res.user.id)
                .execute()
            )

            st.session_state["nome"] = (
                profile.data[0]["nome"]
                if profile.data
                else email
            )

            return True, ""

        return False, "Login inválido."

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
        .limit(20)
        .execute()
    )

    return upcoming.data or [], past.data or []

def add_event(
    titulo,
    descricao,
    data_hora,
    categoria,
    user_id
):

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

        st.success("Evento deletado 🗑️")

    except Exception as e:
        st.error(str(e))

# ── AUTH ───────────────────────────────────────────────────────
def auth_page():

    st.markdown(
        '<div class="main-title">Nossa Agenda 💕</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">o calendário de vocês dois</div>',
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["Entrar", "Criar conta"])

    with tab1:

        with st.form("login"):

            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

            entrar = st.form_submit_button(
                "Entrar 💕",
                use_container_width=True
            )

            if entrar:

                ok, msg = sign_in(email, senha)

                if ok:
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:

        with st.form("signup"):

            nome = st.text_input("Nome")
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")

            criar = st.form_submit_button(
                "Criar conta",
                use_container_width=True
            )

            if criar:

                ok, msg = sign_up(email, senha, nome)

                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

# ── MAIN APP ───────────────────────────────────────────────────
def main_app():

    user = get_user()

    nome = st.session_state.get("nome", "você")

    col1, col2 = st.columns([4,1])

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

        if st.button("Sair"):

            sign_out()
            st.rerun()

    # ── NOVO EVENTO ───────────────────────────────────────
    with st.expander(
        "➕ Adicionar novo evento",
        expanded=False
    ):

        with st.form("novo_evento"):

            titulo = st.text_input(
                "Título do evento *"
            )

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
                height=90
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

                    st.success("Evento salvo 🎉")
                    st.rerun()

    # ── EVENTOS ──────────────────────────────────────────
    upcoming, past = load_events()

    st.markdown(
        '<div class="section-header">📅 Próximos eventos</div>',
        unsafe_allow_html=True
    )

    if not upcoming:

        st.info(
            "Nenhum evento agendado. Que tal planejar algo juntos? 💕"
        )

    else:

        for ev in upcoming:

            dt = (
                datetime.fromisoformat(
                    ev["data_hora"]
                ).astimezone(BR_TZ)
            )

            criador = ev.get("profiles", {})

            criador_nome = (
                criador.get("nome", "?")
                if criador
                else "?"
            )

            cat_emoji = next(
                (
                    k.split()[0]
                    for k, v in CATEGORIAS.items()
                    if v == ev.get("categoria")
                ),
                "📅"
            )

            descricao_html = ""

            if ev.get("descricao"):

                descricao_html = f"""
<div class="event-meta" style="margin-top:6px;">
📝 {ev["descricao"]}
</div>
"""

            card_html = f"""
<div class="event-card">

<div class="event-title">
{cat_emoji} {ev["titulo"]}
</div>

<div class="event-meta">
📆 {dt.strftime('%d/%m/%Y às %H:%M')}
&nbsp;|&nbsp;
👤 {criador_nome}
</div>

{descricao_html}

</div>
"""

            c1, c2 = st.columns([5,1])

            with c1:

                st.markdown(
                    card_html,
                    unsafe_allow_html=True
                )

            with c2:

                if ev.get("user_id") == user.id:

                    st.write("")
                    st.write("")

                    if st.button(
                        "🗑️",
                        key=f"del_{ev['id']}"
                    ):

                        delete_event(ev["id"])
                        st.rerun()

    # ── HISTÓRICO ────────────────────────────────────────
    if past:

        with st.expander(
            f"🕰️ Histórico ({len(past)} eventos)",
            expanded=False
        ):

            for ev in past:

                dt = (
                    datetime.fromisoformat(
                        ev["data_hora"]
                    ).astimezone(BR_TZ)
                )

                criador = ev.get("profiles", {})

                criador_nome = (
                    criador.get("nome", "?")
                    if criador
                    else "?"
                )

                cat_emoji = next(
                    (
                        k.split()[0]
                        for k, v in CATEGORIAS.items()
                        if v == ev.get("categoria")
                    ),
                    "📅"
                )

                descricao_html = ""

                if ev.get("descricao"):

                    descricao_html = f"""
<div class="event-meta" style="margin-top:6px;">
📝 {ev["descricao"]}
</div>
"""

                card_html = f"""
<div class="event-card past">

<div class="event-title">
{cat_emoji} {ev["titulo"]}
</div>

<div class="event-meta">
📆 {dt.strftime('%d/%m/%Y às %H:%M')}
&nbsp;|&nbsp;
👤 {criador_nome}
</div>

{descricao_html}

</div>
"""

                c1, c2 = st.columns([5,1])

                with c1:

                    st.markdown(
                        card_html,
                        unsafe_allow_html=True
                    )

                with c2:

                    if ev.get("user_id") == user.id:

                        st.write("")
                        st.write("")

                        if st.button(
                            "🗑️",
                            key=f"past_del_{ev['id']}"
                        ):

                            delete_event(ev["id"])
                            st.rerun()

# ── ROUTER ────────────────────────────────────────────────────
if get_user():
    main_app()
else:
    auth_page()
