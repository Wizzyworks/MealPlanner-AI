# MealPlanner-AI : A Multi-Agent ADK System
My Meal Planner – remembers your preferences, learns from feedback, and creates personalised meal plans ranging from ₹400/week to luxury diets for weight loss, muscle gain, diabetes control, and Indian hostel/PG life. Persistent memory, health-aware, fully personalised. No deployment needed – just run &amp; record.

### Description
- Remembers your taste, allergies, budget, and fitness goals forever
- Creates realistic 7-day Indian meal plans (mess-style to home-cooked)
- Learns from your feedback and gets better every week
- Handles ₹400/week hostel life to diabetes-friendly or muscle-gain diets

### Motivation
Built from real hostel mess pain – no more random dal-chawal, no more budget overshoot, no more "bhai aaj biryani kar le" drama.
One message → perfect desi thali ready, every week.

Simple. Personal. Truly Indian.

### Features
- Multi-agent workflow (Input → Validator → Planner → Budget → Feedback)
- Persistent memory across sessions
- Personalized for Indian mess/hostel/PG life
- Health goals + allergies + budget aware

### How to Run
Setup Python Environment (using pyenv):
Install pyenv if not already. Then create and activate a virtual environment with Python 3.10:
```bash
pyenv install 3.10.0
pyenv virtualenv 3.10.0 meal-planner-env
pyenv activate meal-planner-env
```
Create .env File:
Generate your Gemini API key from Google AI Studio. Create a .env file in the root directory and add:
```bash
GEMINI_API_KEY=your_generated_key_here
```
Install Dependencies & Run the Agent:
```bash
pip install -r requirements.txt

# Terminal 1
uvicorn app:app --reload

# Terminal 2
streamlit run streamlit_app.py
