import streamlit as st

st.set_page_config(page_title="LGD Scouting Report", layout="wide")

st.title("Scout Report — LGD Gaming")
st.markdown("""
Análise do roster atual da LGD (pós-maio/2026), baseada em 62 partidas competitivas.

Use o menu lateral para navegar entre as seções:
- **Draft**: picks, bans e padrões por adversário
- **Hero Pool**: heróis de conforto por jogador e por time
- **Economia**: como a LGD costuma vencer (e quando a vantagem aparece)
""")
