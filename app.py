import re
import streamlit as st

st.set_page_config(
    page_title="Prométhée — Défis",
    page_icon="🐺",
    layout="centered",
)

# -----------------------------
# CONFIG SIMPLE V1
# -----------------------------
ADMIN_PASSWORD = "change-moi"

CATEGORIES = ["SOFT", "MOYEN", "DIFFICILE", "HARDCORE", "EXTREME"]

COLORS = {
    "SOFT": "#6E8B74",
    "MOYEN": "#8B6E3B",
    "DIFFICILE": "#8B5A3C",
    "HARDCORE": "#7A2E3A",
    "EXTREME": "#4F1C2D",
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


# -----------------------------
# OUTILS
# -----------------------------
def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "profil"


def ensure_profile_progress(profile_slug: str):
    if profile_slug not in st.session_state.progress:
        st.session_state.progress[profile_slug] = {}

    for category in CATEGORIES:
        if category not in st.session_state.progress[profile_slug]:
            st.session_state.progress[profile_slug][category] = {
                "index": 0,
                "status": "todo",  # todo / pending / redo
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


# -----------------------------
# STYLE
# -----------------------------
st.markdown(
    """
    <style>
        .block-container {
            max-width: 980px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        .hero {
            text-align: center;
            padding: 1.2rem 0 1.8rem 0;
        }

        .hero-title {
            font-size: 2.4rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 0.2rem;
            color: #F5F1EA;
        }

        .hero-subtitle {
            color: #B9B2A8;
            font-size: 1rem;
        }

        .card {
            background: linear-gradient(180deg, rgba(26,26,30,0.95), rgba(15,15,18,0.95));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 1rem 1rem 0.7rem 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.28);
        }

        .small-muted {
            color: #B9B2A8;
            font-size: 0.92rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# UI
# -----------------------------
def show_header():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">PROMÉTHÉE</div>
            <div class="hero-subtitle">Défis • Progression • Validation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_user_area():
    st.subheader("Espace utilisatrice")

    profiles = st.session_state.profiles
    slugs = list(profiles.keys())

    default_slug = st.query_params.get("p", slugs[0] if slugs else "demo")
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

    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Profil connecté : {info['name']}")
        st.caption(f"Jokers restants : {info['jokers']}")
    with col2:
        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.logged_profile = None
            st.rerun()

    st.caption(f"Lien direct profil : ?p={slug}")

    for category in CATEGORIES:
        color = COLORS[category]
        progress = st.session_state.progress[slug][category]
        challenge = current_challenge(slug, category)
        status = progress["status"]
        idx = progress["index"]
        total = len(st.session_state.challenges[category])

        with st.container():
            st.markdown(
                f"""
                <div class="card">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                        <div style="font-size:1.05rem;font-weight:700;">{category}</div>
                        <div style="background:{color};color:white;padding:0.35rem 0.7rem;border-radius:999px;font-size:0.78rem;font-weight:700;">
                            Niveau
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            if total == 0:
                st.info("Aucun défi dans cette catégorie.")
            elif challenge is None:
                st.success("Catégorie terminée.")
            else:
                st.markdown(f"**Défi {idx + 1} / {total}**")
                st.write(challenge)

                if status == "pending":
                    st.warning("En attente de validation par l’administrateur.")
                elif status == "redo":
                    st.error("À refaire.")
                else:
                    st.caption("Statut : à faire")

                if status in ["todo", "redo"]:
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Fait", key=f"done_{slug}_{category}", use_container_width=True):
                            mark_done(slug, category)
                            st.rerun()
                    with c2:
                        disabled = info["jokers"] <= 0
                        if st.button(
                            "Utiliser un joker",
                            key=f"joker_{slug}_{category}",
                            use_container_width=True,
                            disabled=disabled,
                        ):
                            use_joker(slug, category)
                            st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


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


# -----------------------------
# APP
# -----------------------------
init_state()
show_header()

st.info("Version V1 simple : idéale pour tester le design et le parcours.")

mode = st.radio("Choisir un espace", ["Utilisatrice", "Admin"], horizontal=True)

if mode == "Utilisatrice":
    render_user_area()
else:
    render_admin_area()
