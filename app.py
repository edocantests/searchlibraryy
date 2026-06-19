"""
Source Library Search — Streamlit app
Busca libros en sourcelibrary.org usando su endpoint público search_library.
No requiere autenticación ni API key.
"""

import requests
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

API_BASE = "https://sourcelibrary.org/api"
SEARCH_ENDPOINT = f"{API_BASE}/search"

st.set_page_config(
    page_title="Source Library Search",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Estilos globales (CSS libre, sin dependencias de pago)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1a1612 0%, #100e0b 60%);
    }
    h1, h2, h3 {
        font-family: "Georgia", "Iowan Old Style", serif;
        letter-spacing: 0.02em;
    }
    .sl-hero {
        padding: 1.25rem 1.5rem;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(193,154,90,0.12), rgba(193,154,90,0.02));
        border: 1px solid rgba(193,154,90,0.25);
        margin-bottom: 1.25rem;
    }
    .sl-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.4rem;
        background: rgba(193,154,90,0.15);
        color: #d9b87c;
        border: 1px solid rgba(193,154,90,0.3);
    }
    .sl-card-title a {
        color: #f2e9da !important;
        text-decoration: none;
        font-weight: 700;
    }
    .sl-card-title a:hover {
        color: #d9b87c !important;
        text-decoration: underline;
    }
    .sl-author {
        color: #c9bba0;
        font-size: 0.95rem;
        margin-top: 0.1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cabecera
# ---------------------------------------------------------------------------
with st.container():
    st.markdown(
        """
        <div class="sl-hero">
            <h1>📜 Source Library Search</h1>
            <p style="color:#c9bba0; font-size:1.05rem; margin-bottom:0;">
            Busca entre 16,000+ textos antiguos traducidos al inglés en
            <a href="https://sourcelibrary.org" style="color:#d9b87c;">sourcelibrary.org</a>
            — Hermética, alquimia, filosofía, teología, ciencia temprana y más.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Llamada a la API
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False, ttl=300)
def search_library(query: str, language: str | None, sort: str, limit: int) -> dict:
    """Llama al endpoint público GET /api/search (search_library) de Source Library."""
    params = {"q": query, "limit": limit, "sort": sort}
    if language and language != "Todos":
        params["language"] = language
    response = requests.get(SEARCH_ENDPOINT, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Sidebar — filtros
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Filtros")
    language_filter = st.selectbox(
        "Idioma original",
        ["Todos", "Latin", "German", "English", "French", "Italian",
         "Greek", "Arabic", "Hebrew", "Spanish"],
        index=0,
    )
    sort_option = st.selectbox(
        "Ordenar por",
        options=["relevance", "date_asc", "date_desc", "title"],
        format_func=lambda v: {
            "relevance": "Relevancia",
            "date_asc": "Año (antiguo → reciente)",
            "date_desc": "Año (reciente → antiguo)",
            "title": "Título (A–Z)",
        }[v],
        index=0,
    )
    result_limit = st.slider("Resultados por búsqueda", 5, 50, 15, step=5)

    st.divider()
    st.caption(
        "Datos vía la API pública de Source Library (sin autenticación). "
        "Más info en [sourcelibrary.org/developers](https://sourcelibrary.org/developers)."
    )

# ---------------------------------------------------------------------------
# Búsqueda
# ---------------------------------------------------------------------------
with st.form(key="search_form"):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input(
            "Término de búsqueda",
            placeholder="ej: prima materia, Paracelsus, Hermes Trismegistus...",
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button("🔍 Buscar", type="primary", use_container_width=True)

if submitted:
    if not query.strip():
        st.warning("Escribe un término de búsqueda.")
    else:
        with st.spinner("Buscando en Source Library..."):
            try:
                data = search_library(query.strip(), language_filter, sort_option, result_limit)
            except requests.exceptions.HTTPError as exc:
                st.error(f"La API respondió con un error: {exc}")
                data = None
            except requests.exceptions.RequestException as exc:
                st.error(f"No se pudo conectar con la API: {exc}")
                data = None

        if data is not None:
            results = data.get("results", [])
            total_matches = data.get("total_matches", len(results))

            if not results:
                st.info("No se encontraron resultados para esa búsqueda.")
            else:
                st.success(
                    f"**{total_matches}** resultado(s) en total — mostrando {len(results)}"
                )

                # Grid de tarjetas (2 columnas en escritorio)
                cols = st.columns(2)
                for idx, book in enumerate(results):
                    title = book.get("title", "Sin título")
                    author = book.get("author", "Autor desconocido")
                    language = book.get("language", "")
                    published = book.get("published", "")
                    url = book.get("url", "")
                    has_doi = book.get("has_doi", False)

                    with cols[idx % 2]:
                        with stylable_container(
                            key=f"card_{idx}",
                            css_styles="""
                                {
                                    border: 1px solid rgba(193,154,90,0.25);
                                    border-radius: 12px;
                                    padding: 1rem 1.1rem;
                                    margin-bottom: 1rem;
                                    background: rgba(255,255,255,0.02);
                                }
                                """,
                        ):
                            st.markdown(
                                f'<div class="sl-card-title">'
                                f'<a href="{url}" target="_blank">{title}</a></div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="sl-author">{author}</div>',
                                unsafe_allow_html=True,
                            )

                            badges = ""
                            if language:
                                badges += f'<span class="sl-badge">🌐 {language}</span>'
                            if published:
                                badges += f'<span class="sl-badge">📅 {published}</span>'
                            if has_doi:
                                badges += '<span class="sl-badge">✅ DOI</span>'
                            if badges:
                                st.markdown(
                                    f'<div style="margin-top:0.5rem;">{badges}</div>',
                                    unsafe_allow_html=True,
                                )

                with st.expander("Ver respuesta JSON completa"):
                    st.json(data)
else:
    st.info("Escribe un término y pulsa **Buscar** para empezar, o ajusta los filtros en la barra lateral.")
