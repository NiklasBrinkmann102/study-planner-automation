
"""
Study Plan Generator
-------------------
A tool to create optimized study plans based on exam schedules, subject difficulty, and available study hours.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

# -------------------------------------------------------------------------------
# SECTION 1: DATA PREPARATION
# -------------------------------------------------------------------------------

def prepare_exams(df_exam):
    """Convert dates to datetime and map difficulty levels to numerical values."""
    df_exam['Prüfungsdatum'] = pd.to_datetime(df_exam['Prüfungsdatum'])
    schwierigkeit_mapping = {
        '🟢 Leicht': 0,
        '🟡 Mittel': 1,
        '🟠 Anspruchsvoll': 2,
        '🔴 Schwer': 3
    }
    df_exam['Schwierigkeit_Nr'] = df_exam['Schwierigkeit'].map(schwierigkeit_mapping)
    return df_exam


def prepare_plan(df_plan):
    """Convert weekday names to integers (0-6)."""
    wochentag_map = {
        'Montag': 0,
        'Dienstag': 1,
        'Mittwoch': 2,
        'Donnerstag': 3,
        'Freitag': 4,
        'Samstag': 5,
        'Sonntag': 6
    }
    df_plan['Weekday (int)'] = df_plan['Tag'].map(wochentag_map)
    return df_plan


def berechne_lernstart(row):
    """Calculate study start date based on settings."""
    today = pd.Timestamp.today().normalize()
    
    if row['Start'] == 'Jetzt':
        return today
    elif 'Monat' in row['Start']:
        monate_vorher = int(row['Start'].split()[0])
        # Calculate start date properly using DateOffset
        lernstart = row['Prüfungsdatum'] - pd.DateOffset(months=monate_vorher)
    elif 'Woche' in row['Start']:
        wochen_vorher = int(row['Start'].split()[0])
        # Calculate start date properly using DateOffset
        lernstart = row['Prüfungsdatum'] - pd.DateOffset(weeks=wochen_vorher)
    else:
        lernstart = today  # Default value for unclear inputs

    # Check if study start date is in the past
    if lernstart < today:
        return today
    else:
        return lernstart


def cleanup_exam_data(df_exam):
    """Remove unnecessary columns after processing."""
    df_copy = df_exam.copy()
    # Instead of dropping, we'll keep these for reference but add the necessary columns
    return df_copy


def berechne_gesamt_lernzeit(df_exam, df_plan):
    """Calculate total available study time based on exam and plan data."""
    # Define time period
    start_datum = df_exam["Lernstart"].min()
    end_datum = df_exam["Prüfungsdatum"].max()
    datum_range = pd.date_range(start=start_datum, end=end_datum)
    gesamttage = len(datum_range)

    # Build calendar
    df_kalender = pd.DataFrame({"Datum": datum_range})
    df_kalender["Wochentag"] = df_kalender["Datum"].dt.weekday

    # Assign study time per weekday
    df_kalender = df_kalender.merge(
        df_plan[["Weekday (int)", "Lernzeit (h)"]],
        left_on="Wochentag", right_on="Weekday (int)", how="left"
    )
    df_kalender = df_kalender.drop('Weekday (int)', axis=1)
    
    # Only consider days with study time
    valid_calendar = df_kalender[df_kalender["Lernzeit (h)"] > 0].copy()

    # Calculate total study time
    gesamtstunden = valid_calendar["Lernzeit (h)"].sum()

    return gesamtstunden, gesamttage, df_kalender


def erweitere_kalender_mit_pruefungstagen(df_kalender, df_exam):
    """Add exam dates to the calendar."""
    df_kalender = df_kalender.copy()
    df_kalender["Prüfung"] = None  # Empty column for exam subjects
    
    # Convert date to datetime if not already done
    df_kalender["Datum"] = pd.to_datetime(df_kalender["Datum"])
    
    for _, row in df_exam.iterrows():
        fach = row["Fachname"]
        pruefungsdatum = pd.to_datetime(row["Prüfungsdatum"])
        
        # Check if an exam subject is already entered for this day
        existing_entry = df_kalender.loc[df_kalender["Datum"] == pruefungsdatum, "Prüfung"].values
        
        if len(existing_entry) > 0 and pd.notna(existing_entry[0]):
            # If a subject is already entered, add the new subject separated by comma
            df_kalender.loc[df_kalender["Datum"] == pruefungsdatum, "Prüfung"] = existing_entry[0] + ", " + fach
        else:
            # Otherwise, enter the subject directly
            df_kalender.loc[df_kalender["Datum"] == pruefungsdatum, "Prüfung"] = fach
    
    return df_kalender


def berechne_zielstunden(df_exam, df_kalender):
    """Calculate target hours for each subject based on difficulty."""
    # Weight mapping based on difficulty
    gewicht_map = {3: 1.0, 2: 0.9, 1: 0.8, 0: 0.7}
    df_exam = df_exam.copy()
    
    # Add weighting
    df_exam['Gewichtung'] = df_exam['Schwierigkeit_Nr'].map(gewicht_map)
    
    # Calculate total hours
    gesamtstunden = df_kalender['Lernzeit (h)'].sum()
    
    # Calculate target hours
    summe_gewichtungen = df_exam['Gewichtung'].sum()
    if summe_gewichtungen > 0:  # Prevent division by zero
        df_exam['Stundenanteil (%)'] = df_exam['Gewichtung'] / summe_gewichtungen
        df_exam['Zielstunden'] = (df_exam['Stundenanteil (%)'] * gesamtstunden).round(1)
    else:
        df_exam['Stundenanteil (%)'] = 0
        df_exam['Zielstunden'] = 0
    
    return df_exam


def erstelle_fächer(df_kalender):
    """Create study subjects columns in the calendar."""
    df_lernplan = df_kalender.copy()
    for i in range(1, 4):
        df_lernplan[f'Lernfach {i}'] = None
        df_lernplan[f'Dauer {i}'] = 0.0  # Use float instead of int for consistency
    return df_lernplan


def aktualisiere_freie_zeit(df):
    """Update the free time on the calendar, handling exam days correctly."""
    df = df.copy()
    
    # First set study time to 0 on exam days 
    for i, row in df.iterrows():
        if pd.notna(row['Prüfung']):
            df.at[i, 'Lernzeit (h)'] = 0.0
            # Also reset any study subjects and durations on exam days
            for j in range(1, 4):
                df.at[i, f'Lernfach {j}'] = None
                df.at[i, f'Dauer {j}'] = 0.0
    
    # Then calculate free time based on available study time minus planned time
    df["freie_zeit"] = df["Lernzeit (h)"] - df[["Dauer 1", "Dauer 2", "Dauer 3"]].sum(axis=1)
    # Ensure free time is never negative
    df["freie_zeit"] = df["freie_zeit"].clip(lower=0)
    
    return df


# -------------------------------------------------------------------------------
# SECTION 2: SCHEDULING DAILY REVIEWS
# -------------------------------------------------------------------------------

def plane_daily_reviews(df_pre, df_exam, wiederhol_dauer=0.5):
    """Plan daily review sessions for Anki and language subjects."""
    # Initialize columns if not present
    if "Daily Review" not in df_pre.columns:
        df_pre["Daily Review"] = ""
    if "Dauer 4" not in df_pre.columns:
        df_pre["Dauer 4"] = 0.0

    # Determine the second-to-last exam date
    if len(df_exam) > 1:
        letzter_termin = df_exam.sort_values("Prüfungsdatum")["Prüfungsdatum"].iloc[-2]
    else:
        letzter_termin = df_exam["Prüfungsdatum"].max()  # If only one exam
    
    letzter_termin = pd.to_datetime(letzter_termin)

    # Create a copy to avoid the SettingWithCopyWarning
    df_result = df_pre.copy()

    for _, fach_row in df_exam.iterrows():
        if fach_row["Kategorie"] not in ["Anki", "Sprache"]:
            continue

        fach = fach_row["Fachname"]
        start = pd.to_datetime(fach_row["Lernstart"])
        ende = pd.to_datetime(fach_row["Prüfungsdatum"])

        for idx, row in df_result.iterrows():
            datum = pd.to_datetime(row["Datum"])
            
            # Skip if outside study period for this subject
            if not (start <= datum <= ende):
                continue
                
            # Skip if after the second-to-last exam
            if datum > letzter_termin:
                continue
                
            # Skip if there's an exam on this day
            if pd.notna(row["Prüfung"]):
                continue

            # Skip if the next day has an exam
            next_day = datum + pd.Timedelta(days=1)
            next_day_rows = df_result[df_result["Datum"] == next_day]
            if not next_day_rows.empty and pd.notna(next_day_rows.iloc[0]["Prüfung"]):
                continue

            # Skip if there's not enough available time
            if row["Lernzeit (h)"] < wiederhol_dauer:
                continue

            # Add the subject to daily reviews if not already included
            aktuelle_review = df_result.at[idx, "Daily Review"]
            if not aktuelle_review or fach not in aktuelle_review.split(", "):
                neue_review = f"{aktuelle_review}, {fach}" if aktuelle_review else fach
                df_result.at[idx, "Daily Review"] = neue_review.strip(", ")
                df_result.at[idx, "Dauer 4"] += wiederhol_dauer
                
                # Update available study time and free time
                df_result.at[idx, "Lernzeit (h)"] -= wiederhol_dauer
                if "freie_zeit" in df_result.columns:
                    df_result.at[idx, "freie_zeit"] -= wiederhol_dauer
                    # Ensure free time doesn't go negative
                    df_result.at[idx, "freie_zeit"] = max(0, df_result.at[idx, "freie_zeit"])

    return df_result


# -------------------------------------------------------------------------------
# SECTION 3: PLANNING STUDY SESSIONS
# -------------------------------------------------------------------------------

def fülle_vortage_aller_prüfungen(df_all):
    """Fill the days before exams with study time for the exam subjects."""
    df = df_all.copy()
    df["Datum"] = pd.to_datetime(df["Datum"])
    
    # Extract exams
    df_pruefungen = df[df["Prüfung"].notna()].sort_values("Datum").reset_index(drop=True)
    if len(df_pruefungen) < 1:
        print("No exams available.")
        return df
    
    # Sort in reverse order to start with later exams
    df_pruefungen = df_pruefungen.sort_values("Datum", ascending=False).reset_index(drop=True)
    
    # For each exam
    for i in range(len(df_pruefungen)):
        pruefung = df_pruefungen.iloc[i]
        fach_eintrag = pruefung["Prüfung"]
        datum_vortag = pruefung["Datum"] - pd.Timedelta(days=1)
        
        # Check if there are multiple subjects on the same day (separated by comma)
        if isinstance(fach_eintrag, str) and "," in fach_eintrag:
            faecher = [f.strip() for f in fach_eintrag.split(",")]
            mehrere_faecher = True
        else:
            faecher = [fach_eintrag]
            mehrere_faecher = False
        
        # Check if the previous day exists in the study plan
        if datum_vortag in df["Datum"].values:
            idx = df.index[df["Datum"] == datum_vortag][0]
            gesamt = df.at[idx, "Lernzeit (h)"]
            
            # Check if Lernfach 1 is already occupied
            lernfach1_belegt = not pd.isna(df.at[idx, "Lernfach 1"]) and df.at[idx, "Lernfach 1"] is not None
            
            if lernfach1_belegt:
                # Lernfach 1 is already occupied, check if it's available in Lernfach 2
                lernfach2_belegt = not pd.isna(df.at[idx, "Lernfach 2"]) and df.at[idx, "Lernfach 2"] is not None
                
                if lernfach2_belegt:
                    # If both Lernfach 1 and 2 are occupied, check Lernfach 3
                    lernfach3_belegt = not pd.isna(df.at[idx, "Lernfach 3"]) and df.at[idx, "Lernfach 3"] is not None
                    
                    if not lernfach3_belegt and gesamt > 0:
                        # Use Lernfach 3 if available
                        df.at[idx, "Lernfach 3"] = faecher[0]
                        df.at[idx, "Dauer 3"] = min(gesamt, 2.0)  # Allocate up to 2 hours
                else:
                    # Use Lernfach 2 if available
                    if mehrere_faecher and len(faecher) >= 2:
                        # With multiple subjects: split study time
                        zeit_pro_fach = min(gesamt / 2, 1.5)  # Max 1.5 hours per subject
                        
                        df.at[idx, "Lernfach 2"] = faecher[0]
                        df.at[idx, "Dauer 2"] = zeit_pro_fach
                        
                        df.at[idx, "Lernfach 3"] = faecher[1] 
                        df.at[idx, "Dauer 3"] = zeit_pro_fach
                    else:
                        # With one subject: use all available time
                        df.at[idx, "Lernfach 2"] = faecher[0]
                        df.at[idx, "Dauer 2"] = min(gesamt, 3.0)  # Allocate up to 3 hours
            else:
                # Lernfach 1 is available
                if mehrere_faecher and len(faecher) >= 2:
                    # With multiple subjects: split study time
                    zeit_pro_fach = min(gesamt / 2, 2.0)  # Max 2 hours per subject
                    
                    df.at[idx, "Lernfach 1"] = faecher[0]
                    df.at[idx, "Dauer 1"] = zeit_pro_fach
                    
                    df.at[idx, "Lernfach 2"] = faecher[1]
                    df.at[idx, "Dauer 2"] = zeit_pro_fach
                else:
                    # With one subject: use all available time
                    df.at[idx, "Lernfach 1"] = faecher[0]
                    df.at[idx, "Dauer 1"] = min(gesamt, 4.0)  # Allocate up to 4 hours
    
    # Update free time after filling the study plan
    for idx in df.index:
        total_scheduled = sum(df.loc[idx, f"Dauer {i}"] for i in range(1, 4) if pd.notna(df.loc[idx, f"Dauer {i}"]))
        df.loc[idx, "freie_zeit"] = max(0, df.loc[idx, "Lernzeit (h)"] - total_scheduled)
    
    return df


def get_total_study_time_by_subject(df):
    """Calculate total study time per subject from the study plan."""
    fach_spalten = ['Lernfach 1', 'Lernfach 2', 'Lernfach 3']
    dauer_spalten = ['Dauer 1', 'Dauer 2', 'Dauer 3']

    frames = []

    # Process regular subjects
    for fach_col, dauer_col in zip(fach_spalten, dauer_spalten):
        temp = df[[fach_col, dauer_col]].copy()
        temp.columns = ['Lernfach', 'Lernzeit (h)']
        temp = temp[temp['Lernfach'].notnull() & (temp['Lernzeit (h)'] > 0)]
        frames.append(temp)

    # Process Daily Review entries
    if "Daily Review" in df.columns and "Dauer 4" in df.columns:
        for idx, row in df.iterrows():
            eintrag = row["Daily Review"]
            dauer_gesamt = row["Dauer 4"]
            
            # Skip if no entry or duration is zero/NaN
            if pd.isna(eintrag) or not eintrag.strip() or pd.isna(dauer_gesamt) or dauer_gesamt <= 0:
                continue
                
            fächer = [fach.strip() for fach in eintrag.split(",") if fach.strip()]
            if not fächer:
                continue
                
            # Calculate duration per subject, avoid division by zero
            dauer_pro_fach = dauer_gesamt / len(fächer) if len(fächer) > 0 else 0
            
            for fach in fächer:
                frames.append(pd.DataFrame({
                    "Lernfach": [fach],
                    "Lernzeit (h)": [dauer_pro_fach]
                }))

    # Combine and group
    if frames:
        combined = pd.concat(frames, ignore_index=True)
        result = combined.groupby('Lernfach')['Lernzeit (h)'].sum().reset_index()
        result.columns = ['Lernfach', 'Geplante Lernzeit']
    else:
        # Return empty DataFrame with correct columns if no data
        result = pd.DataFrame(columns=['Lernfach', 'Geplante Lernzeit'])
        
    return result


def fill_study_plan(df_exam, df_pre, df_bereits_verplante_stunden, 
                   split_threshold=4.0, split_ratio=0.5, 
                   exam_proximity_weight=3.0, fairness_weight=2.5, 
                   min_days_between=2, max_consecutive_days=2,
                   dedicated_days_before_exam=2):
    """
    Fill the study plan based on target hours and already planned hours,
    with even distribution of subjects across days.
    """
    # Create a copy of df_pre to avoid modifying the original
    study_plan = df_pre.copy()
    
    # Convert date strings to datetime objects if they're not already
    if isinstance(study_plan['Datum'].iloc[0], str):
        study_plan['Datum'] = pd.to_datetime(study_plan['Datum'])
    if isinstance(df_exam['Prüfungsdatum'].iloc[0], str):
        df_exam['Prüfungsdatum'] = pd.to_datetime(df_exam['Prüfungsdatum'])
    if isinstance(df_exam['Lernstart'].iloc[0], str):
        df_exam['Lernstart'] = pd.to_datetime(df_exam['Lernstart'])
    
    # Calculate total available study time
    total_available_time = study_plan['Lernzeit (h)'].sum()
    
    # Calculate already planned hours for each subject
    already_planned_dict = {}
    for _, row in df_bereits_verplante_stunden.iterrows():
        already_planned_dict[row['Lernfach']] = row['Geplante Lernzeit']
    
    # Initialize subjects_remaining dictionary with all required information
    subjects_remaining = {}
    total_target_hours = 0
    total_adjusted_target = 0
    
    # Create a mapping of exam dates to subjects for dedicated study days
    exam_to_subject = {}
    
    for _, row in df_exam.iterrows():
        subject = row['Fachname']
        target_hours = row['Zielstunden']
        total_target_hours += target_hours
        exam_date = row['Prüfungsdatum']
        
        # Map exam date to subject
        if exam_date in exam_to_subject:
            # If there's already a subject for this date, append
            exam_to_subject[exam_date] = f"{exam_to_subject[exam_date]}, {subject}"
        else:
            exam_to_subject[exam_date] = subject
        
        # Get already planned hours for this subject
        already_planned = already_planned_dict.get(subject, 0)
        
        # Initialize subject info
        subjects_remaining[subject] = {
            'target_hours': target_hours,
            'already_planned': already_planned,
            'remaining_hours': max(0, target_hours - already_planned),
            'exam_date': exam_date,
            'start_date': row['Lernstart'],
            'difficulty': row.get('Schwierigkeit_Nr', 1),
            'weight': row.get('Gewichtung', 1.0),
            'last_scheduled': None,
            'scheduled_count': 0,
            'total_study_period': (exam_date - row['Lernstart']).days,
            'percentage_complete': already_planned / target_hours if target_hours > 0 else 1.0,
            'scheduled_dates': [],
            'consecutive_days': 0,
            'current_streak': 0
        }
        
        # Add to total remaining hours if there are hours left to plan
        if subjects_remaining[subject]['remaining_hours'] > 0:
            total_adjusted_target += subjects_remaining[subject]['remaining_hours']
    
    # Calculate if we have enough time to fulfill all target hours
    if total_available_time < total_adjusted_target:
        # If we don't have enough time, calculate what percentage of each subject's
        # target we can actually fulfill to ensure fairness
        target_percentage = total_available_time / total_adjusted_target if total_adjusted_target > 0 else 0
        
        # Adjust all subjects' remaining hours based on this percentage
        for subject in subjects_remaining:
            subjects_remaining[subject]['adjusted_remaining'] = subjects_remaining[subject]['remaining_hours'] * target_percentage
    else:
        # If we have enough time, keep all targets as is
        for subject in subjects_remaining:
            subjects_remaining[subject]['adjusted_remaining'] = subjects_remaining[subject]['remaining_hours']
    
    # Sort dates to ensure chronological processing
    study_plan = study_plan.sort_values(by='Datum')
    
    # Initialize tracking structures
    day_subjects = {}
    scheduled_hours = {subject: 0 for subject in subjects_remaining.keys()}
    last_date = None
    daily_schedules = defaultdict(list)
    
    # Helper function to round study hours to nearest 0.25
    def round_to_quarter(hours):
        return round(hours * 4) / 4
    
    # Helper function to update consecutive days tracking
    def update_consecutive_days(current_date):
        # Reset consecutive days for subjects not studied today
        for subject, info in subjects_remaining.items():
            # If subject was studied on previous day but not today
            if info['last_scheduled'] is not None and info['last_scheduled'] != current_date:
                days_gap = (current_date - info['last_scheduled']).days
                if days_gap > 1:  # If there's a gap, reset the streak
                    subjects_remaining[subject]['current_streak'] = 0
        
        # For subjects studied today, update their streaks
        for subject in daily_schedules[current_date]:
            if subjects_remaining[subject]['last_scheduled'] is not None:
                days_gap = (current_date - subjects_remaining[subject]['last_scheduled']).days
                if days_gap == 1:  # If studied on consecutive days
                    subjects_remaining[subject]['current_streak'] += 1
                else:
                    subjects_remaining[subject]['current_streak'] = 1
            else:
                subjects_remaining[subject]['current_streak'] = 1
    
    # First, identify days that should be dedicated to specific subjects due to upcoming exams
    dedicated_study_days = {}
    
    for exam_date, subject in exam_to_subject.items():
        # For each day in the dedicated_days_before_exam range
        for days_before in range(1, dedicated_days_before_exam + 1):
            dedicated_date = exam_date - timedelta(days=days_before)
            # Check if this day exists in our study plan
            matching_days = study_plan[study_plan['Datum'] == dedicated_date]
            if not matching_days.empty:
                dedicated_study_days[dedicated_date] = subject
    
    # Process each day in the study plan
    for idx, day in study_plan.iterrows():
        current_date = day['Datum']
        available_hours = day['Lernzeit (h)']
        
        # Skip days with no study time or already planned exams
        if available_hours <= 0 or pd.notna(day['Prüfung']):
            continue
        
        # Calculate already planned hours for this day
        already_planned_hours = 0
        for i in range(1, 4):
            if pd.notna(day[f'Lernfach {i}']) and day[f'Dauer {i}'] > 0:
                already_planned_hours += day[f'Dauer {i}']
        
        # Skip if no hours remaining
        remaining_hours = available_hours - already_planned_hours
        if remaining_hours <= 0:
            continue
            
        # Find the next available slot (1, 2, or 3)
        next_slot = None
        for i in range(1, 4):
            if pd.isna(day[f'Lernfach {i}']) or day[f'Lernfach {i}'] is None or day[f'Dauer {i}'] == 0:
                next_slot = i
                break
                
        if next_slot is None:
            # All slots are filled
            continue
        
        # If this is a new date, update consecutive days tracking
        if last_date is not None and current_date != last_date:
            update_consecutive_days(last_date)
        
        last_date = current_date
        
        # Initialize day tracking if not exists
        if current_date not in day_subjects:
            day_subjects[current_date] = set()
        
        # Check if this is a dedicated study day
        if current_date in dedicated_study_days:
            dedicated_subject = dedicated_study_days[current_date]
            
            # Handle comma-separated subjects
            dedicated_subjects = [s.strip() for s in dedicated_subject.split(',')]
            
            for ded_subject in dedicated_subjects:
                # Skip if all slots are filled
                if next_slot > 3:
                    break
                    
                # Check if subject is still eligible for study
                if ded_subject in subjects_remaining and (
                    subjects_remaining[ded_subject]['start_date'] <= current_date <= 
                    subjects_remaining[ded_subject]['exam_date'] and 
                    subjects_remaining[ded_subject]['adjusted_remaining'] > 0):
                    
                    # Dedicate available hours to this subject
                    hours_raw = min(remaining_hours, subjects_remaining[ded_subject]['adjusted_remaining'])
                    hours = round_to_quarter(hours_raw)
                    
                    if hours > 0:
                        # Update the study plan
                        study_plan.at[idx, f'Lernfach {next_slot}'] = ded_subject
                        study_plan.at[idx, f'Dauer {next_slot}'] = hours
                        
                        # Update subject tracking
                        day_subjects[current_date].add(ded_subject)
                        daily_schedules[current_date].append(ded_subject)
                        
                        # Update remaining hours and tracking info
                        subjects_remaining[ded_subject]['adjusted_remaining'] -= hours
                        subjects_remaining[ded_subject]['last_scheduled'] = current_date
                        subjects_remaining[ded_subject]['scheduled_count'] += 1
                        subjects_remaining[ded_subject]['scheduled_dates'].append(current_date)
                        scheduled_hours[ded_subject] += hours
                        
                        # Update remaining hours for this day
                        remaining_hours -= hours
                        
                        # Move to next slot
                        next_slot += 1
                        
                        # Exit if no more hours
                        if remaining_hours <= 0:
                            break
            
            # If we used all hours or filled all slots, continue to next day
            if remaining_hours <= 0 or next_slot > 3:
                continue
        
        # Get eligible subjects (start date has passed and exam not yet happened)
        eligible_subjects = {
            subject: info for subject, info in subjects_remaining.items()
            if info['start_date'] <= current_date <= info['exam_date'] and info['adjusted_remaining'] > 0
        }
        
        if not eligible_subjects:
            continue


        # Sort subjects by priority, with stronger emphasis on exam proximity
        def get_priority_score(subject_info, subject_name):
            days_until_exam = max(1, (subject_info['exam_date'] - current_date).days)
            total_period = max(1, subject_info['total_study_period'])
            
            # Calculate progress in the study period (0 to 1 scale)
            progress_ratio = 1 - (days_until_exam / total_period)
            
            # Apply stronger non-linear scaling for exam proximity
            # As exam gets closer, priority increases exponentially
            exam_proximity_factor = (1 + progress_ratio) ** exam_proximity_weight
            
            # Exponential increase as exam approaches (inversely proportional to days until exam)
            urgency = subject_info['weight'] * subject_info['difficulty'] * (1 / max(0.5, days_until_exam))
            
            # Very high priority for subjects with exams coming up soon
            if days_until_exam <= 7:  # Last week before exam
                urgency *= (8 - days_until_exam)  # Boost increases each day closer to exam
            
            # Apply exam proximity boost
            urgency = urgency * exam_proximity_factor
            
            # Factor in scheduling frequency
            frequency_penalty = subject_info['scheduled_count'] * 0.1
            
            # Calculate recency penalty (spaced repetition)
            recency_penalty = 0
            if subject_info['scheduled_dates']:
                # Get days since this subject was last scheduled
                days_since_last = (current_date - max(subject_info['scheduled_dates'])).days
                
                # Strong penalty for subjects studied too recently (to enforce spaced repetition)
                if days_since_last < min_days_between:
                    recency_penalty = 50 - (days_since_last * 15)  # High penalty that decreases as days pass
            
            # Add consecutive days penalty
            consecutive_penalty = 0
            if subject_info['current_streak'] >= max_consecutive_days:
                consecutive_penalty = subject_info['current_streak'] * 20  # Penalty for too many consecutive days
            
            # Calculate current completion percentage
            current_completion = (subject_info['already_planned'] + scheduled_hours[subject_name]) / subject_info['target_hours'] if subject_info['target_hours'] > 0 else 1.0
            
            # Fairness boost: prioritize subjects with lower completion percentages
            fairness_boost = (1 - current_completion) * fairness_weight
            
            # Calculate variety score - favor subjects that haven't been studied much recently
            variety_score = 0
            if len(daily_schedules) > 5:  # If we have at least 5 days of schedule
                # Look at the last 5 scheduled days
                recent_days = sorted(daily_schedules.keys())[-5:]
                subject_count = 0
                for day in recent_days:
                    if subject_name in daily_schedules[day]:
                        subject_count += 1
                
                # If this subject has been scheduled a lot recently, penalize it
                if subject_count > 0:
                    variety_score = -subject_count * 3
            
            return urgency - frequency_penalty - recency_penalty - consecutive_penalty + fairness_boost + variety_score
        
        sorted_subjects = sorted(
            eligible_subjects.items(),
            key=lambda x: get_priority_score(x[1], x[0]),
            reverse=True  # Higher priority first
        )
        
        # Allocate study time
        if available_hours >= split_threshold and len(sorted_subjects) >= 2:
            # Split between two subjects, ensuring they aren't already scheduled for this day
            selected_subjects = []
            
            # First try to select subjects that haven't been studied for several days
            for subject, info in sorted_subjects:
                if subject not in day_subjects[current_date] and len(selected_subjects) < 2:
                    # Add extra check for subjects that haven't been studied recently
                    if (info['last_scheduled'] is None or 
                        (current_date - info['last_scheduled']).days >= min_days_between):
                        selected_subjects.append((subject, info))
            
            # If we couldn't find enough subjects with the spacing constraint, relax it
            if len(selected_subjects) < 2:
                for subject, info in sorted_subjects:
                    if subject not in day_subjects[current_date] and len(selected_subjects) < 2 and (subject, info) not in selected_subjects:
                        selected_subjects.append((subject, info))
            
            # If we still couldn't find 2 unique subjects, fall back to top priority
            if len(selected_subjects) < 2:
                # Make sure we don't add the same subject twice
                if len(selected_subjects) == 1:
                    subject1, _ = selected_subjects[0]
                    for subject, info in sorted_subjects:
                        if subject != subject1 and len(selected_subjects) < 2:
                            selected_subjects.append((subject, info))
                
                # If we still don't have 2 subjects, take top 2 priorities
                if len(selected_subjects) < 2:
                    selected_subjects = sorted_subjects[:2]
            
            # Split the time between subjects
            subject1, info1 = selected_subjects[0]
            subject2, info2 = selected_subjects[1]
            
            # Calculate current completion percentages
            s1_completion = (info1['already_planned'] + scheduled_hours[subject1]) / info1['target_hours'] if info1['target_hours'] > 0 else 1.0
            s2_completion = (info2['already_planned'] + scheduled_hours[subject2]) / info2['target_hours'] if info2['target_hours'] > 0 else 1.0
            
            # Calculate ratio to favor the subject with lower completion percentage
            total_completion = s1_completion + s2_completion
            if total_completion == 0:
                fairness_ratio = 0.5
            else:
                s1_weight = 1 - (s1_completion / total_completion) if total_completion > 0 else 0.5
                fairness_ratio = min(0.8, max(0.2, s1_weight))
            
            # Consider exam proximity for ratio calculation
            days_to_exam1 = max(1, (info1['exam_date'] - current_date).days)
            days_to_exam2 = max(1, (info2['exam_date'] - current_date).days)
            
            # Calculate exam proximity ratio - subject with closer exam gets more time
            total_days = days_to_exam1 + days_to_exam2
            if total_days == 0:
                exam_ratio = 0.5
            else:
                # Stronger bias towards subjects with closer exams
                # The subject with the closer exam gets a higher percentage
                exam_ratio = 1 - (days_to_exam1 / total_days) if total_days > 0 else 0.5
                
                # Apply non-linear scaling to further prioritize subjects with very close exams
                if days_to_exam1 <= 7 or days_to_exam2 <= 7:  # If either exam is within a week
                    if days_to_exam1 < days_to_exam2:
                        exam_ratio = max(0.65, exam_ratio)  # At least 65% to subject1
                    else:
                        exam_ratio = min(0.35, exam_ratio)  # At most 35% to subject1
                
                exam_ratio = min(0.75, max(0.25, exam_ratio))  # Keep within reasonable bounds but allow more extreme values
            
            # Calculate final ratio: 60% weight to exam proximity, 40% to fairness
            # This increases the importance of exam proximity in the calculation
            adjusted_ratio = (fairness_ratio * 0.4) + (exam_ratio * 0.6)
            
            # Calculate hours based on the adjusted ratio and round to nearest 0.25
            hours1_raw = min(available_hours * adjusted_ratio, info1['adjusted_remaining'])
            hours1 = round_to_quarter(hours1_raw)
            
            hours2_raw = min(available_hours * (1 - adjusted_ratio), info2['adjusted_remaining'])
            hours2 = round_to_quarter(hours2_raw)
            
            # Make sure we don't exceed available hours due to rounding
            if hours1 + hours2 > available_hours:
                if hours1 > hours2:
                    hours1 = round_to_quarter(available_hours - hours2)
                else:
                    hours2 = round_to_quarter(available_hours - hours1)
            
            # Update the study plan
            study_plan.at[idx, 'Lernfach 1'] = subject1
            study_plan.at[idx, 'Dauer 1'] = hours1
            study_plan.at[idx, 'Lernfach 2'] = subject2
            study_plan.at[idx, 'Dauer 2'] = hours2
            
            # Update subject tracking
            day_subjects[current_date].add(subject1)
            day_subjects[current_date].add(subject2)
            daily_schedules[current_date].extend([subject1, subject2])
            
            # Update remaining hours and tracking info
            subjects_remaining[subject1]['adjusted_remaining'] -= hours1
            subjects_remaining[subject1]['last_scheduled'] = current_date
            subjects_remaining[subject1]['scheduled_count'] += 1
            subjects_remaining[subject1]['scheduled_dates'].append(current_date)
            scheduled_hours[subject1] += hours1
            
            subjects_remaining[subject2]['adjusted_remaining'] -= hours2
            subjects_remaining[subject2]['last_scheduled'] = current_date
            subjects_remaining[subject2]['scheduled_count'] += 1
            subjects_remaining[subject2]['scheduled_dates'].append(current_date)
            scheduled_hours[subject2] += hours2
            
        else:
            # Choose a subject that hasn't been studied recently
            selected_subject = None
            
            # First try to find a subject that hasn't been studied for min_days_between days
            for subject, info in sorted_subjects:
                if (subject not in day_subjects[current_date] and 
                    (info['last_scheduled'] is None or 
                     (current_date - info['last_scheduled']).days >= min_days_between) and
                    info['current_streak'] < max_consecutive_days):
                    selected_subject = (subject, info)
                    break
            
            # If no suitable subject found, relax the consecutive days constraint
            if selected_subject is None:
                for subject, info in sorted_subjects:
                    if subject not in day_subjects[current_date]:
                        selected_subject = (subject, info)
                        break
            
            # If all eligible subjects are already scheduled today, choose the top priority one
            if selected_subject is None and sorted_subjects:
                selected_subject = sorted_subjects[0]
            elif selected_subject is None:
                continue
                
            subject, info = selected_subject
            hours_raw = min(available_hours, info['adjusted_remaining'])
            hours = round_to_quarter(hours_raw)
            
            # Update the study plan
            study_plan.at[idx, 'Lernfach 1'] = subject
            study_plan.at[idx, 'Dauer 1'] = hours
            
            # Update subject tracking
            day_subjects[current_date].add(subject)
            daily_schedules[current_date].append(subject)
            
            # Update remaining hours and tracking info
            subjects_remaining[subject]['adjusted_remaining'] -= hours
            subjects_remaining[subject]['last_scheduled'] = current_date
            subjects_remaining[subject]['scheduled_count'] += 1
            subjects_remaining[subject]['scheduled_dates'].append(current_date)
            scheduled_hours[subject] += hours
    
    # Do a final update of consecutive days tracking
    if last_date is not None:
        update_consecutive_days(last_date)
    
    # Calculate final stats for reporting
    final_stats = {}
    for subject, info in subjects_remaining.items():
        total_scheduled = scheduled_hours[subject] + info['already_planned']
        
        final_stats[subject] = {
            'target_hours': info['target_hours'],
            'scheduled_hours': total_scheduled,
            'percentage': (total_scheduled / info['target_hours']) * 100 if info['target_hours'] > 0 else 100,
            'shortfall': info['target_hours'] - total_scheduled
        }
    
    # Add completion percentage as metadata
    study_plan.attrs['completion_stats'] = final_stats
    
    # Check fairness of distribution
    percentages = [stats['percentage'] for subject, stats in final_stats.items()]
    fairness_metrics = {
        'min_percentage': min(percentages) if percentages else 0,
        'max_percentage': max(percentages) if percentages else 0,
        'avg_percentage': sum(percentages) / len(percentages) if percentages else 0,
        'std_deviation': np.std(percentages) if percentages else 0
    }
    study_plan.attrs['fairness_metrics'] = fairness_metrics
    
    # Calculate diversity metrics - how well subjects are mixed
    subject_sequences = []
    last_subject = None
    sequence_length = 0
    
    # Go through the study plan chronologically and track subject sequences
    for _, day in study_plan.sort_values(by='Datum').iterrows():
        subjects_today = []
        if pd.notna(day['Lernfach 1']):
            subjects_today.append(day['Lernfach 1'])
        if pd.notna(day['Lernfach 2']):
            subjects_today.append(day['Lernfach 2'])
        if pd.notna(day['Lernfach 3']):
            subjects_today.append(day['Lernfach 3'])
        
        for subject in subjects_today:
            if subject == last_subject:
                sequence_length += 1
            else:
                if last_subject is not None:
                    subject_sequences.append(sequence_length)
                last_subject = subject
                sequence_length = 1
    
    # Add the last sequence
    if last_subject is not None and sequence_length > 0:
        subject_sequences.append(sequence_length)
    
    # Calculate metrics about subject sequences
    if subject_sequences:
        diversity_metrics = {
            'max_consecutive_days': max(subject_sequences),
            'avg_consecutive_days': sum(subject_sequences) / len(subject_sequences),
            'long_sequences_count': sum(1 for seq in subject_sequences if seq > max_consecutive_days)
        }
    else:
        diversity_metrics = {
            'max_consecutive_days': 0,
            'avg_consecutive_days': 0,
            'long_sequences_count': 0
        }
    
    study_plan.attrs['diversity_metrics'] = diversity_metrics
    
    return study_plan

#----------------------------------------------------------------------------------

def generate_complete_study_plan(df_exam, df_plan, settings=None):
    """
    Hauptfunktion zum Generieren eines kompletten Lernplans basierend auf Prüfungsdaten und Zeitplaneinstellungen.
    
    Parameters:
    -----------
    df_exam : pandas DataFrame
        DataFrame mit Prüfungsinformationen. Sollte folgende Spalten enthalten:
        - Fachname: Name des Fachs
        - Prüfungsdatum: Datum der Prüfung
        - Schwierigkeit: Schwierigkeitsgrad ('🟢 Leicht', '🟡 Mittel', '🟠 Anspruchsvoll', '🔴 Schwer')
        - Start: Wann der Lernstart beginnen soll ('Jetzt', '1 Monat', '2 Wochen', etc.)
        - Kategorie: Fachkategorie (optional, "Anki" und "Sprache" werden für tägliche Wiederholungen verwendet)
    
    df_plan : pandas DataFrame
        DataFrame mit Wochenplaninformationen. Sollte folgende Spalten enthalten:
        - Tag: Wochentag ('Montag', 'Dienstag', etc.)
        - Lernzeit (h): Verfügbare Lernzeit in Stunden für diesen Wochentag
    
    settings : dict, optional
        Wörterbuch mit optionalen Einstellungen:
        - split_threshold: Ab wie vielen verfügbaren Stunden pro Tag auf multiple Fächer aufgeteilt wird (default: 4.0)
        - split_ratio: Verhältnis für die Aufteilung der Zeit zwischen den Hauptfächern (default: 0.5)
        - exam_proximity_weight: Gewichtung der Prüfungsnähe bei der Priorisierung (default: 3.0)
        - fairness_weight: Gewichtung der gleichmäßigen Verteilung bei der Priorisierung (default: 2.5)
        - min_days_between: Minimale Tage zwischen Lerneinheiten desselben Fachs (default: 2)
        - max_consecutive_days: Maximale aufeinanderfolgende Tage für dasselbe Fach (default: 2)
        - dedicated_days_before_exam: Anzahl der Tage vor einer Prüfung, die für das Prüfungsfach reserviert werden (default: 2)
        - wiederhol_dauer: Dauer der täglichen Wiederholungen in Stunden (default: 0.5)
    
    Returns:
    --------
    pandas DataFrame
        Vollständiger Lernplan mit täglichen Lernfächern und -zeiten
    dict
        Zusätzliche Statistiken und Metriken zum erstellten Lernplan
    """
    # Standardeinstellungen definieren, falls nicht vorhanden
    if settings is None:
        settings = {
            'split_threshold': 4.0,
            'split_ratio': 0.5,
            'exam_proximity_weight': 3.0,
            'fairness_weight': 2.5,
            'min_days_between': 2,
            'max_consecutive_days': 2,
            'dedicated_days_before_exam': 2,
            'wiederhol_dauer': 0.25
        }
    else:
        # Fehlende Einstellungen mit Standardwerten ergänzen
        default_settings = {
            'split_threshold': 4.0,
            'split_ratio': 0.5,
            'exam_proximity_weight': 3.0,
            'fairness_weight': 2.5,
            'min_days_between': 2,
            'max_consecutive_days': 2,
            'dedicated_days_before_exam': 2,
            'wiederhol_dauer': 0.25
        }
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
    
    # SCHRITT 1: Daten vorbereiten
    # ----------------------------
    # Prüfungsdaten vorbereiten
    df_exam = prepare_exams(df_exam)
    
    # Wochenplan vorbereiten
    df_plan = prepare_plan(df_plan)
    
    # Lernstartdaten berechnen
    df_exam['Lernstart'] = df_exam.apply(berechne_lernstart, axis=1)
    
    # Prüfungsdaten bereinigen
    df_exam = cleanup_exam_data(df_exam)
    
    # SCHRITT 2: Kalender erstellen
    # -----------------------------
    # Gesamte Lernzeit berechnen
    gesamtstunden, gesamttage, df_kalender = berechne_gesamt_lernzeit(df_exam, df_plan)
    
    # Prüfungstage im Kalender markieren
    df_kalender = erweitere_kalender_mit_pruefungstagen(df_kalender, df_exam)
    
    # Zielstunden pro Fach berechnen
    df_exam = berechne_zielstunden(df_exam, df_kalender)
    
    # SCHRITT 3: Lernplan initialisieren
    # ----------------------------------
    # Lernfachspalten im Kalender vorbereiten
    df_lernplan = erstelle_fächer(df_kalender)
    
    # Freie Zeit im Kalender aktualisieren
    df_lernplan = aktualisiere_freie_zeit(df_lernplan)
    
    # SCHRITT 4: Vortage vor Prüfungen planen
    # ---------------------------------------
    # Tage vor Prüfungen mit den Prüfungsfächern füllen
    df_lernplan = fülle_vortage_aller_prüfungen(df_lernplan)
    
    # Freie Zeit nach der Vortagsplanung aktualisieren
    df_lernplan = aktualisiere_freie_zeit(df_lernplan)
    
    # SCHRITT 5: Tägliche Wiederholungen planen (für Anki und Sprachen)
    # -----------------------------------------------------------------
    df_lernplan = plane_daily_reviews(df_lernplan, df_exam, wiederhol_dauer=settings['wiederhol_dauer'])
    
    # Freie Zeit nach den täglichen Wiederholungen aktualisieren
    df_lernplan = aktualisiere_freie_zeit(df_lernplan)
    
    # SCHRITT 6: Aktuelle Lernzeiten pro Fach berechnen
    # -------------------------------------------------
    df_bereits_verplante_stunden = get_total_study_time_by_subject(df_lernplan)
    
    # SCHRITT 7: Restlichen Lernplan füllen
    # -------------------------------------
    # Lernplan mit den verbleibenden Stunden füllen
    df_lernplan_final = fill_study_plan(
        df_exam, 
        df_lernplan, 
        df_bereits_verplante_stunden,
        split_threshold=settings['split_threshold'],
        split_ratio=settings['split_ratio'],
        exam_proximity_weight=settings['exam_proximity_weight'],
        fairness_weight=settings['fairness_weight'],
        min_days_between=settings['min_days_between'],
        max_consecutive_days=settings['max_consecutive_days'],
        dedicated_days_before_exam=settings['dedicated_days_before_exam']
    )
    
    # SCHRITT 8: Statistiken und Metriken sammeln
    # -------------------------------------------
    # Endgültige Verteilung der Lernzeiten berechnen
    final_stats = df_lernplan_final.attrs.get('completion_stats', {})
    fairness_metrics = df_lernplan_final.attrs.get('fairness_metrics', {})
    diversity_metrics = df_lernplan_final.attrs.get('diversity_metrics', {})
    
    # Gesamtstatistiken berechnen
    gesamt_stats = {
        'Gesamte verfügbare Lernzeit (h)': gesamtstunden,
        'Gesamtzahl der Tage im Lernplan': gesamttage,
        'Anzahl der Prüfungsfächer': len(df_exam),
        'Fairness-Metriken': fairness_metrics,
        'Diversitäts-Metriken': diversity_metrics,
        'Fach-Statistiken': final_stats
    }
    
    return df_lernplan_final, gesamt_stats


def create_example_study_plan():
    """
    Erstellt einen Beispiel-Lernplan mit Demo-Daten.
    
    Returns:
    --------
    pandas DataFrame
        Vollständiger Beispiel-Lernplan
    dict
        Zusätzliche Statistiken zum Beispiel-Lernplan
    """
    import pandas as pd
    
    # Beispiel-Prüfungsdaten erstellen
    data_exam = {
        'Fachname': ['Mathematik', 'Informatik', 'Physik', 'Wirtschaftswissenschaften'],
        'Prüfungsdatum': ['2025-06-15', '2025-06-20', '2025-07-05', '2025-07-10'],
        'Schwierigkeit': ['🔴 Schwer', '🟠 Anspruchsvoll', '🟠 Anspruchsvoll', '🟡 Mittel'],
        'Start': ['1 Monat', '3 Wochen', '4 Wochen', '2 Wochen'],
        'Kategorie': ['Standard', 'Anki', 'Standard', 'Standard']
    }
    df_exam = pd.DataFrame(data_exam)
    
    # Beispiel-Wochenplan erstellen
    data_plan = {
        'Tag': ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag'],
        'Lernzeit (h)': [2, 3, 1.5, 2, 1, 5, 4]
    }
    df_plan = pd.DataFrame(data_plan)
    
    # Eigene Einstellungen für das Beispiel
    settings = {
        'split_threshold': 3.0,  # Ab 3 Stunden auf mehrere Fächer aufteilen
        'split_ratio': 0.5,      # 60:40 Aufteilung
        'exam_proximity_weight': 3.5,  # Stärkere Gewichtung der Prüfungsnähe
        'fairness_weight': 2.0,  # Etwas geringere Fairnessgewichtung
        'min_days_between': 1,   # Fächer können an aufeinanderfolgenden Tagen gelernt werden
        'max_consecutive_days': 3,  # Maximal 3 Tage hintereinander dasselbe Fach
        'dedicated_days_before_exam': 3,  # 3 Tage vor der Prüfung für das Fach reservieren
        'wiederhol_dauer': 0.75  # 45 Minuten für tägliche Wiederholungen
    }
    
    # Lernplan generieren
    return generate_complete_study_plan(df_exam, df_plan, settings)


if __name__ == "__main__":
    # Beispiel-Lernplan erstellen und Ergebnisse anzeigen
    lernplan, statistiken = create_example_study_plan()
    
    print("Beispiel-Lernplan erstellt!")
    print(f"Gesamte verfügbare Lernzeit: {statistiken['Gesamte verfügbare Lernzeit (h)']} Stunden")
    print(f"Anzahl der Prüfungsfächer: {statistiken['Anzahl der Prüfungsfächer']}")
    
    # Zeige einen Teil des Lernplans
    print("\nAuszug aus dem Lernplan:")
    print(lernplan[['Datum', 'Wochentag', 'Lernzeit (h)', 'Lernfach 1', 'Dauer 1', 
                   'Lernfach 2', 'Dauer 2', 'Prüfung']].head(10))
    
    # Zeige Statistiken pro Fach
    print("\nStatistiken pro Fach:")
    for fach, stats in statistiken['Fach-Statistiken'].items():
        print(f"{fach}: Ziel {stats['target_hours']}h, geplant {stats['scheduled_hours']}h " +
              f"({stats['percentage']:.1f}%)")