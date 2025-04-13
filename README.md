# 📚 Study Planner Automation

This project provides a streamlined, semi-automated solution for generating personalized study plans. It is especially useful for students juggling multiple exams and time constraints. The tool takes user inputs like exam dates, subject difficulty, and personal availability, then outputs a smart, exportable study schedule.

---

## 🔍 Overview

The primary goal of this tool is to **automatically create a fair and efficient study plan**. It tackles the challenge of balancing limited study hours against multiple exam dates, varying subject difficulty, and individual preferences (such as designating deep-work days or incorporating spaced repetition practice like Anki). By automating the planning process, it aims to reduce overwhelm and improve learning outcomes.

---

## 🎯 Key Features

-   **Input Exam Details:** Enter exam dates and assign a perceived difficulty level per subject.
-   **Specify Availability:** Define your available study times on a daily or weekly basis.
-   **Automated Plan Generation:** A custom algorithm calculates and distributes study sessions.
-   **Multiple Views:** Visualize your generated plan in various formats:
    -   📅 **Calendar View:** Get a weekly or daily overview of scheduled sessions.
    -   📊 **Tabular Breakdown:** See a detailed list of subjects, tasks, and allocated durations.
    -   📤 **Exportable Calendar:** Generate an `.ics` file compatible with Google Calendar, Outlook, Apple Calendar, etc.
-   **Smart Allocation:** Built-in logic ensures remaining study hours are distributed fairly based on urgency and difficulty.

---

## ✨ Workflow & How It Works

The application guides the user through a simple process:

1.  **Homepage (`Homepage.py`):** The landing page introduces the tool and provides navigation.
2.  **Exam Input (`pages/01_01 Prüfungstermine.py`):** Users input their upcoming exams, specifying dates and difficulty.
3.  **Time Input (`pages/02_02 Zeitlicher Rahmen.py`):** Users define their available time slots for studying.
4.  **View Plan (`pages/03_03 Lernplan.py`):** The generated study plan is displayed across three tabs:
    *   Tab 1: Interactive Calendar view.
    *   Tab 2: Detailed Table view.
    *   Tab 3: Export function to generate the `.ics` file.

The **core logic** resides in `my_func.py`. This script contains the algorithm responsible for:
-   Weighting subjects based on proximity to the exam date and user-defined difficulty.
-   Distributing study time efficiently across available slots.
-   Adapting the plan based on the total available time versus the estimated required time.

For a visual representation of the data flow, please see the `Image_Workflow.png` file included in the repository.

---

## 💻 Technologies Used

-   **Python:** Core programming language.
-   **Streamlit:** Framework for building the interactive web application UI.
-   **(Likely) Pandas:** For data manipulation and structuring the study plan data.
-   **(Likely) iCalendar (`icalendar` library):** For generating the `.ics` export file.
-   *(Add any other significant libraries used)*

---

## 🗂 Folder Structure
Use code with caution.
Markdown
study-planner-automation/
├── pages/ # Streamlit convention for multi-page app pages
│ ├── 01_01 Prüfungstermine.py # Input: Exam dates and difficulty
│ ├── 02_02 Zeitlicher Rahmen.py # Input: Available days/times for learning
│ ├── 03_03 Lernplan.py # Output: Study plan in 3 tabs
│ └── 00_Archiv/ # Archived/old modules (optional)
├── Homepage.py # Main start page of the Streamlit app
├── my_func.py # 🧠 Core algorithm: creates the actual study plan
├── Image_Workflow.png # Project workflow diagram
├── LICENSE.txt # Project License file
├── requirements.txt # Python dependencies
└── pycache/ # Cached files (auto-generated, often ignored by git)

---

## ⚙️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NiklasBrinkmann102/study-planner-automation.git
    cd study-planner-automation
    ```

2.  **Set up a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ Usage

Once the installation is complete, run the Streamlit application from the project's root directory:

```bash
streamlit run Homepage.py
