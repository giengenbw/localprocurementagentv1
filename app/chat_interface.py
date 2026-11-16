import streamlit as st
from agents.procurement_agent import ProcurementAgent
def render_chat():
    st.subheader("Procurement Assistant")
    text=st.text_area("Instruction / Anweisung / 指令",placeholder="Erstelle eine Bestellung für Material 123456, 10 Stück, Liefertermin 15.12.2026.")
    use_llm=st.toggle("Use local Ollama",value=True)
    if st.button("Analyze",type="primary") and text:
        plan=ProcurementAgent().handle(text,use_llm=use_llm)
        st.json(plan.model_dump(mode="json"))
