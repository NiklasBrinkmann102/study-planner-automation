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

        

            # st.image("Image_Workflow.png")
        st.video("https://youtu.be/WnzZktzy958")
    container = st.container(border=True)
    with container:
        st.container().subheader("In 3 einfachen Schritten:")

        steps_container = st.container()
        
        steps_container.markdown("### 1️⃣ Prüfungen eintragen")
        steps_container.write(
            "Lege deine Prüfungen mit wenigen Klicks an: gib Fachnamen, "
            "Kategorie (z. B. Theorie, Sprache, Anki), Schwierigkeitsgrad, "
            "Prüfungsdatum und das gewünschte Startdatum fürs Lernen ein. "
            "Der Schwierigkeitsgrad hilft dabei, die Lernzeit automatisch sinnvoll zu gewichten."
            "Anki und Sprache als Kategorie sorgen für tägliche Wiederholungen"
        )

        steps_container.markdown("### 2️⃣ Lernpräferenzen festlegen")
        steps_container.write(
            "Bestimme, wann und wie du lernen möchtest. Wähle deinen Lernstil "
            "(z. B. Deep Work = 1 Fach pro Tag, oder Balanced = bis zu 3 Fächer pro Tag) "
            "und gib an, wie viele Stunden du täglich investieren kannst – entweder pauschal oder je Tag individuell. "
            "Wenn du ein Fach mit Wiederholungsbedarf hast, z. B. Sprachen oder Anki, kannst du hier auch "
            "tägliche Wiederholzeiten festlegen."
        )

        steps_container.markdown("### 3️⃣ Lernplan erhalten")
        steps_container.write(
            "Der Planer generiert deinen persönlichen Lernplan – mit klarer Übersicht, "
            "welches Fach du wann und wie lange lernen sollst. "
            "Den fertigen Plan kannst du als Tabelle exportieren oder als .ics-Datei in deinen Kalender "
            "(Outlook, Apple, Google etc.) integrieren. "
            "So hast du deinen Lernplan immer im Blick – ganz automatisch, individuell und kostenlos."
        )

            
            # st.button("Jetzt starten", type="primary", use_container_width=True)
        

    st.header("Funktionen auf einen Blick")
    container = st.container(border=True)
    with container:

        # Display features in 2x3 grid
        feature_cols1 = st.columns(3)
        feature_cols2 = st.columns(3)

        # Erste Zeile mit Features
        with feature_cols1[0]:
            st.subheader("📊 Intelligente Priorisierung")
            st.write("Automatische Gewichtung nach Wichtigkeit und individuellem Schwierigkeitsgrad")

        with feature_cols1[1]:
            st.subheader("🔄 Spaced Repetition")
            st.write("Wissenschaftlich optimierte Wiederholungsintervalle für besseres Behalten")

        with feature_cols1[2]:
            st.subheader("📱 Kalenderansicht")
            st.write("Übersichtliche Darstellung mit farblicher Kennzeichnung der Fächer")

        # Zweite Zeile mit Features
        with feature_cols2[0]:
            st.subheader("📈 Statistik")
            st.write("Übersicht zu Lernstunden und Tagen  bis zur Prüfung")

        with feature_cols2[1]:
            st.subheader("⚙️ Anpassbarkeit")
            st.write("Berücksichtigung deiner Tagesroutine und Lernpräferenzen")

        with feature_cols2[2]:
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

