import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
import hashlib
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
from io import BytesIO
#from pyxlsb import open_workbook as open_xlsb
from my_func import *
from datetime import datetime, timedelta
import re
import uuid
import base64
from st_social_media_links import SocialMediaIcons

st.set_page_config(layout="wide")
st.title("📅 Überblick für deinen Lernplan")

#-------------------------------------------------------------------
# IMPORT OF DATA AND CLEANING OF LERNPLAN
#-------------------------------------------------------------------

if "df_exam" in st.session_state and not st.session_state.df_exam.empty:
    # st.dataframe(st.session_state.df_exam, use_container_width=True)
    df_exam = st.session_state.df_exam
else:
    st.warning("Du hast noch keine Prüfungen eingetragen.")

if "df_plan" in st.session_state and not st.session_state.df_plan.empty:
    # st.dataframe(st.session_state.df_plan, use_container_width=True)
    df_plan = st.session_state.df_plan
else:
    st.warning("Du hast noch keine Lernzeiten festgelegt.")

if "df_studyplan" not in st.session_state:
    st.session_state.df_studyplan = pd.DataFrame()

if "df_studyplan_clean" in st.session_state and not st.session_state.df_studyplan_clean.empty:
    # st.dataframe(st.session_state.df_plan, use_container_width=True)
    df_studyplan_clean = st.session_state.df_studyplan_clean

## Learntype auslesen und von Auswahl in Stunden umwandeln
if "learning_type" in st.session_state:
    learning_type = st.session_state.learning_type

def LearningType_to_Hours(learning_type):
    if learning_type == "Deep-Work":
        return 8.0
    else:
        return 2.0
learning_type = LearningType_to_Hours(learning_type=learning_type)

def lernplan_daten_aufbereiten(df):
    # DataFrame kopieren, um das Original nicht zu verändern
    df_clean = df.copy()
    # df_clean = df.drop(['Lernfach 3', 'Dauer 3'], axis=1)
    
    # Prüfen, ob Daily Review-Spalte existiert
    if "Daily Review" in df_clean.columns:
        for idx, row in df_clean.iterrows():
            daily_review = row.get("Daily Review")
            
            # Wenn Daily Review mit Lernfach 1 identisch ist
            if pd.notna(daily_review) and daily_review != "None" and daily_review == row.get("Lernfach 1"):
                # Daily Review leeren, da es in Lernfach 1 bereits enthalten ist
                df_clean.at[idx, "Daily Review"] = "None"
            
            # Wenn Daily Review mit Lernfach 2 identisch ist
            elif pd.notna(daily_review) and daily_review != "None" and daily_review == row.get("Lernfach 2"):
                # Daily Review leeren, da es in Lernfach 2 bereits enthalten ist
                df_clean.at[idx, "Daily Review"] = "None"
    return df_clean

def format_studyplan(df):
    return df


# df_studyplan = full_process(df_exam, df_plan, split_threshold=2.0,wiederhol_dauer=0.5)#

df_studyplan, stats = generate_complete_study_plan(df_exam, df_plan, settings = {
            'split_threshold': learning_type,
            'split_ratio': 0.5,
            'exam_proximity_weight': 3.0,
            'fairness_weight': 2.5,
            'min_days_between': 2,
            'max_consecutive_days': 2,
            'dedicated_days_before_exam': 3,
            'wiederhol_dauer': 0.25,
        })
# df_studyplan = lernplan_daten_aufbereiten(df_studyplan)


st.session_state.df_studyplan = df_studyplan

#-------------------------------------------------------------------
# Kalender
#-------------------------------------------------------------------

# Tabs erzeugen
tab1, tab2, tab3 = st.tabs(["📅 Kalenderansicht", "📋 Tabelle", "💾 Export"])

#-------------------------------------------------------------------
# Tab 1
#-------------------------------------------------------------------

