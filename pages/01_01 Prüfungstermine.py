import streamlit as st
import datetime
import pandas as pd
from st_social_media_links import SocialMediaIcons

st.set_page_config(layout="wide")

# Initialize session state variables
if 'subject_data' not in st.session_state:
    st.session_state.subject_data = []

if 'num_subjects' not in st.session_state:
    st.session_state.num_subjects = 1

# -------------------------------------------------------------------------------
# SECTION 1: CALLBACK FUNCTIONS
# -------------------------------------------------------------------------------

def update_num_subjects():
    """Callback to handle number of subjects change"""
    new_num = st.session_state.num_subjects_input
    
    # Adjust subject_data to match the new number of subjects
    while len(st.session_state.subject_data) < new_num:
        st.session_state.subject_data.append({
            "Fachname": "",
            "Kategorie": "Rechenfach",
            "Prüfungsdatum": datetime.date.today(),
            "Schwierigkeit": "🟢 Leicht",
            "Start": "1 Monat vorher"
        })
    
    # Trim if reduced
    if len(st.session_state.subject_data) > new_num:
        st.session_state.subject_data = st.session_state.subject_data[:new_num]
    
    st.session_state.num_subjects = new_num

def save_form_data():
    """Callback to save form data"""
    temp_data = []
    for i in range(st.session_state.num_subjects):
        temp_data.append({
            "Fachname": st.session_state[f"name_{i}"],
            "Kategorie": st.session_state[f"category_{i}"],
            "Prüfungsdatum": st.session_state[f"date_{i}"],
            "Schwierigkeit": st.session_state[f"difficulty_{i}"],
            "Start": st.session_state[f"start_{i}"],
        })
    st.session_state.subject_data = temp_data
    st.session_state.form_submitted = True

def proceed_to_next_step():
    """Callback for next step button"""
    df_exam = pd.DataFrame(st.session_state.subject_data)
    df_exam['Lernstart'] = df_exam.apply(berechne_lernstart, axis=1)
    st.session_state.df_exam = df_exam
    st.session_state.proceed_next = True

# -------------------------------------------------------------------------------
# SECTION 2: UTILITY FUNCTIONS
# -------------------------------------------------------------------------------

today = pd.Timestamp.today().normalize()

def berechne_lernstart(row):
    if row['Start'] == 'Jetzt':
        return today
    elif 'Monat' in row['Start']:
        monate_vorher = int(row['Start'].split()[0])
        lernstart = row['Prüfungsdatum'] - pd.DateOffset(months=monate_vorher)
    elif 'Woche' in row['Start']:
        wochen_vorher = int(row['Start'].split()[0])
        lernstart = row['Prüfungsdatum'] - pd.DateOffset(weeks=wochen_vorher)
    else:
        lernstart = today  # Default value for unclear inputs

    # Check if start date is in the past
    if lernstart < today:
        return today
    else:
        return lernstart

# -------------------------------------------------------------------------------
# SECTION 3: USER INTERFACE
# -------------------------------------------------------------------------------

st.title("📚 Deine Prüfungen")

# Select number of subjects
st.write("#### Für wie viele Prüfungen möchtest du dich vorbereiten?")
container = st.container(border=True)
cols = container.columns(4)

# Use callback for number input
cols[0].number_input(
    "Anzahl der Prüfungen", 
    min_value=1, 
    max_value=10, 
    value=st.session_state.num_subjects,
    step=1,
    key="num_subjects_input",
    on_change=update_num_subjects
)

st.write("#### Gib für jedes Fach die wichtigsten Infos ein")

