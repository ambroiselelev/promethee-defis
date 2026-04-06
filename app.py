import re
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Prométhée — Défis",
    page_icon="🐺",
    layout="centered",
)

# ---------------------------------------------------
# CONFIG V1
# ---------------------------------------------------
ADMIN_PASSWORD = "change-moi"

CATEGORIES = ["SOFT", "MOYEN", "DIFFICILE", "HARDCORE", "EXTREME"]

COLORS = {
    "SOFT": "#6F8C76",
    "MOYEN": "#9A7A45",
    "DIFFICILE": "#8F5C43",
    "HARDCORE": "#7A3040",
    "EXTREME": "#4A1825",
}

STATUS_LABELS = {
    "todo": "À faire",
    "pending": "En attente de validation",
    "redo": "À refaire",
}

DEFAULT_CHALLENGES = {
    "SOFT": [
        "Défi soft 1",
        "Défi soft 2",
    ],
    "MOYEN": [
        "Défi moyen 1",
        "Défi moyen 2",
    ],
    "DIFFICILE": [
        "Défi difficile 1",
        "Défi difficile 2",
    ],
    "HARDCORE": [
        "Défi hardcore 1",
        "Défi hardcore 2",
    ],
    "EXTREME": [
        "Défi extreme 1",
        "Défi extreme 2",
    ],
}