# 📅 Tab 1: Kalenderansicht
with tab1:

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
        
        # Für Daily Review - sammle auch diese Fächer
        if "Daily Review" in df_clean.columns:
            for review_entry in df_clean["Daily Review"].dropna().unique():
                if review_entry != "None":
                    # Durch Komma getrennte Fächer aufteilen
                    subjects = [s.strip() for s in review_entry.split(",")]
                    unique_subjects.update(subjects)
        
        # Sortierte Liste der Fächer erstellen, um konsistente Farbzuweisung zu gewährleisten
        sorted_subjects = sorted(list(unique_subjects))
        
        # Farben zuweisen
        color_mapping = {}
        
        # Rot explizit als Farbe für Prüfungen reservieren
        exam_color = "#d62728"  # Rot nur für Prüfungen
        
        # Farbe für Daily Review definieren (als Event-Typ, nicht als Fach)
        daily_review_color = "#E0E0E0"  # Standardfarbe für Daily Review
        
        # Sichere Farbindizes (ohne Rot, welches Index 3 in der Tab10-Palette ist)
        safe_color_indices = [0, 1, 2, 4, 5, 6, 7, 8, 9]  # Alle außer 3 (Rot)
        
        # Konsistente Farbzuweisung basierend auf fester Reihenfolge
        for i, subject in enumerate(sorted_subjects):
            # Verwende nur sichere Farben (ohne Rot)
            color_idx = safe_color_indices[i % len(safe_color_indices)]
            
            # Konvertiere zu Hex-Farbe mit korrekter Formatierung
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
                                    "backgroundColor": color_mapping.get(subject, "#7f7f7f"),  # Konsistente Farbe aus dem Mapping
                                    "borderColor": "#686868",
                                    "textColor": "white",
                                    "description": f"Lernzeit für {subject}: {duration} Stunden",
                                    "display": "block"
                                })
                
                # Daily Review hinzufügen (als Event-Typ, nicht als einzelne Fächer)
                daily_review_spalte = "Daily Review"
                daily_review_dauer = "Dauer 4"  # Annahme: Dauer 4 ist für Daily Review
                
                if daily_review_spalte in row and pd.notna(row[daily_review_spalte]):
                    review_subject = row[daily_review_spalte]
                    review_duration = row.get(daily_review_dauer, 0.25) if daily_review_dauer in row else 0.25
                    
                    # Format korrekt mit Komma trennen
                    if review_subject != "None" and review_duration > 0:
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
            
            # Verarbeitung der Daily Review-Einträge
            if "Daily Review" in df_clean.columns and "Dauer 4" in df_clean.columns:
                for idx, row in df_clean.iterrows():
                    if pd.notna(row["Daily Review"]) and row["Daily Review"] != "None":
                        # Durch Komma getrennte Fächer aufteilen
                        subjects = [s.strip() for s in row["Daily Review"].split(",")]
                        review_hours = row["Dauer 4"] if pd.notna(row["Dauer 4"]) else 0
                        
                        # Stunden gleichmäßig auf die Fächer aufteilen
                        if len(subjects) > 0 and review_hours > 0:
                            hours_per_subject_review = review_hours / len(subjects)
                            for subject in subjects:
                                if subject not in hours_per_subject:
                                    hours_per_subject[subject] = 0
                                hours_per_subject[subject] += hours_per_subject_review
            
            # Anzeigen der Stunden pro Fach - Nur Fächer mit Stunden > 0 anzeigen
            # Sortiere nach Fächern, um eine konsistente Reihenfolge zu gewährleisten
            sorted_subjects_with_hours = sorted(
                [(subject, hours) for subject, hours in hours_per_subject.items() if hours > 0],
                key=lambda x: x[0]  # Sortieren nach Fachname
            )
            
            for subject, hours in sorted_subjects_with_hours:
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

    lernplan_visualisieren(df_studyplan)
#-------------------------------------------------------------------
# Tab 2
#-------------------------------------------------------------------

# 📋 Tab 2: Tabelle
with tab2:
    
    def clean_studyplan_for_user(df):
        df_clean = df.copy()
        
        for i, row in df_studyplan.iterrows():
            if pd.notnull(row['Lernfach 1']):
                df_clean.at[i, 'Lernfach 1'] = f"{row['Lernfach 1']} ({row['Dauer 1']} h)"
            if pd.notnull(row['Lernfach 2']):
                df_clean.at[i, 'Lernfach 2'] = f"{row['Lernfach 2']} ({row['Dauer 2']} h)"
            if row['Daily Review'] != "":
                df_clean.at[i, 'Daily Review'] = f"{row['Daily Review']} ({row['Dauer 4']} h)"


        df_clean = df_clean.drop(['Wochentag', 'Lernzeit (h)', 'Lernfach 3', 'Dauer 3', 'freie_zeit', 'Dauer 1','Dauer 2', 'Dauer 4'], axis=1) 
        return df_clean

    df_studyplan_clean = clean_studyplan_for_user(df_studyplan)
    st.session_state.df_studyplan_clean = df_studyplan_clean

    # st.dataframe(df_studyplan_clean, height=1000, use_container_width=True)
    
    st.title("Lernplan in tabellarischer Form")


        

    def style_pruefung(val):
        """Wenn nicht None, dann rot einfärben"""
        return 'color: red; font-weight: bold;' if pd.notnull(val) and str(val).strip() != 'None' else ''

    def style_df(df):
        # Index zurücksetzen für klare Anzeige
        df = df.reset_index(drop=True)

        styled = df.style.applymap(style_pruefung, subset=['Prüfung'])

        # Datum schöner formatieren (optional)
        df['Datum'] = pd.to_datetime(df['Datum']).dt.strftime('%d.%m.%Y')

        # Stilisierte Tabelle anzeigen
        st.dataframe(styled, use_container_width=True, height=800)


    styled_table = style_df(df_studyplan_clean)
    # st.dataframe(styled_df)




