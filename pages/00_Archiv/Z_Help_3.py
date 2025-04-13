import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import uuid
import base64

st.set_page_config(layout="wide", page_title="Lernplan Statistik")

# DataFrame aus Session State laden, falls vorhanden
if "df_studyplan_clean" in st.session_state:
    df_studyplan_clean = st.session_state.df_studyplan_clean
else:
    st.error("Keine Lernplandaten gefunden. Bitte laden Sie zuerst Ihre Daten auf der Hauptseite.")
    st.stop()

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

# Streamlit App Layout
st.title("Lernplan Kalender-Konverter")

st.write("""
Diese App konvertiert Ihren Lernplan in eine Kalenderdatei (.ics), 
die Sie in Ihren digitalen Kalender (Google Calendar, Apple Calendar, Outlook etc.) importieren können.
""")

# # Vorschau der Daten
# st.subheader("Vorschau der Daten:")
# st.dataframe(df_studyplan_clean.head(10))

# Information über erkannte Spalten
spalten = df_studyplan_clean.columns.tolist()
st.write(f"Erkannte Spalten: {', '.join(spalten)}")

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

# Hilfe-Bereich
with st.expander("Hilfe & Informationen"):
    st.markdown("""
    ### Format der Lernpläne
    
    Diese App erwartet einen Lernplan mit mindestens folgenden Spalten:
    
    - **Datum**: Das Datum im Format YYYY-MM-DD, DD.MM.YY oder ähnlich
    - **Prüfung**: (Optional) Bezeichnung für Prüfungstermine
    - **Lernfach X**: Beliebige Spalten mit Lernfächern (z.B. "Mathematik (3.0 h)")
    - **Daily Review**: (Optional) Tägliche Wiederholungen im Format "Fach1, Fach2 (X.X h)"
    
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
