# 📚 Study Planner Automation

This project provides a streamlined, semi-automated solution for generating personalized study plans. It is especially useful for students juggling multiple exams and time constraints. The tool takes user inputs like exam dates and availability, and outputs a smart, exportable study schedule.

## 🔍 Project Overview

The goal of this tool is to **automatically create a fair and efficient study plan**, balancing the number of available study hours with exam dates, perceived subject difficulty, and individual preferences (like deep-work days or Anki practice).

### 🎯 Key Features
- Input exam dates and difficulty per subject
- Specify your availability for studying
- Automatically generate a plan using a custom algorithm
- Visualize your plan in:
  - A **calendar view**
  - A **tabular breakdown**
  - An **exportable `.ics` calendar file**
- Built-in logic to fairly allocate remaining study hours

---

## 🗂 Folder Structure

study-planner-automation/ ├── pages/ │ ├── 01_01 Prüfungstermine.py # Input: Exam dates and difficulty │ ├── 02_02 Zeitlicher Rahmen.py # Input: Available days/times for learning │ ├── 03_03 Lernplan.py # Output: Study plan in 3 tabs │ └── 00_Archiv/ # Archived/old modules ├── Homepage.py # Start page of the app ├── my_func.py # 🧠 Core algorithm: creates the actual study plan ├── Image_Workflow.png # Project workflow diagram ├── LICENSE.txt ├── requirements.txt # Python dependencies └── pycache/ # Cached files (auto-generated)


---

## 💡 How It Works

1. **Homepage** – Landing page to start using the planner.
2. **Prüfungstermine** – Users input upcoming exams and relevant metadata (e.g., difficulty, goals).
3. **Zeitlicher Rahmen** – Users enter when they are available to study (daily/weekly time slots).
4. **Lernplan** – Three-tab display of the computed plan:
   - Tab 1: Calendar (week/day overview)
   - Tab 2: Table (detailed list of tasks and durations)
   - Tab 3: Export function (generate an `.ics` calendar file)

The **heart of the system** is the `my_func.py` file, which contains the algorithm that:
- Weighs subjects by urgency and difficulty
- Distributes learning time fairly and efficiently
- Adapts to available time slots and pre-committed events

---

## 🖼 Workflow Overview

See `Image_Workflow.png` for a visual breakdown of the overall process.

---

## ⚙️ Installation

```bash
git clone https://github.com/yourusername/study-planner-automation.git
cd study-planner-automation
pip install -r requirements.txt
