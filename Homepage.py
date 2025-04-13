from streamlit_calendar import calendar
from st_social_media_links import SocialMediaIcons
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

def homepage():
    # Page configuration
    st.set_page_config(
        page_title="Prüfungsplaner | Lerne effizienter",
        page_icon="📚",
        layout="wide"
    )
    

    st.title("📚 Prüfungsplaner")
    st.write(f"#### Dein optimaler Lernplan für maximalen Erfolg")
    
    # Main info section - explaining the why
    st.header("Warum du einen Lernplan brauchst")

    container = st.container(border=True)
    with container:
        why_cols = st.columns(3)
        with why_cols[0]:
            
            st.container().subheader("⏱️ Zeitmangel")
            st.container().write("Strukturierte Vorbereitung verhindert Last-Minute-Panik und sichert ausreichend Zeit für alle Themen.")
            
            with why_cols[1]:
                st.container().subheader("🧠 Vergessenskurve")
                st.container().write("Regelmäßige Wiederholungen sorgen für langfristiges Behalten statt schnellem Vergessen.")
            
            with why_cols[2]:
                st.container().subheader("📊 Struktur")
                st.container().write("Fokus auf wichtige und schwierige Themen statt ineffizientes Lernen nach Gefühl.")
    
    # Video section with explanation
    st.header("So funktioniert der Prüfungsplaner")
    container = st.container(border=True)
    with container:
        video_cols = st.columns([2, 3])
        
        with video_cols[0]:
            st.image("figures/Studyplaner_Workflow.png")
            # st.video("https://www.youtube.com/watch?v=AbRlFdrz09s")
        
        with video_cols[1]:
            st.container().subheader("In 3 einfachen Schritten:")
            
            steps_container = st.container()
            steps_container.write("1️⃣ Prüfungstermine eingeben")
            steps_container.write("2️⃣ Lernpräferenzen festlegen")
            steps_container.write("3️⃣ Personalisierten Plan erhalten")
            
            st.button("Jetzt starten", type="primary", use_container_width=True)
        

    st.header("Funktionen des Prüfungsplaners")

    # Display features in 2x3 grid
    feature_cols1 = st.columns(3)
    feature_cols2 = st.columns(3)

    # Erste Zeile mit Features
    with feature_cols1[0]:
        container = st.container(border=True)
        with container:
            st.subheader("📊 Intelligente Priorisierung")
            st.write("Automatische Gewichtung nach Wichtigkeit und individuellem Schwierigkeitsgrad")

    with feature_cols1[1]:
        container = st.container(border=True)
        with container:
            st.subheader("🔄 Spaced Repetition")
            st.write("Wissenschaftlich optimierte Wiederholungsintervalle für besseres Behalten")

    with feature_cols1[2]:
        container = st.container(border=True)
        with container:
            st.subheader("📱 Kalenderansicht")
            st.write("Übersichtliche Darstellung mit farblicher Kennzeichnung der Fächer")

    # Zweite Zeile mit Features
    with feature_cols2[0]:
        container = st.container(border=True)
        with container:
            st.subheader("📈 Fortschrittsübersicht")
            st.write("Tägliche und wöchentliche Fortschrittskontrolle auf einen Blick")

    with feature_cols2[1]:
        container = st.container(border=True)
        with container:
            st.subheader("⚙️ Anpassbarkeit")
            st.write("Berücksichtigung deiner Tagesroutine und Lernpräferenzen")

    with feature_cols2[2]:
        container = st.container(border=True)
        with container:
            st.subheader("📤 Export-Funktion")
            st.write("Lernplan direkt in deinen digitalen Kalender importieren")




    with st.sidebar:
        social_media_links = [
            "https://www.youtube.com/@NiklasBrinkmann1",
            "https://www.linkedin.com/in/brinkmann-niklas/",
            "https://www.niklasbrinkmann.de",
        ]
        social_media_icons = SocialMediaIcons(social_media_links)
        social_media_icons.render()

if __name__ == "__main__":
    homepage()