# ---------------------------------------------------
# OUTILS
# ---------------------------------------------------
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "profil"


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
                radial-gradient(circle at top, rgba(140, 38, 65, 0.18), transparent 28%),
                linear-gradient(180deg, #060608 0%, #09090B 35%, #050506 100%);
        }

        .block-container {
            max-width: 980px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #F4EDE2;
            letter-spacing: 0.01em;
        }

        p, label, div {
            color: #E8E0D4;
        }

        .hero-wrap {
            text-align: center;
            padding: 0.6rem 0 1.8rem 0;
        }

        .hero-kicker {
            color: #A67C52;
            text-transform: uppercase;
            letter-spacing: 0.28em;
            font-size: 0.78rem;
            margin-top: 0.4rem;
            margin-bottom: 0.7rem;
        }

        .hero-title {
            font-size: 3rem;
            font-weight: 700;
            color: #F4EDE2;
            margin-bottom: 0.35rem;
        }

        .hero-subtitle {
            color: #B6AA99;
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        .hero-line {
            width: 180px;
            height: 1px;
            margin: 0 auto;
            background: linear-gradient(90deg, transparent, #8B6A45, transparent);
        }

        .lux-card {
            background: linear-gradient(180deg, rgba(19,19,24,0.96), rgba(11,11,14,0.96));
            border: 1px solid rgba(212, 188, 150, 0.12);
            border-radius: 20px;
            padding: 1.15rem 1.15rem 0.95rem 1.15rem;
            margin-bottom: 1rem;
            box-shadow: 0 14px 34px rgba(0,0,0,0.32);
        }

        .card-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 0.8rem;
        }

        .card-title {
            font-size: 1.08rem;
            font-weight: 700;
            color: #F4EDE2;
            letter-spacing: 0.04em;
        }

        .level-chip {
            display: inline-block;
            padding: 0.34rem 0.72rem;
            border-radius: 999px;
            color: white;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }

        .meta-line {
            color: #B6AA99;
            font-size: 0.93rem;
            margin-bottom: 0.4rem;
        }

        .challenge-text {
            color: #F2EADF;
            font-size: 1.05rem;
            line-height: 1.65;
            margin: 0.65rem 0 0.9rem 0;
            white-space: pre-wrap;
        }

        .status-chip {
            display: inline-block;
            margin-top: 0.15rem;
            margin-bottom: 1rem;
            padding: 0.34rem 0.72rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.07);
            color: #EADFCF;
            font-size: 0.82rem;
        }

        .panel-box {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(212, 188, 150, 0.08);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
        }

        .panel-title {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: #A67C52;
            margin-bottom: 0.35rem;
        }

        .panel-value {
            color: #F4EDE2;
            font-size: 1.08rem;
            font-weight: 700;
        }

        .subtle-text {
            color: #AA9E8D;
            font-size: 0.92rem;
        }

        .stButton > button {
            width: 100%;
            border-radius: 14px;
            border: 1px solid rgba(212, 188, 150, 0.14);
            background: linear-gradient(180deg, #151519, #0E0E11);
            color: #F4EDE2;
            min-height: 2.9rem;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: rgba(212, 188, 150, 0.32);
            color: #FFFFFF;
        }

        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stNumberInput input {
            background: rgba(255,255,255,0.03) !important;
            border-radius: 12px !important;
            color: #F4EDE2 !important;
        }

        .stRadio label {
            color: #E8E0D4 !important;
        }

        .stTabs [data-baseweb="tab"] {
            color: #D5C8B8;
        }

        .stTabs [aria-selected="true"] {
            color: #F4EDE2 !important;
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
        c1, c2, c3 = st.columns([1.2, 1, 1.2])
        with c2:
            st.image(str(logo_path), width=190)

    st.markdown('<div class="hero-kicker">Prométhée</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Défis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Progression privée • Validation admin • Parcours maîtrisé</div>',
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

    st.markdown('<div class="lux-card">', unsafe_allow_html=True)
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
        st.info("Aucun défi dans cette catégorie.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if challenge is None:
        st.success("Catégorie terminée.")
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

    default_slug = st.query_params.get("p", "demo")
    if isinstance(default_slug, list):
        default_slug = default_slug[0]
    if default_slug not in slugs and slugs:
        default_slug = slugs[0]

    if st.session_state.logged_profile is None:
        selected_slug = st.selectbox(
            "Profil",
            slugs,
            index=slugs.index(default_slug),
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
                <div class="panel-title">Profil connecté</div>
                <div class="panel-value">{info['name']}</div>
                <div class="subtle-text">Jokers restants : {info['jokers']}</div>
                <div class="subtle-text">Lien direct : ?p={slug}</div>
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

    if st.button("Quitter l’admin"):
        st.session_state.admin_ok = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Profils", "Défis", "Validations"])

    with tab1:
        st.markdown("### Ajouter un profil")
        with st.form("new_profile_form"):
            new_name = st.text_input("Nom affiché")
            new_pin = st.text_input("PIN")
            new_jokers = st.number_input("Jokers", min_value=0, max_value=99, value=3, step=1)
            submitted = st.form_submit_button("Créer le profil")

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
                        st.success(f"Profil créé : {new_name}")
                        st.rerun()

        st.markdown("### Gérer les profils")
        for slug, info in st.session_state.profiles.items():
            st.markdown("---")
            st.markdown(f"**{info['name']}**")
            st.caption(f"Lien : ?p={slug}")

            c1, c2, c3 = st.columns(3)
            with c1:
                updated_name = st.text_input("Nom", value=info["name"], key=f"name_{slug}")
            with c2:
                updated_pin = st.text_input("PIN", value=info["pin"], key=f"pin_{slug}")
            with c3:
                updated_jokers = st.number_input(
                    "Jokers",
                    min_value=0,
                    max_value=99,
                    value=int(info["jokers"]),
                    step=1,
                    key=f"jokers_{slug}",
                )

            if st.button("Mettre à jour", key=f"save_profile_{slug}", use_container_width=True):
                st.session_state.profiles[slug]["name"] = updated_name.strip()
                st.session_state.profiles[slug]["pin"] = updated_pin.strip()
                st.session_state.profiles[slug]["jokers"] = int(updated_jokers)
                st.success("Profil mis à jour.")
                st.rerun()

    with tab2:
        st.markdown("### Modifier les défis")
        category = st.selectbox("Catégorie", CATEGORIES, key="admin_category")
        items = st.session_state.challenges[category]

        for i, text in enumerate(items):
            st.text_area(
                f"Défi {i + 1}",
                value=text,
                key=f"challenge_{category}_{i}",
                height=100,
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Monter", key=f"up_{category}_{i}", use_container_width=True) and i > 0:
                    items[i - 1], items[i] = items[i], items[i - 1]
                    st.rerun()
            with c2:
                if st.button("Descendre", key=f"down_{category}_{i}", use_container_width=True) and i < len(items) - 1:
                    items[i + 1], items[i] = items[i], items[i + 1]
                    st.rerun()
            with c3:
                if st.button("Supprimer", key=f"delete_{category}_{i}", use_container_width=True):
                    items.pop(i)
                    st.rerun()

        if st.button("Enregistrer les textes", use_container_width=True):
            new_items = []
            for i in range(len(items)):
                new_items.append(st.session_state[f"challenge_{category}_{i}"])
            st.session_state.challenges[category] = new_items
            st.success("Défis enregistrés.")
            st.rerun()

        st.markdown("### Ajouter un défi")
        new_challenge = st.text_area("Nouveau défi", key=f"new_{category}", height=100)
        if st.button("Ajouter ce défi", use_container_width=True):
            if new_challenge.strip():
                st.session_state.challenges[category].append(new_challenge.strip())
                st.success("Défi ajouté.")
                st.rerun()
            else:
                st.error("Le texte est vide.")

    with tab3:
        st.markdown("### Défis en attente")
        has_pending = False

        for slug, info in st.session_state.profiles.items():
            for category in CATEGORIES:
                progress = st.session_state.progress[slug][category]

                if progress["status"] == "pending":
                    has_pending = True
                    idx = progress["index"]
                    items = st.session_state.challenges[category]
                    text = items[idx] if idx < len(items) else "(défi introuvable)"

                    st.markdown("---")
                    st.markdown(f"**Profil** : {info['name']}")
                    st.markdown(f"**Catégorie** : {category}")
                    st.write(text)

                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Valider", key=f"approve_{slug}_{category}", use_container_width=True):
                            approve_challenge(slug, category)
                            st.success("Défi validé.")
                            st.rerun()
                    with c2:
                        if st.button("Demander de refaire", key=f"redo_{slug}_{category}", use_container_width=True):
                            redo_challenge(slug, category)
                            st.warning("Défi marqué à refaire.")
                            st.rerun()

        if not has_pending:
            st.info("Aucun défi en attente pour le moment.")


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
