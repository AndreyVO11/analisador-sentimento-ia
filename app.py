import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

st.set_page_config(page_title="Analisador de Sentimento IA", page_icon="🎭")
st.title("Analisador de Sentimento em Tempo Real")
st.caption("Digite qualquer texto e veja a IA analisar o tom instantaneamente.")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

texto = st.text_area(
    "Digite uma frase, comentário ou conversa:",
    placeholder="Ex: 'Ah, claro, mais uma reunião às 8h da manhã. Adoro.'",
    height=120
)

analisar = st.button("Analisar sentimento", type="primary")

if analisar and texto.strip():
    with st.spinner("Analisando..."):
        prompt = f"""Analise o sentimento do texto abaixo e responda APENAS em JSON, sem markdown, no formato:
{{
  "sentimento": "positivo | negativo | neutro | sarcástico | irônico",
  "intensidade": número de 0 a 100,
  "explicacao": "explicação curta de 1-2 frases sobre por que classificou assim"
}}

Texto: "{texto}" """

        resposta = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        conteudo = resposta.choices[0].message.content.strip()
        # Remove possíveis blocos de markdown
        conteudo = conteudo.replace("```json", "").replace("```", "").strip()

        try:
            resultado = json.loads(conteudo)

            # Mapeia cores por sentimento
            cores = {
                "positivo": "#1D9E75",
                "negativo": "#E24B4A",
                "neutro": "#888780",
                "sarcástico": "#BA7517",
                "irônico": "#7F77DD"
            }
            cor = cores.get(resultado["sentimento"].lower(), "#888780")

            st.markdown(f"""
            <div style="background-color:{cor}20; border-left: 5px solid {cor}; padding: 16px; border-radius: 8px;">
                <h3 style="margin:0; color:{cor};">{resultado['sentimento'].upper()}</h3>
                <p style="margin:8px 0 0;">Intensidade: {resultado['intensidade']}/100</p>
                <p style="margin:8px 0 0;">{resultado['explicacao']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Barra de intensidade
            st.progress(resultado["intensidade"] / 100)

        except json.JSONDecodeError:
            st.error("Não consegui interpretar a resposta. Tente novamente.")
            st.write(conteudo)

elif analisar:
    st.warning("Digite um texto para analisar.")