# Add form for subject data
with st.form("subject_form"):
    for i in range(st.session_state.num_subjects):
        st.markdown(f"**Fach {i+1}**")
        cols = st.columns([2, 2, 2, 2, 2])
        
        # Pre-fill with existing data
        current_data = st.session_state.subject_data[i] if i < len(st.session_state.subject_data) else {
            "Fachname": "",
            "Kategorie": "Rechenfach",
            "Prüfungsdatum": datetime.date.today(),
            "Schwierigkeit": "🟢 Leicht",
            "Start": "1 Monat vorher"
        }
        
        # Use unique keys for all inputs and selectboxes
        cols[0].text_input(
            "Fachname", 
            value=current_data.get("Fachname", ""), 
            key=f"name_{i}",
            placeholder="z. B. Mathematik"
        )
        
        cols[2].date_input(
            "Prüfungsdatum", 
            value=current_data.get("Prüfungsdatum", (datetime.date.today() + datetime.timedelta(days=40))), 
            min_value=datetime.date.today(), 
            key=f"date_{i}"
        )
        
        difficulty_options = ["🟢 Leicht", "🟡 Mittel", "🟠 Anspruchsvoll", "🔴 Schwer"]
        difficulty_index = difficulty_options.index(current_data.get("Schwierigkeit", "🟢 Leicht")) if current_data.get("Schwierigkeit") in difficulty_options else 0
        cols[3].selectbox(
            "Schwierigkeit", 
            difficulty_options, 
            index=difficulty_index, 
            key=f"difficulty_{i}", 
            help="Die Schwierigkeit beeinflusst die geplante Lernzeit. Schwer erhält die meiste Zeit, während Leicht die geringste Zeit zugewiesen wird. Die Gewichtungen sind: Schwer = 100%, Anspruchsvoll = 90%, Mittel = 80%, Leicht = 70%."
        )
        
        category_options = ["Rechenfach", "Auswendiglernen", "Sprache", "Sonstiges", "Anki"]
        category_index = category_options.index(current_data.get("Kategorie", "Rechenfach")) if current_data.get("Kategorie") in category_options else 0
        cols[1].selectbox(
            "Kategorie", 
            category_options, 
            index=category_index, 
            key=f"category_{i}",
            help="Der Algorithmus berücksichtigt bei den Kategorien 'Sprache' und 'Anki' tägliche Wiederholungen. Für andere Kategorien sind diese Wiederholungen nicht relevant, sondern dienen lediglich deiner persönlichen Organisation."
        )
        
        start_options = ["Jetzt", "1 Woche vorher", "2 Wochen vorher", "1 Monat vorher"]
        start_index = start_options.index(current_data.get("Start", "1 Monat vorher")) if current_data.get("Start") in start_options else 3
        cols[4].selectbox(
            "Start", 
            start_options, 
            index=start_index, 
            key=f"start_{i}"
        )
    
    # Submit button with callback
    st.form_submit_button("✅ Speichern", on_click=save_form_data)

st.session_state.df_exam = pd.DataFrame(st.session_state.subject_data)



# Show success message after form submission
if st.session_state.get('form_submitted', False):
    st.success("Alle Fächer wurden erfolgreich gespeichert!")
    st.session_state.form_submitted = False  # Reset flag
    # st.dataframe(df_exam, use_container_width=True)

# if not st.session_state.df_exam.empty:
#     st.dataframe(st.session_state.df_exam, use_container_width=True)

# Display data and next step button
if st.session_state.subject_data:
    df_exam = pd.DataFrame(st.session_state.subject_data)
    df_exam['Lernstart'] = df_exam.apply(berechne_lernstart, axis=1)

with st.expander("Hinweise & Erklärungen"):
    st.write('''
        Hier kannst du bis zu 10 Prüfungen eintragen. Beachte dabei:
        - **Kategorie**: Bestimmt die Lernmethode. Für "Sprache" und "Anki" werden tägliche Wiederholungen eingeplant. Falls du eine der beiden Kategorien auswählst, wird die tägliche Wiederholzeit in Minuten auf der nächsten Seite abgefragt.
        - **Prüfungsdatum**: Das Datum der jeweiligen Prüfung.
        - **Schwierigkeit**: Beeinflusst die relative Lernzeit (Schwer = 100%, Anspruchsvoll = 90%, Mittel = 80%, Leicht = 70%).
        - **Start**: Zeitpunkt, ab dem du mit der Prüfungsvorbereitung beginnen möchtest.
    ''')

with st.sidebar:
    social_media_links = [
        "https://www.youtube.com/@NiklasBrinkmann1",
        "https://www.linkedin.com/in/brinkmann-niklas/",
        "https://www.niklasbrinkmann.de"
    ]
    social_media_icons = SocialMediaIcons(social_media_links)
    social_media_icons.render()

    
    # # Add next step button with callback
    # col1, col2 = st.columns([3, 1])
    # with col2:
    #     st.button(
    #         "✅ Zum nächsten Schritt", 
    #         type="primary", 
    #         on_click=proceed_to_next_step
    #     )
    
    # # Display confirmation if proceeding to next step
    # if st.session_state.get('proceed_next', False):
    #     st.success("Weiter zum nächsten Schritt!")
    #     st.session_state.proceed_next = False  # Reset flag
    
    # Display dataframe
    # st.dataframe(df_exam, use_container_width=True)