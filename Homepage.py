import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from streamlit_calendar import calendar
# from st_social_media_links import SocialMediaIcons

def homepage():
    # Page configuration
    st.set_page_config(
        page_title="Prüfungsplaner | Lerne effizienter  sdfsd",
        page_icon="📚",
        layout="wide"
    )
    
    # Header with logo
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("# 📚")
    with col2:
        st.title("Prüfungsplaner")
        st.write("#### Erstelle deinen optimalen Lernplan für maximalen Erfolg")
    
    # Divider
    st.divider()
    
    # Hero section
    st.header("Nie wieder Prüfungsstress!", anchor=False)
    
    # Two columns for video and main features
    video_col, text_col = st.columns([3, 2])
    
    with video_col:
        # Embed YouTube video
        st.video("https://www.youtube.com/watch?v=AbRlFdrz09s")
        st.caption("Schau dir das Video an, um zu sehen, wie der Prüfungsplaner funktioniert")
    
    with text_col:
        st.info("""
        ### Was ist der Prüfungsplaner?
        
        Der Prüfungsplaner ist dein persönlicher Assistent für die optimale Prüfungsvorbereitung. 
        Basierend auf deinen Prüfungsterminen und Lernpräferenzen erstellt er einen individuellen Lernplan, der dich optimal auf deine Prüfungen vorbereitet.
        
        ### So funktioniert's:
        
        1. **Prüfungen eingeben** - Trage deine Prüfungstermine ein
        2. **Präferenzen definieren** - Bestimme, wann und wie du am liebsten lernst
        3. **Plan generieren** - Erhalte deinen personalisierten Lernplan
        4. **Erfolg!** - Folge dem Plan und bestehe deine Prüfungen mit Bestnoten
        """)
    
    # Main benefits in three columns
    st.header("Deine Vorteile", anchor=False)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 🧠 Optimale Lernverteilung\n\nDurch wissenschaftlich fundierte Lernmethoden wird der Stoff optimal verteilt, um das langfristige Behalten zu maximieren.")
        
    with col2:
        st.success("### ⏱️ Zeitmanagement\n\nVermeide Last-Minute-Stress und nutze deine verfügbare Zeit effizient durch einen ausgewogenen Lernplan.")
        
    with col3:
        st.warning("### 📅 Tägliche Struktur\n\nKlare tägliche Lernziele geben dir Orientierung und sorgen für kontinuierlichen Fortschritt im Studium, Abitur oder worauf sonst du auch lernen möchtest.")
    
    # Features section
    st.header("Was der Prüfungsplaner kann", anchor=False)
    
    # Feature list
    features = [
        {
            "icon": "📊", 
            "title": "Intelligente Priorisierung", 
            "desc": "Der Algorithmus berücksichtigt die Wichtigkeit und Schwierigkeit jedes Fachs und plant entsprechend."
        },
        {
            "icon": "🔄", 
            "title": "Regelmäßige Wiederholungen", 
            "desc": "Integrierte 'Daily Reviews' helfen dir, das Gelernte langfristig zu behalten."
        },
        {
            "icon": "📱", 
            "title": "Kalenderansicht", 
            "desc": "Übersichtliche Kalenderdarstellung mit farblicher Kennzeichnung der verschiedenen Fächer."
        },
        {
            "icon": "📈", 
            "title": "Fortschrittsübersicht", 
            "desc": "Sehe auf einen Blick, wie viel du bereits geschafft hast und wie viel noch vor dir liegt."
        },
        {
            "icon": "⚙️", 
            "title": "Anpassbar", 
            "desc": "Passe den Plan an deine individuellen Bedürfnisse und deinen Tagesrhythmus an."
        },
        {
            "icon": "📱", 
            "title": "Export-Funktion", 
            "desc": "Exportiere deinen Lernplan als PDF oder in deinen digitalen Kalender."
        }
    ]
    
    # Display features in 2x3 grid
    rows = [st.columns(3) for _ in range(2)]
    
    for i, feature in enumerate(features):
        row = i // 3
        col = i % 3
        with rows[row][col]:
            feature_text = f"### {feature['icon']} {feature['title']}\n{feature['desc']}"
            st.container().write(feature_text)
    
    # Scientific background
    st.header("Wissenschaftlich fundiert", anchor=False)
    
    st.info("""
    Der Prüfungsplaner basiert auf wissenschaftlichen Erkenntnissen zum Lernen und Gedächtnis:
    
    - **Spaced Repetition** - Optimale Wiederholungsintervalle für langfristiges Behalten
    - **Verteiltes Lernen** - Mehrere kürzere Lerneinheiten sind effektiver als eine lange
    - **Interleaving** - Wechsel zwischen verschiedenen Themen verbessert das Verständnis
    - **Prioritätsbasiertes Lernen** - Fokus auf die wichtigsten und schwierigsten Themen
    """)
    
    # Call-to-Action
    st.header("Erstelle jetzt deinen personalisierten Lernplan!", anchor=False)
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_start, col_tutorial = st.columns(2)
        with col_start:
            st.button("Starten", type="primary", use_container_width=True)
        with col_tutorial:
            st.button("Tutorial ansehen", use_container_width=True)
    
    # Footer
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        st.write("© 2025 Prüfungsplaner")
    with footer_col2:
        st.write("Datenschutz | Impressum | Kontakt")
    with footer_col3:
        # Social media links
        social_media_links = [
            "https://www.youtube.com/@NiklasBrinkmann1",
            "https://www.linkedin.com/in/brinkmann-niklas/",
            "https://www.niklasbrinkmann.de"
        ]


    # with st.sidebar:
    #     social_media_links = [
    #         "https://www.youtube.com/@NiklasBrinkmann1",
    #         "https://www.linkedin.com/in/brinkmann-niklas/",
    #         "https://www.niklasbrinkmann.de"
    #     ]
    #     social_media_icons = SocialMediaIcons(social_media_links)
    #     social_media_icons.render()




if __name__ == "__main__":
    homepage()