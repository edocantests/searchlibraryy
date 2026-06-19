"""
Source Library Search — Streamlit app
Busca libros en sourcelibrary.org usando su API pública (search_library).
No requiere autenticación ni API key.
"""

import requests
import streamlit as st

API_BASE = "https://sourcelibrary.org/api"
SEARCH_ENDPOINT = f"{API_BASE}/search"

st.set_page_config(page_title="Source Library Search", page_icon="📜", layout="wide")

st.title("📜 Source Library Search")
st.caption(
    "Busca entre 16,000+ textos antiguos traducidos al inglés en "
    "[sourcelibrary.org](https://sourcelibrary.org) — Hermética, alquimia, "
    "filosofía, teología, ciencia temprana y más."
)


@st.cache_data(show_spinner=False, ttl=300)
def search_library(query: str) -> dict:
    """Llama al endpoint público GET /api/search de Source Library."""
    response = requests.get(SEARCH_ENDPOINT, params={"q": query}, timeout=20)
    response.raise_for_status()
    return response.json()


def render_book(item: dict) -> None:
    title = item.get("title", "Sin título")
    author = item.get("author", "Autor desconocido")
    language = item.get("language", "")
    published = item.get("published", "")
    pages_count = item.get("pages_count")
    translation_percent = item.get("translation_percent")
    url = item.get("url") or (
        f"https://sourcelibrary.org/book/{item.get('id')}" if item.get("id") else None
    )

    with st.container(border=True):
        if url:
            st.markdown(f"### [{title}]({url})")
        else:
            st.markdown(f"### {title}")

        meta = " · ".join(
            str(p) for p in [author, language, published] if p
        )
        if meta:
            st.caption(meta)

        details = []
        if pages_count is not None:
            details.append(f"{pages_count} páginas")
        if translation_percent is not None:
            details.append(f"{translation_percent}% traducido")
        if details:
            st.write(" · ".join(details))


# --- Interfaz de búsqueda ---

with st.form(key="search_form"):
    query = st.text_input(
        "Término de búsqueda",
        placeholder="ej: prima materia, Paracelsus, Hermes Trismegistus...",
    )
    submitted = st.form_submit_button("🔍 Buscar", type="primary")

if submitted:
    if not query.strip():
        st.warning("Escribe un término de búsqueda.")
    else:
        with st.spinner("Buscando en Source Library..."):
            try:
                data = search_library(query.strip())
            except requests.exceptions.RequestException as exc:
                st.error(f"No se pudo conectar con la API: {exc}")
                data = None

        if data is not None:
            results = data.get("books") or data.get("results") or []
            total = data.get("total", len(results))

            if not results:
                st.info("No se encontraron resultados para esa búsqueda.")
            else:
                st.success(f"{total} resultado(s) encontrado(s) — mostrando {len(results)}")
                for book in results:
                    render_book(book)

                with st.expander("Ver respuesta JSON completa"):
                    st.json(data)
else:
    st.info("Escribe un término y pulsa **Buscar** para empezar.")

st.divider()
st.caption(
    "Datos vía la API pública de Source Library (sin autenticación). "
    "Más info en [sourcelibrary.org/developers](https://sourcelibrary.org/developers)."
)
