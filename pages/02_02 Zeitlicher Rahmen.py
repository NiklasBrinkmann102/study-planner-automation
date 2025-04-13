import streamlit as st
import pandas as pd
import datetime
from st_social_media_links import SocialMediaIcons

st.set_page_config(layout="wide")
st.title('🕒 Deine Lernzeiten')

# Session State initialisieren
if "selected_days" not in st.session_state:
    st.session_state.selected_days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
if "learning_time_type" not in st.session_state:
    st.session_state.learning_time_type = "Jeden Tag gleiche Lernzeit"
if "learning_hours_uniform" not in st.session_state:
    st.session_state.learning_hours_uniform = 3
if "learning_hours_individual" not in st.session_state:
    # Initialisiere mit Standardwerten von 3.0 für jeden Tag
    st.session_state.learning_hours_individual = {day: 3.0 for day in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']}
if "df_plan" not in st.session_state:
    st.session_state.df_plan = pd.DataFrame()
if "learning_start_option" not in st.session_state:
    st.session_state.learning_start_option = "Sofort"
if "learning_start_date" not in st.session_state:
    st.session_state.learning_start_date = datetime.date.today()
if "learning_type" not in st.session_state:
    st.session_state.learning_type = "Deep-Work"

if 'daily_repeat_time' not in st.session_state:
    st.session_state.daily_repeat_time = 30


# Callback-Funktionen
def update_selected_days():
    st.session_state.selected_days = [day for day in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'] 
                                     if st.session_state.get(f"day_{day}", False)]

def update_learning_type():
    st.session_state.learning_type = st.session_state.learning_type_radio

def update_learning_time_type():
    st.session_state.learning_time_type = st.session_state.learning_time_type_radio

def update_learning_hours_uniform():
    st.session_state.learning_hours_uniform = st.session_state.hours_slider

def update_learning_hours_individual(day):
    # Aktualisiere den Wert im learning_hours_individual Dictionary
    st.session_state.learning_hours_individual[day] = st.session_state[f"input_{day}"]

def save_learning_plan():
    day_full_names = {
        'Mo': 'Montag', 'Di': 'Dienstag', 'Mi': 'Mittwoch',
        'Do': 'Donnerstag', 'Fr': 'Freitag', 'Sa': 'Samstag', 'So': 'Sonntag'
    }
    
    if st.session_state.learning_time_type == "Jeden Tag gleiche Lernzeit":
        lernplan = {
            day_full_names[day]: st.session_state.learning_hours_uniform if day in st.session_state.selected_days else 0
            for day in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        }
        total_hours = st.session_state.learning_hours_uniform * len(st.session_state.selected_days)
        st.session_state.info_box = f"""
        ### 🧾 Deine Planung im Überblick
        - 📅 **Ausgewählte Tage:** {', '.join([day_full_names[d] for d in st.session_state.selected_days])}
        - ⏱️ **Lernzeit pro Tag:** {st.session_state.learning_hours_uniform} h
        - 📊 **Gesamtzeit pro Woche:** {total_hours} h
        """
    else:
        # Bei individueller Lernzeit die gespeicherten Werte verwenden
        lernplan = {}
        for day in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']:
            if day in st.session_state.selected_days:
                # Verwende den im Dictionary gespeicherten Wert (Standardwert 3.0)
                lernplan[day_full_names[day]] = st.session_state.learning_hours_individual.get(day, 3.0)
            else:
                lernplan[day_full_names[day]] = 0
                
        # Berechnung der Gesamtzeit
        total = sum(st.session_state.learning_hours_individual.get(d, 3.0) for d in st.session_state.selected_days)
        avg = total / len(st.session_state.selected_days) if st.session_state.selected_days else 0
        
        st.session_state.info_box = f"""
        ### 🧾 Deine Planung im Überblick
        - 📊 **Gesamtzeit pro Woche:** {total:.1f} h
        """

    st.session_state.df_plan = pd.DataFrame(list(lernplan.items()), columns=["Tag", "Lernzeit (h)"])
    st.session_state.plan_saved = True

# Tag Auswahl
st.write('#### An welchen Tagen möchtest du lernen?')
container = st.container(border=True)
cols = container.columns(7)
day_labels = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

# Zeige die Checkboxen an und verwende on_change für sofortige Updates
for i, day in enumerate(day_labels):
    cols[i].checkbox(
        day, 
        value=day in st.session_state.selected_days, 
        key=f"day_{day}",
        on_change=update_selected_days
    )

# Vollständige Namen
day_full_names = {
    'Mo': 'Montag', 'Di': 'Dienstag', 'Mi': 'Mittwoch',
    'Do': 'Donnerstag', 'Fr': 'Freitag', 'Sa': 'Samstag', 'So': 'Sonntag'
}

if not st.session_state.selected_days:
    st.warning("Bitte wähle mindestens einen Tag aus, an dem du lernen möchtest.")
    st.stop()


st.write("#### Wie ist dein Lernstil?")
container = st.container(border=True)



# Optionen für den Lernstil
learning_styles = [
    "Deep-Work",
    "Balanced-Work",
]

col1, col2 = container.columns([1, 3])
with col1:
    st.radio(
        "Wähle deinen bevorzugten Lernstil:",
        options=learning_styles,
        index=learning_styles.index(st.session_state.learning_type),
        key="learning_type_radio",
        on_change=update_learning_type
    )

with col2:
    st.info("""
        **Deep-Work**:  
        Du konzentrierst dich den ganzen Tag auf ein einzelnes Fach. Ideal für tiefes Arbeiten.

        **Balanced-Work**:  
        Maximal 2-3 Fächer pro Tag, mit mindestens 2 Stunden pro Fach. Sorgt für Abwechslung und Struktur.
    """)

# st.caption("Hinweis: Der Algorithmus sorgt für eine Mindestdauer von 2 Stunden pro Fach, um effizientes Lernen zu gewährleisten.")


# Lernzeit-Art auswählen
st.write("#### Wieviele Stunden möchtest du Lernen?")
container = st.container(border=True)
container.radio(
    "Wähle deinen Lernstunden pro Tag:",
    ["Jeden Tag gleiche Lernzeit", "Individuelle Lernzeit pro Tag"],
    index=["Jeden Tag gleiche Lernzeit", "Individuelle Lernzeit pro Tag"].index(st.session_state.learning_time_type),
    key="learning_time_type_radio",
    on_change=update_learning_time_type
)

if st.session_state.learning_time_type == "Jeden Tag gleiche Lernzeit":
    container.slider(
        "Wie viele Stunden möchtest du an jedem Lerntag lernen?",
        min_value=0,
        max_value=8,
        value=st.session_state.learning_hours_uniform,
        step=1,
        key="hours_slider",
        on_change=update_learning_hours_uniform
    )
else:
    container.markdown("Gib die Lernzeit in Stunden für jeden Tag einzeln ein:")
    input_cols = container.columns(len(st.session_state.selected_days))

    for i, day in enumerate(st.session_state.selected_days):
        # Verwende den im Dictionary gespeicherten Wert mit Standardwert 3.0
        default_value = st.session_state.learning_hours_individual.get(day, 3.0)
        with input_cols[i]:
            # Übergebe den Tag an eine lokale Funktion für den Callback
            def make_callback(d=day):
                return lambda: update_learning_hours_individual(d)
                
            st.number_input(
                f"{day_full_names[day]}",
                min_value=0.0,
                max_value=8.0,
                value=default_value,
                step=0.5,
                key=f"input_{day}",
                format="%.1f",
                on_change=make_callback()
            )

# if df_exam.Kategorie.unique() any is "Anki" or Sprache
   
container = st.container(border=True)
if "df_exam" in st.session_state and not st.session_state.df_exam.empty:
    if any(st.session_state.df_exam["Kategorie"].isin(["Anki", "Sprache"])):
        st.write("#### Tägliche Wiederholzeit festlegen")
        st.caption('Da du bei der Fächerwahl Fächer der Kategorien "Anki" oder "Sprache" ausgewählt hast, kannst du hier die tägliche Wiederholzeit festlegen.')
        repeat_container = st.container(border=True)
        repeat_time = repeat_container.slider(
        "Wie viele Minuten möchtest du täglich für Wiederholungen (Anki/Sprache) einplanen?",
        min_value=0,
        max_value=120,
        value=30,
        step=5,
        key="repeat_time_slider"  # Different key for the widget
        )
    else:
        repeat_time = 0

# Now you can safely store this in a different session state variable
st.session_state.daily_repeat_time = repeat_time
        

save_container = st.container()  # New container for the save button

# Lernplan speichern
if "plan_saved" not in st.session_state:
    st.session_state.plan_saved = False
    
if save_container.button("✅ Speichern", on_click=save_learning_plan):
    save_container.success("Dein Lernplan wurde gespeichert!")

# if st.session_state.plan_saved:
#     # container.success("Dein Lernplan wurde gespeichert!")
#     st.info(st.session_state.info_box)


with st.sidebar:
        social_media_links = [
            "https://www.youtube.com/@NiklasBrinkmann1",
            "https://www.linkedin.com/in/brinkmann-niklas/",
            "https://www.niklasbrinkmann.de"
        ]
        social_media_icons = SocialMediaIcons(social_media_links)
        social_media_icons.render()