#-------------------------------------------------------------------
# Tab 3
#-------------------------------------------------------------------

# 💾 Tab 3: Export
with tab3:

    def create_ics_entry(summary, start_date_str, duration_hours, description=""):
        """Erstellt einen iCalendar-Eintrag für ein Ereignis"""
        try:
            # Bestimme das Format des Datums und parse es entsprechend
            if isinstance(start_date_str, datetime):
                # Wenn es bereits ein datetime-Objekt ist
                start_time = start_date_str.replace(hour=8, minute=0, second=0, microsecond=0)
            elif isinstance(start_date_str, str):
                if re.match(r'\d{4}-\d{2}-\d{2}', start_date_str):
                    # Format: 'YYYY-MM-DD' oder 'YYYY-MM-DD 00:00:00'
                    date_part = start_date_str.split(' ')[0]
                    start_time = datetime.strptime(f"{date_part} 08:00:00", "%Y-%m-%d %H:%M:%S")
                elif re.match(r'\d{2}\.\d{2}\.\d{2}', start_date_str):
                    # Format: 'DD.MM.YY'
                    start_time = datetime.strptime(f"{start_date_str} 08:00:00", "%d.%m.%y %H:%M:%S")
                else:
                    # Allgemeiner Versuch
                    try:
                        start_time = pd.to_datetime(start_date_str)
                        start_time = start_time.replace(hour=8, minute=0, second=0, microsecond=0)
                    except:
                        # Wenn alles fehlschlägt, heutiges Datum verwenden
                        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
                        st.warning(f"Datum {start_date_str} konnte nicht erkannt werden. Verwende heutiges Datum.")
            else:
                # Wenn es ein anderer Datentyp ist (z.B. pd.Timestamp)
                try:
                    start_time = pd.to_datetime(start_date_str)
                    start_time = start_time.replace(hour=8, minute=0, second=0, microsecond=0)
                except:
                    start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
                    st.warning(f"Datum {start_date_str} konnte nicht erkannt werden. Verwende heutiges Datum.")
            
            # Dauer in Stunden anwenden
            try:
                duration_float = float(duration_hours)
            except (ValueError, TypeError):
                duration_float = 2.0  # Standarddauer als Fallback wenn keine gültige Stundenzahl
            
            end_time = start_time + timedelta(hours=duration_float)
            
            # Formatierung nach iCalendar Standard
            start_time_utc = start_time.strftime("%Y%m%dT%H%M%S")
            end_time_utc = end_time.strftime("%Y%m%dT%H%M%S")
            
            # Eindeutige ID für den Kalendereintrag
            uid = str(uuid.uuid4())
            
            # Erstellung des iCalendar-Eintrags
            ics_entry = [
                "BEGIN:VEVENT",
                f"SUMMARY:{summary}",
                f"DTSTART:{start_time_utc}",
                f"DTEND:{end_time_utc}",
                f"DESCRIPTION:{description}",
                f"UID:{uid}",
                "END:VEVENT"
            ]
            
            return "\n".join(ics_entry)
        except Exception as e:
            st.error(f"Fehler beim Erstellen des Kalendereintrags: {e}")
            return ""

    def extract_hours(fach_info):
        """Extrahiert die Stundenzahl aus verschiedenen Formaten"""
        if pd.isna(fach_info) or fach_info == "" or fach_info == "None":
            return None, 0
        
        if not isinstance(fach_info, str):
            return str(fach_info), 2.0
        
        # Suche nach Stundenzahl im Format "Fach (X.X h)" oder "Fach (X h)"
        hours_match = re.search(r'\((\d+\.?\d*)\s*h\)', fach_info)
        if hours_match:
            hours = float(hours_match.group(1))
            fach_name = fach_info.split('(')[0].strip()
            return fach_name, hours
        
        return fach_info, 2.0  # Standarddauer von 2 Stunden, wenn keine Angabe

    def process_daily_review(daily_review_info):
        """Verarbeitet das Daily Review Format: 'Fach1, Fach2 (X.X h)'
        und gibt eine Liste von (Fach, Stunden) Tupeln zurück."""
        if pd.isna(daily_review_info) or daily_review_info == "" or daily_review_info == "None":
            return []
        
        if not isinstance(daily_review_info, str):
            return [(str(daily_review_info), 2.0)]
        
        # Extrahiere die Gesamtstunden
        hours_match = re.search(r'\((\d+\.?\d*)\s*h\)', daily_review_info)
        if hours_match:
            total_hours = float(hours_match.group(1))
            # Entferne den Stundenteil aus dem String
            faecher_text = daily_review_info.split('(')[0].strip()
        else:
            total_hours = 2.0  # Fallback-Wert
            faecher_text = daily_review_info
        
        # Teile den Text bei Kommas
        faecher = [f.strip() for f in faecher_text.split(',') if f.strip()]
        
        # Wenn Fächer gefunden wurden, teile die Stunden gleichmäßig auf
        if faecher:
            hours_per_fach = total_hours / len(faecher)
            return [(fach, hours_per_fach) for fach in faecher]
        else:
            return [(faecher_text, total_hours)]

    def create_ics_file(df):
        """Erstellt eine vollständige iCalendar-Datei aus dem DataFrame"""
        ics_header = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Lernplan Generator//DE",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        ics_footer = [
            "END:VCALENDAR"
        ]
        
        events = []
        errors = []
        
        # Durchlaufen aller Zeilen im DataFrame
        for idx, row in df.iterrows():
            try:
                if 'Datum' not in row.index or pd.isna(row['Datum']):
                    continue
                    
                datum = row['Datum']
                
                # Prüfung auf Prüfungstermine
                if 'Prüfung' in row.index and pd.notna(row['Prüfung']) and row['Prüfung'] != 'None':
                    prüfung_info = row['Prüfung']
                    fach_name, hours = extract_hours(prüfung_info)
                    if fach_name:
                        summary = f"PRÜFUNG: {fach_name}"
                        ics_entry = create_ics_entry(summary, datum, hours, "Prüfungstermin")
                        if ics_entry:
                            events.append(ics_entry)
                
                # Durchlaufen aller Lernfächer (außer Daily Review und Prüfung)
                for col in row.index:
                    if col not in ['Datum', 'Prüfung', 'Daily Review'] and pd.notna(row[col]) and row[col] != 'None' and row[col] != "":
                        fach_info = row[col]
                        fach_name, hours = extract_hours(fach_info)
                        
                        if fach_name:
                            summary = f"Lernen: {fach_name}"
                            ics_entry = create_ics_entry(summary, datum, hours, f"{hours} Stunden")
                            if ics_entry:
                                events.append(ics_entry)
                
                # Spezielle Verarbeitung für Daily Review
                if 'Daily Review' in row.index and pd.notna(row['Daily Review']) and row['Daily Review'] != 'None' and row['Daily Review'] != "":
                    daily_review_items = process_daily_review(row['Daily Review'])
                    
                    for fach, hours in daily_review_items:
                        if fach:
                            summary = f"Daily Review: {fach}"
                            description = f"Wiederholung: {hours} Stunden"
                            ics_entry = create_ics_entry(summary, datum, hours, description)
                            if ics_entry:
                                events.append(ics_entry)
            except Exception as e:
                errors.append(f"Fehler in Zeile {idx}: {str(e)}")
        
        if errors:
            error_msg = "\n".join(errors[:5])
            if len(errors) > 5:
                error_msg += f"\n... und {len(errors) - 5} weitere Fehler"
            st.warning(f"Einige Einträge konnten nicht verarbeitet werden:\n{error_msg}")
        
        # Zusammenführen aller Teile der iCalendar-Datei
        ics_content = "\n".join(ics_header + events + ics_footer)
        return ics_content

    def get_download_link(file_content, file_name):
        """Erstellt einen Download-Link für die generierte Datei"""
        b64 = base64.b64encode(file_content.encode()).decode()
        href = f'<a href="data:text/calendar;charset=utf-8;base64,{b64}" download="{file_name}" class="button">Kalenderdatei (.ics) herunterladen</a>'
        return href

    # def to_excel(df):
    #     """Konvertiert DataFrame zu Excel-Bytes"""
    #     output = BytesIO()
    #     writer = pd.ExcelWriter(output, engine='xlsxwriter')
    #     df.to_excel(writer, index=False, sheet_name='Lernplan')
    #     workbook = writer.book
    #     worksheet = writer.sheets['Lernplan']
    #     format1 = workbook.add_format({'num_format': '0.00'}) 
    #     worksheet.set_column('A:A', None, format1)  
    #     writer.save()
    #     processed_data = output.getvalue()
    #     return processed_data

    # Streamlit App Layout
    st.title("Export vom Lernplan")
    st.subheader("Kalenderdatei (.ics)")
        # Hilfe-Bereich
    st.write('Du kannst diese Datei problemlos in deinen Kalender importieren, egal ob Apple, Google oder Outlook. Das standardisierte Dateiformat sorgt für maximale Kompatibilität.')

    # Information über erkannte Spalten
    # spalten = df_studyplan_clean.columns.tolist()
    # st.write(f"Erkannte Spalten: {', '.join(spalten)}")

    # Konvertierung und Download
    if st.button("Kalenderdatei erstellen", key="create_calendar"):
        try:
            with st.spinner("Erstelle Kalenderdatei..."):
                # Konvertiere zu iCalendar
                ics_content = create_ics_file(df_studyplan_clean)
                
                if ics_content.count("BEGIN:VEVENT") > 0:
                    # Anzahl der erstellten Ereignisse
                    event_count = ics_content.count("BEGIN:VEVENT")
                    st.success(f"{event_count} Kalendereinträge wurden erfolgreich erstellt!")
                    
                    # Zeige Download-Link an
                    st.markdown(get_download_link(ics_content, "lernplan.ics"), unsafe_allow_html=True)
                    
                    # Zeige Vorschau des iCalendar-Inhalts
                    with st.expander("Vorschau des Kalender-Inhalts"):
                        st.code(ics_content, language="text")
                else:
                    st.error("Es konnten keine Kalendereinträge erstellt werden. Bitte überprüfen Sie Ihre Daten.")
        except Exception as e:
            st.error(f"Fehler bei der Erstellung der Kalenderdatei: {str(e)}")
            st.error("Vollständiger Traceback:")
            import traceback
            st.code(traceback.format_exc())

    with st.expander("Hilfe & Informationen"):
        st.markdown("""

        
        ### Besonderheiten
        
        - Alle Kalendereinträge beginnen um 8:00 Uhr.
        - Beim Daily Review werden mehrere durch Komma getrennte Fächer erkannt und die Zeit gleichmäßig aufgeteilt.
        - Bei Prüfungsterminen wird "PRÜFUNG:" im Titel vorangestellt.
        
        ### Import in Kalender-Apps
        
        Die erzeugte .ics-Datei kann in alle gängigen Kalender-Apps importiert werden:
        
        - **Google Calendar**: Einstellungen → Kalender importieren
        - **Apple Calendar**: Datei → Importieren
        - **Outlook**: Datei → Öffnen & Exportieren → Importieren/Exportieren
        """)

    # # Excel-Export vorbereiten

    # st.divider()

    # # Excel-Export Sektion
    # st.subheader("Excel (.xlsx)")
    # col1, col2 = st.columns([1, 5])
    # col1.download_button(
    #     label='📥 Lernplan als Excel herunterladen',
    #     data=df_xlsx,
    #     file_name='Lernplan.xlsx'
    # )
    # col2.info("""
    #     Du kannst deinen individuell erstellten Lernplan hier als Excel-Datei herunterladen.
    #     Die Tabelle enthält alle geplanten Lerneinheiten und Prüfungen im übersichtlichen Format.
    #     """)
    
    # st.divider()

with st.sidebar:
    social_media_links = [
        "https://www.youtube.com/@NiklasBrinkmann1",
        "https://www.linkedin.com/in/brinkmann-niklas/",
        "https://www.niklasbrinkmann.de"
    ]
    social_media_icons = SocialMediaIcons(social_media_links)
    social_media_icons.render()
