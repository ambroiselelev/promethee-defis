import re
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Prométhée — Défis",
    page_icon="🐺",
    layout="centered",
)

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------
ADMIN_PASSWORD = "boubouboubou122"

CATEGORIES = ["SOFT", "MOYEN", "DIFFICILE", "HARDCORE", "EXTREME"]

COLORS = {
    "SOFT": "#8EA38F",
    "MOYEN": "#B6925E",
    "DIFFICILE": "#B37455",
    "HARDCORE": "#A24A5E",
    "EXTREME": "#7B2F45",
}

STATUS_LABELS = {
    "todo": "À faire",
    "pending": "En attente",
    "redo": "À refaire",
}

DEFAULT_CHALLENGES = {
    "SOFT": ["Défi soft 1", "Défi soft 2"],
    "MOYEN": ["Défi moyen 1", "Défi moyen 2"],
    "DIFFICILE": ["Défi difficile 1", "Défi difficile 2"],
    "HARDCORE": ["Défi hardcore 1", "Défi hardcore 2"],
    "EXTREME": ["Défi extreme 1", "Défi extreme 2"],
}


# ---------------------------------------------------
# OUTILS
# ---------------------------------------------------
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "profil"


def short_text(text: str, limit: int = 90) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def get_default_profile_slug():
    profiles = list(st.session_state.profiles.keys())
    if not profiles:
        return None

    try:
        qp = st.query_params.get("p", None)
        if isinstance(qp, list):
            qp = qp[0] if qp else None
        if qp in profiles:
            return qp
    except Exception:
        pass

    return profiles[0]


def ensure_profile_progress(profile_slug: str):
    if "progress" not in st.session_state:
        st.session_state.progress = {}

    if profile_slug not in st.session_state.progress:
        st.session_state.progress[profile_slug] = {}

    for category in CATEGORIES:
        if category not in st.session_state.progress[profile_slug]:
            st.session_state.progress[profile_slug][category] = {
                "index": 0,
                "status": "todo",
            }


def init_state():
    if "profiles" not in st.session_state:
        st.session_state.profiles = {
            "demo": {
                "name": "Demo",
                "pin": "1234",
                "jokers": 3,
            }
        }

    if "challenges" not in st.session_state:
        st.session_state.challenges = {
            category: values[:] for category, values in DEFAULT_CHALLENGES.items()
        }

    if "progress" not in st.session_state:
        st.session_state.progress = {}

    for slug in st.session_state.profiles.keys():
        ensure_profile_progress(slug)

    if "logged_profile" not in st.session_state:
        st.session_state.logged_profile = None

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False


def current_challenge(profile_slug: str, category: str):
    progress = st.session_state.progress[profile_slug][category]
    items = st.session_state.challenges[category]
    idx = progress["index"]

    if idx >= len(items):
        return None

    return items[idx]


def approve_challenge(profile_slug: str, category: str):
    st.session_state.progress[profile_slug][category]["index"] += 1
    st.session_state.progress[profile_slug][category]["status"] = "todo"


def redo_challenge(profile_slug: str, category: str):
    st.session_state.progress[profile_slug][category]["status"] = "redo"


def mark_done(profile_slug: str, category: str):
    st.session_state.progress[profile_slug][category]["status"] = "pending"


def use_joker(profile_slug: str, category: str):
    if st.session_state.profiles[profile_slug]["jokers"] <= 0:
        return

    st.session_state.profiles[profile_slug]["jokers"] -= 1
    st.session_state.progress[profile_slug][category]["index"] += 1
    st.session_state.progress[profile_slug][category]["status"] = "todo"


