import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import hashlib
from datetime import datetime
import pytz
import matplotlib.pyplot as plt

if "df_studyplan" not in st.session_state:
    st.session_state.df_studyplan = pd.DataFrame()
df_studyplan = st.session_state.df_studyplan

def lernplan_visualisieren(df_studyplan):
    """
    Generische Funktion zur Visualisierung eines Lernplans als Kalender
    
    Parameter:
    df_studyplan: DataFrame mit mind. Spalten für Datum, Lernfächer, Prüfungen etc.
    """
    # DataFrame vorbereiten
    df_clean = df_studyplan.copy()
    
    # Titel für den Kalender
    st.title("Lernplan Kalender")
    
    # Matplotlib's Tab10 Farbpalette für verschiedene Fächer verwenden
    tab10_colors = plt.get_cmap('tab10').colors
    
    # Farben für jedes Fach dynamisch zuweisen
    unique_subjects = set()
    
    # Alle Lernfächer sammeln
    for i in range(1, 4):  # Bis zu 3 Lernfächer
        fach_spalte = f"Lernfach {i}"
        if fach_spalte in df_clean.columns:
            subjects = [s for s in df_clean[fach_spalte].dropna().unique() if s != "None"]
            unique_subjects.update(subjects)
    
    # Farben zuweisen
    color_mapping = {}
    
    # Rot explizit als Farbe für Prüfungen reservieren
    exam_color = "#d62728"  # Rot nur für Prüfungen
    
    # Farbe für Daily Review definieren
    daily_review_color = "#E0E0E0"  # Standardfarbe für Daily Review
    
    # Sichere Farbindizes (ohne Rot, welches Index 3 in der Tab10-Palette ist)
    safe_color_indices = [0, 1, 2, 4, 5, 6, 7, 8, 9]
    
    # Fixierte Farben für bestimmte Fächer, um Konsistenz zu gewährleisten
    # WICHTIG: Hier werden die Farben explizit zugewiesen, damit sie im Kalender und in der Legende übereinstimmen
    color_mapping["Mathe"] = "#{:02x}{:02x}{:02x}".format(
        int(tab10_colors[0][0] * 255),
        int(tab10_colors[0][1] * 255),
        int(tab10_colors[0][2] * 255)
    )  # Blau
    
    color_mapping["Spanisch"] = "#{:02x}{:02x}{:02x}".format(
        int(tab10_colors[1][0] * 255),
        int(tab10_colors[1][1] * 255),
        int(tab10_colors[1][2] * 255)
    )  # Orange
    
    color_mapping["Thermo"] = "#{:02x}{:02x}{:02x}".format(
        int(tab10_colors[2][0] * 255),
        int(tab10_colors[2][1] * 255),
        int(tab10_colors[2][2] * 255)
    )  # Grün
    
    color_mapping["Statistik"] = "#{:02x}{:02x}{:02x}".format(
        int(tab10_colors[4][0] * 255),
        int(tab10_colors[4][1] * 255),
        int(tab10_colors[4][2] * 255)
    )  # Lila
    
    # Für alle anderen Fächer, die nicht explizit zugewiesen wurden
    current_color_idx = 0  # Starte mit dem ersten sicheren Index
    for subject in unique_subjects:
        if subject not in color_mapping:
            # Verwende nur sichere Farben (nicht Rot)
            color_idx = safe_color_indices[current_color_idx % len(safe_color_indices)]
            current_color_idx += 1
            
            # Überprüfe, ob die Farbe bereits rot ist, und überspringe sie
            if color_idx == 3:  # 3 ist rot in der Tab10-Palette
                color_idx = 4
            
            # Konvertiere zu Hex-Farbe
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(tab10_colors[color_idx][0] * 255),
                int(tab10_colors[color_idx][1] * 255),
                int(tab10_colors[color_idx][2] * 255)
            )
            color_mapping[subject] = hex_color
    
    @st.cache_data
    def create_calendar_events(df):
        """
        Wandelt einen DataFrame mit Lernplan-Daten in eine Liste von Kalender-Events um
        """
        events = []
        
        for index, row in df.iterrows():
            # Datum aus dem DataFrame extrahieren und formatieren
            date_obj = pd.to_datetime(row["Datum"])
            date_str = date_obj.strftime("%Y-%m-%d")
            
            # Prüfungen als Ereignisse hinzufügen (falls vorhanden)
            if "Prüfung" in row and pd.notna(row["Prüfung"]) and row["Prüfung"] != "None":
                exam_subject = row["Prüfung"]
                event_id = hashlib.md5(f"exam_{date_str}_{exam_subject}".encode()).hexdigest()
                events.append({
                    "id": event_id,
                    "title": f"{exam_subject}",
                    "start": date_str,
                    "backgroundColor": exam_color,
                    "borderColor": "#b01e1e",
                    "textColor": "white",
                    "description": f"Prüfung in {exam_subject}",
                    "display": "block",
                    "allDay": True
                })
            
            # Dynamisch durch alle Lernfächer zyklieren
            for i in range(1, 4):  # Maximal 3 Lernfächer pro Tag unterstützt
                fach_spalte = f"Lernfach {i}"
                dauer_spalte = f"Dauer {i}"
                
                if fach_spalte in row and dauer_spalte in row:
                    if pd.notna(row[fach_spalte]) and row[fach_spalte] != "None":
                        if pd.notna(row[dauer_spalte]) and row[dauer_spalte] > 0:
                            subject = row[fach_spalte]
                            duration = row[dauer_spalte]
                            
                            event_id = hashlib.md5(f"subject{i}_{date_str}_{subject}".encode()).hexdigest()
                            events.append({
                                "id": event_id,
                                "title": f"{subject} ({duration}h)",
                                "start": date_str,
                                "backgroundColor": color_mapping.get(subject, "#7f7f7f"),
                                "borderColor": "#686868",
                                "textColor": "white",
                                "description": f"Lernzeit für {subject}: {duration} Stunden",
                                "display": "block"
                            })
            
            # Daily Review hinzufügen (falls vorhanden)
            daily_review_spalte = "Daily Review"
            daily_review_dauer = "Dauer 4"  # Annahme: Dauer 4 ist für Daily Review
            
            if daily_review_spalte in row and pd.notna(row[daily_review_spalte]):
                review_subject = row[daily_review_spalte]
                review_duration = row.get(daily_review_dauer, 0.25) if daily_review_dauer in row else 0.25
                
                # Format korrekt mit Komma trennen und nicht als eigenes Fach betrachten
                if review_subject != "None" and review_duration > 0:
                    # Verwende den Daily Review mit korrektem Format (z.B. "Spanisch, Chinesisch")
                    event_id = hashlib.md5(f"review_{date_str}".encode()).hexdigest()
                    
                    # Für Daily Review eine einfache graue Farbe verwenden
                    events.append({
                        "id": event_id,
                        "title": f"Daily: {review_subject} ({review_duration}h)",
                        "start": date_str,
                        "backgroundColor": daily_review_color,
                        "borderColor": "#a0a0a0",
                        "textColor": "black",
                        "description": f"Tägliche Wiederholung: {review_subject} ({review_duration}h)",
                        "display": "block"
                    })
        
        return events
    
    # Kalender-Ereignisse aus dem DataFrame erstellen
    events = create_calendar_events(df_clean)
    
    # Kalender-Konfiguration mit Montag als erstem Tag
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "dayGridMonth",
        "height": "auto",
        "selectable": True,
        "weekNumbers": True,
        "dayMaxEvents": 3,
        "navLinks": True,
        "rerenderDelay": 300,
        "lazyFetching": True,
        "firstDay": 1  # 1 für Montag (0 wäre Sonntag)
    }
    
    # Kalender mit voller Breite anzeigen
    calendar_component = calendar(
        events=events,
        options=calendar_options,
        custom_css="""
        .fc-event {
            margin: 2px 0;
            border-radius: 3px;
            font-weight: 500;
        }
        .fc-event-title {
            font-weight: 600;
            padding: 3px;
        }
        .fc-daygrid-day-number {
            font-weight: bold;
        }
        """
    )
    
    st.divider()

    # Statistiken-Bereich erstellen
    st.header("Statistiken")
    
    # Stats in mehreren Spalten anzeigen für besseres Layout
    stats_cols = st.columns(3)
    
    with stats_cols[0]:
        st.subheader("Gesamtübersicht")
        # Prüfen, ob die Spalte existiert
        if "Lernzeit (h)" in df_clean.columns:
            total_hours = df_clean["Lernzeit (h)"].sum()
            st.metric("Gesamte Lernzeit", f"{total_hours:.1f} Stunden")
        
        # Stunden pro Fach dynamisch berechnen
        hours_per_subject = {}
        
        # Durch alle möglichen Lernfächer iterieren
        for i in range(1, 4):  # Bis zu 3 Lernfächer
            fach_spalte = f"Lernfach {i}"
            dauer_spalte = f"Dauer {i}"
            
            if fach_spalte in df_clean.columns and dauer_spalte in df_clean.columns:
                for subject in df_clean[fach_spalte].dropna().unique():
                    if subject != "None":
                        subject_hours = df_clean[df_clean[fach_spalte] == subject][dauer_spalte].sum()
                        if subject not in hours_per_subject:
                            hours_per_subject[subject] = 0
                        hours_per_subject[subject] += subject_hours
        
        # Hier die Verarbeitung der Daily Review-Einträge anpassen
        if "Daily Review" in df_clean.columns and "Dauer 4" in df_clean.columns:
            for review_entry in df_clean["Daily Review"].dropna().unique():
                if review_entry != "None":
                    # Durch Komma getrennte Fächer aufteilen
                    subjects = [s.strip() for s in review_entry.split(",")]
                    review_hours = df_clean[df_clean["Daily Review"] == review_entry]["Dauer 4"].sum()
                    
                    # Stunden gleichmäßig auf die Fächer aufteilen (hälfte zu einem, hälfte zum anderen)
                    if len(subjects) > 1:
                        hours_per_subject_review = review_hours / len(subjects)
                        for subject in subjects:
                            if subject not in hours_per_subject:
                                hours_per_subject[subject] = 0
                            hours_per_subject[subject] += hours_per_subject_review
                    else:
                        # Falls nur ein Fach, alle Stunden diesem zuweisen
                        subject = subjects[0]
                        if subject not in hours_per_subject:
                            hours_per_subject[subject] = 0
                        hours_per_subject[subject] += review_hours
        
        # Anzeigen der Stunden pro Fach - Nur Fächer mit Stunden > 0 anzeigen
        for subject, hours in hours_per_subject.items():
            if hours > 0:  # Filtere Einträge mit 0 Stunden raus
                color = color_mapping.get(subject, "#7f7f7f")
                st.markdown(
                    f"""<div style='display: flex; align-items: center;'>
                           <div style='background-color: {color}; width: 12px; height: 12px; margin-right: 8px; border-radius: 2px;'></div>
                           <div>{subject}: <b>{hours:.1f} Stunden</b></div>
                       </div>""",
                    unsafe_allow_html=True
                )
    
    with stats_cols[1]:
        # Anzahl der Prüfungen
        today = datetime.now(pytz.timezone('Europe/Berlin')).date()
        if "Prüfung" in df_clean.columns:
            st.subheader("Prüfungen")
            exam_count = df_clean[df_clean["Prüfung"] != "None"]["Prüfung"].count()
            st.metric("Anzahl Prüfungen", exam_count)
    
    with stats_cols[2]:
        if "Prüfung" in df_clean.columns:
            st.header("Tage bis zur Prüfung")
            
            # Prüfungstermine auslesen und sortieren
            upcoming_exams = []
            for index, row in df_clean.iterrows():
                if pd.notna(row["Prüfung"]) and row["Prüfung"] != "None":
                    exam_date = pd.to_datetime(row["Datum"]).date()
                    days_remaining = (exam_date - today).days
                    if days_remaining >= 0:  # Nur zukünftige Prüfungen
                        upcoming_exams.append({
                            "subject": row["Prüfung"],
                            "date": exam_date,
                            "days_remaining": days_remaining
                        })
            
            # Nach verbleibenden Tagen sortieren
            upcoming_exams.sort(key=lambda x: x["days_remaining"])
            
            # Anzeigen der Countdown-Boxen untereinander
            if upcoming_exams:
                for exam in upcoming_exams:
                    days = exam["days_remaining"]
                    subject = exam["subject"]
                    
                    # Farbcodierung je nach Dringlichkeit
                    if days <= 7:
                        color = "#FF6B6B"  # Rot für < 1 Woche
                    elif days <= 14:
                        color = "#FFD166"  # Gelb für < 2 Wochen
                    else:
                        color = "#06D6A0"  # Grün für > 2 Wochen
                        
                    st.markdown(
                        f"""
                        <div style="background-color: {color}; border-radius: 3px; 
                        padding: 3px 6px; margin: 2px 0; color: {'black' if days > 7 else 'white'}; 
                        display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.1em;">{subject}</span>
                        <span style="font-weight: bold; font-size: 0.8em;">{days} T</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                st.info("Keine bevorstehenden Prüfungen gefunden.")
        # # Lernfortschritt
        # st.subheader("Lernfortschritt")
        
        # # Aktuelles Datum
        # today = datetime.now(pytz.timezone('Europe/Berlin')).date()
        
        # # Berechne Gesamtfortschritt
        # total_days = len(df_clean)
        # days_passed = sum(1 for date_str in df_clean["Datum"] if pd.to_datetime(date_str).date() <= today)
        # progress_pct = int((days_passed / total_days) * 100) if total_days > 0 else 0
        
        # # Fortschrittsbalken
        # st.progress(progress_pct)
        # st.write(f"Fortschritt: {progress_pct}% ({days_passed} von {total_days} Tagen)")
    
    # Divider vor dem Countdown-Bereich
    st.divider()
    
    # Countdown zu Prüfungen in einem eigenen Bereich
    

lernplan_visualisieren(df_studyplan)