# ---------------------------------------------------
# STYLE
# ---------------------------------------------------
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top, rgba(140, 38, 65, 0.07), transparent 28%),
                linear-gradient(180deg, #FFFFFF 0%, #FBF8F4 100%);
        }

        .block-container {
            max-width: 940px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, h5, h6,
        p, label, div, span {
            color: #1D1D1D;
        }

        .hero-wrap {
            text-align: center;
            padding: 0.4rem 0 1.3rem 0;
        }

        .hero-kicker {
            color: #9A6A4B;
            text-transform: uppercase;
            letter-spacing: 0.22em;
            font-size: 0.78rem;
            margin-top: 0.25rem;
            margin-bottom: 0.55rem;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 700;
            color: #181818;
            margin-bottom: 0.2rem;
        }

        .hero-subtitle {
            color: #6B6258;
            font-size: 0.97rem;
            margin-bottom: 0.8rem;
        }

        .hero-line {
            width: 170px;
            height: 1px;
            margin: 0 auto;
            background: linear-gradient(90deg, transparent, #B79372, transparent);
        }

        .panel-box {
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(167, 132, 99, 0.18);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 28px rgba(30, 20, 10, 0.06);
        }

        .panel-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #A06F4A;
            margin-bottom: 0.3rem;
        }

        .panel-value {
            color: #1B1B1B;
            font-size: 1.02rem;
            font-weight: 700;
        }

        .subtle-text {
            color: #6A625A;
            font-size: 0.92rem;
        }

        .challenge-card {
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(167, 132, 99, 0.16);
            border-radius: 20px;
            padding: 1rem 1rem 0.9rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 28px rgba(30, 20, 10, 0.06);
        }

        .card-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 0.8rem;
        }

        .card-title {
            font-size: 1.02rem;
            font-weight: 700;
            color: #1B1B1B;
            letter-spacing: 0.04em;
        }

        .level-chip {
            display: inline-block;
            padding: 0.32rem 0.72rem;
            border-radius: 999px;
            color: white;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }

        .meta-line {
            color: #71675D;
            font-size: 0.91rem;
            margin-bottom: 0.42rem;
        }

        .challenge-text {
            color: #1E1E1E;
            font-size: 1.02rem;
            line-height: 1.62;
            margin: 0.55rem 0 0.8rem 0;
            white-space: pre-wrap;
        }

        .status-chip {
            display: inline-block;
            margin-top: 0.05rem;
            margin-bottom: 0.95rem;
            padding: 0.34rem 0.72rem;
            border-radius: 999px;
            background: #F3EEE8;
            border: 1px solid rgba(140, 110, 80, 0.12);
            color: #5A4A3B;
            font-size: 0.81rem;
        }

        .compact-row {
            background: rgba(255,255,255,0.86);
            border: 1px solid rgba(167, 132, 99, 0.16);
            border-radius: 14px;
            padding: 0.7rem 0.85rem 0.45rem 0.85rem;
            margin-bottom: 0.65rem;
        }

        .compact-top {
            font-size: 0.84rem;
            color: #7A6B5D;
            margin-bottom: 0.25rem;
        }

        .compact-main {
            font-size: 0.96rem;
            font-weight: 600;
            color: #1E1E1E;
            margin-bottom: 0.45rem;
        }

        .stButton > button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(167, 132, 99, 0.20);
            background: linear-gradient(180deg, #FFFFFF, #F5EFE8);
            color: #1D1D1D;
            min-height: 2.65rem;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: rgba(167, 132, 99, 0.42);
            color: #000000;
        }

        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stNumberInput input {
            background: rgba(255,255,255,0.88) !important;
            border-radius: 12px !important;
            color: #1D1D1D !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #6C625A;
        }

        .stTabs [aria-selected="true"] {
            color: #1C1C1C !important;
        }

        .stRadio label {
            color: #1D1D1D !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------
# UI
# ---------------------------------------------------
def show_header():
    possible_paths = [
        Path("logo.jpg"),
        Path("assets/logo.jpg"),
    ]

    logo_path = None
    for p in possible_paths:
        if p.exists():
            logo_path = p
            break

    st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)

    if logo_path is not None:
        c1, c2, c3 = st.columns([1.4, 1, 1.4])
        with c2:
            st.image(str(logo_path), width=150)

    st.markdown('<div class="hero-kicker">Prométhée</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Défis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Simple • Privé • Progressif</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-line"></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_category_card(profile_slug: str, category: str):
    color = COLORS[category]
    progress = st.session_state.progress[profile_slug][category]
    challenge = current_challenge(profile_slug, category)
    status = progress["status"]
    idx = progress["index"]
    total = len(st.session_state.challenges[category])

    st.markdown('<div class="challenge-card">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="card-head">
            <div class="card-title">{category}</div>
            <div class="level-chip" style="background:{color};">{category}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if total == 0:
        st.info("Aucun défi.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if challenge is None:
        st.success("Terminé.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown(
        f'<div class="meta-line">Défi {idx + 1} sur {total}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="challenge-text">{challenge}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="status-chip">Statut : {STATUS_LABELS.get(status, "À faire")}</div>',
        unsafe_allow_html=True,
    )

    if status in ["todo", "redo"]:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Fait", key=f"done_{profile_slug}_{category}", use_container_width=True):
                mark_done(profile_slug, category)
                st.rerun()
        with c2:
            disabled = st.session_state.profiles[profile_slug]["jokers"] <= 0
            if st.button(
                "Utiliser un joker",
                key=f"joker_{profile_slug}_{category}",
                use_container_width=True,
                disabled=disabled,
            ):
                use_joker(profile_slug, category)
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_user_area():
    st.subheader("Espace utilisatrice")

    profiles = st.session_state.profiles
    slugs = list(profiles.keys())

    default_slug = get_default_profile_slug()

    if st.session_state.logged_profile is None:
        selected_slug = st.selectbox(
            "Profil",
            slugs,
            index=slugs.index(default_slug) if default_slug in slugs else 0,
            format_func=lambda x: profiles[x]["name"],
        )
        pin = st.text_input("Code PIN", type="password")

        if st.button("Entrer", use_container_width=True):
            if pin == profiles[selected_slug]["pin"]:
                st.session_state.logged_profile = selected_slug
                st.rerun()
            else:
                st.error("PIN incorrect.")
        return

    slug = st.session_state.logged_profile
    info = profiles[slug]

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"""
            <div class="panel-box">
                <div class="panel-title">Profil</div>
                <div class="panel-value">{info['name']}</div>
                <div class="subtle-text">Jokers restants : {info['jokers']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.logged_profile = None
            st.rerun()

    for category in CATEGORIES:
        render_category_card(slug, category)


def render_admin_area():
    st.subheader("Espace admin")

    if not st.session_state.admin_ok:
        password = st.text_input("Mot de passe admin", type="password")
        if st.button("Connexion admin", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
        return

    top1, _ = st.columns([1, 4])
    with top1:
        if st.button("Quitter", use_container_width=True):
            st.session_state.admin_ok = False
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["Validations", "Défis", "Profils"])

    with tab1:
        pending_items = []
        for slug, info in st.session_state.profiles.items():
            for category in CATEGORIES:
                progress = st.session_state.progress[slug][category]
                if progress["status"] == "pending":
                    idx = progress["index"]
                    items = st.session_state.challenges[category]
                    text = items[idx] if idx < len(items) else "(défi introuvable)"
                    pending_items.append(
                        {
                            "slug": slug,
                            "name": info["name"],
                            "category": category,
                            "text": text,
                        }
                    )

        st.markdown(
            f"""
            <div class="panel-box">
                <div class="panel-title">En attente</div>
                <div class="panel-value">{len(pending_items)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not pending_items:
            st.info("Aucun défi en attente.")
        else:
            filter_profile = st.selectbox(
                "Filtrer par profil",
                ["Tous"] + [st.session_state.profiles[s]["name"] for s in st.session_state.profiles],
            )
            filter_category = st.selectbox(
                "Filtrer par catégorie",
                ["Toutes"] + CATEGORIES,
            )

            for item in pending_items:
                if filter_profile != "Tous" and item["name"] != filter_profile:
                    continue
                if filter_category != "Toutes" and item["category"] != filter_category:
                    continue

                st.markdown(
                    f"""
                    <div class="compact-row">
                        <div class="compact-top">{item['name']} • {item['category']}</div>
                        <div class="compact-main">{short_text(item['text'], 120)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("Voir le texte complet"):
                    st.write(item["text"])

                c1, c2 = st.columns(2)
                with c1:
                    if st.button(
                        "Valider",
                        key=f"approve_{item['slug']}_{item['category']}",
                        use_container_width=True,
                    ):
                        approve_challenge(item["slug"], item["category"])
                        st.rerun()
                with c2:
                    if st.button(
                        "À refaire",
                        key=f"redo_{item['slug']}_{item['category']}",
                        use_container_width=True,
                    ):
                        redo_challenge(item["slug"], item["category"])
                        st.rerun()

    with tab2:
        category = st.selectbox("Catégorie", CATEGORIES, key="admin_category")
        items = st.session_state.challenges[category]

        st.markdown(
            f"""
            <div class="panel-box">
                <div class="panel-title">Nombre de défis</div>
                <div class="panel-value">{len(items)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Ajouter un défi")
        new_challenge = st.text_area("Texte", key=f"new_{category}", height=120)
        if st.button("Ajouter", key=f"add_{category}", use_container_width=True):
            if new_challenge.strip():
                st.session_state.challenges[category].append(new_challenge.strip())
                st.rerun()
            else:
                st.error("Le texte est vide.")

        st.markdown("### Modifier un défi existant")

        if len(items) == 0:
            st.info("Aucun défi dans cette catégorie.")
        else:
            selected_index = st.selectbox(
                "Défi",
                options=list(range(len(items))),
                format_func=lambda i: f"{i + 1}. {short_text(items[i], 80)}",
                key=f"selected_{category}",
            )

            edited_text = st.text_area(
                "Texte du défi",
                value=items[selected_index],
                key=f"edit_text_{category}_{selected_index}",
                height=180,
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Enregistrer", key=f"save_{category}", use_container_width=True):
                    st.session_state.challenges[category][selected_index] = edited_text.strip()
                    st.rerun()
            with c2:
                if st.button("Supprimer", key=f"delete_{category}", use_container_width=True):
                    st.session_state.challenges[category].pop(selected_index)
                    st.rerun()

            c3, c4 = st.columns(2)
            with c3:
                if st.button("Monter", key=f"up_{category}", use_container_width=True) and selected_index > 0:
                    items[selected_index - 1], items[selected_index] = items[selected_index], items[selected_index - 1]
                    st.rerun()
            with c4:
                if st.button("Descendre", key=f"down_{category}", use_container_width=True) and selected_index < len(items) - 1:
                    items[selected_index + 1], items[selected_index] = items[selected_index], items[selected_index + 1]
                    st.rerun()

    with tab3:
        st.markdown("### Ajouter un profil")
        with st.form("new_profile_form"):
            new_name = st.text_input("Nom affiché")
            new_pin = st.text_input("PIN")
            new_jokers = st.number_input("Jokers", min_value=0, max_value=99, value=3, step=1)
            submitted = st.form_submit_button("Créer")

            if submitted:
                if not new_name.strip() or not new_pin.strip():
                    st.error("Nom et PIN obligatoires.")
                else:
                    new_slug = slugify(new_name)
                    if new_slug in st.session_state.profiles:
                        st.error("Ce profil existe déjà.")
                    else:
                        st.session_state.profiles[new_slug] = {
                            "name": new_name.strip(),
                            "pin": new_pin.strip(),
                            "jokers": int(new_jokers),
                        }
                        ensure_profile_progress(new_slug)
                        st.rerun()

        st.markdown("### Modifier un profil")
        profile_slugs = list(st.session_state.profiles.keys())
        selected_profile = st.selectbox(
            "Profil",
            profile_slugs,
            format_func=lambda s: st.session_state.profiles[s]["name"],
            key="profile_to_edit",
        )

        info = st.session_state.profiles[selected_profile]
        updated_name = st.text_input("Nom", value=info["name"], key=f"name_{selected_profile}")
        updated_pin = st.text_input("PIN", value=info["pin"], key=f"pin_{selected_profile}")
        updated_jokers = st.number_input(
            "Jokers",
            min_value=0,
            max_value=99,
            value=int(info["jokers"]),
            step=1,
            key=f"jokers_{selected_profile}",
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Mettre à jour", key=f"save_profile_{selected_profile}", use_container_width=True):
                st.session_state.profiles[selected_profile]["name"] = updated_name.strip()
                st.session_state.profiles[selected_profile]["pin"] = updated_pin.strip()
                st.session_state.profiles[selected_profile]["jokers"] = int(updated_jokers)
                st.rerun()
        with c2:
            if (
                selected_profile != "demo"
                and st.button("Supprimer le profil", key=f"delete_profile_{selected_profile}", use_container_width=True)
            ):
                st.session_state.profiles.pop(selected_profile, None)
                st.session_state.progress.pop(selected_profile, None)
                if st.session_state.logged_profile == selected_profile:
                    st.session_state.logged_profile = None
                st.rerun()


# ---------------------------------------------------
# APP
# ---------------------------------------------------
init_state()
show_header()

mode = st.radio("Choisir un espace", ["Utilisatrice", "Admin"], horizontal=True)

if mode == "Utilisatrice":
    render_user_area()
else:
    render_admin_area()
