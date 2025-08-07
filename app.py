"""
Simple demonstration web application for tracking spiritual, physical and mental
fitness. This prototype uses the Flask web framework and stores user progress
in memory. In a real production system you would persist data to a database
and implement authentication.

To run this app locally install Flask (pip install flask) and then
execute `python app.py`. Visit http://localhost:5000 in your browser to
interact with the demo.
"""

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# A secret key is required to use Flask sessions. In a real deployment this
# should be random and not checked into version control.
app.secret_key = "change-me-in-production"

# Define the survey questions for each category. Each entry contains a
# ``level`` and a list of ``questions``. When the user completes a level the
# next one becomes available. For brevity only a handful of questions are
# included – you can expand these lists to suit your program. Each category
# has three levels to demonstrate progressive disclosure.
SURVEY_QUESTIONS = {
    "spiritual": [
        {"level": 1, "questions": [
            "Did you set aside time for prayer or meditation today?",
            "Did you read a passage from a religious or philosophical text?",
        ]},
        {"level": 2, "questions": [
            "Have you engaged in a community service or outreach activity this week?",
            "Have you participated in a group worship, study or reflection session recently?",
        ]},
        {"level": 3, "questions": [
            "Do you feel your spiritual practice is deepening over time?",
            "Are you mentoring or supporting others in their spiritual journey?",
        ]},
    ],
    "physical": [
        {"level": 1, "questions": [
            "Did you complete at least 30 minutes of physical activity today?",
            "Did you drink at least 8 cups of water today?",
        ]},
        {"level": 2, "questions": [
            "Did you eat a balanced meal with fruits and vegetables today?",
            "Have you consistently slept 7–8 hours per night this week?",
        ]},
        {"level": 3, "questions": [
            "Are you following a regular exercise routine that challenges you?",
            "Have you reached or maintained a healthy weight range?",
        ]},
    ],
    "mental": [
        {"level": 1, "questions": [
            "Did you practice a stress‑relief technique like mindfulness or deep breathing today?",
            "Did you take a break from screens and social media for at least 30 minutes?",
        ]},
        {"level": 2, "questions": [
            "Have you connected with a friend, family member or counselor to talk about how you're feeling?",
            "Did you spend time on a hobby or creative activity that you enjoy?",
        ]},
        {"level": 3, "questions": [
            "Are you regularly journaling or reflecting on your emotions?",
            "Do you feel you can manage stress and challenges in a healthy way?",
        ]},
    ],
}


def get_user_progress() -> dict:
    """
    Retrieve the current user's progress from the session. If no progress
    exists yet a new record is created. Progress is stored as a dict with
    category names as keys. Each value is another dict containing:
        ``level``: the highest completed level (starting at 0)
        ``responses``: a list of answers given
        ``badges``: a list of badge names earned

    Returns
    -------
    dict
        The user progress data.
    """
    if "progress" not in session:
        # Initialize progress for each category. Start at level 0 (no survey
        # completed). Badges list is empty.
        session["progress"] = {
            cat: {"level": 0, "responses": [], "badges": []}
            for cat in SURVEY_QUESTIONS.keys()
        }
    return session["progress"]


@app.route("/")
def index():
    """
    Home page displaying the user's progress in each category and available
    surveys. Shows progress bars and any earned badges. The user can click
    through to the next survey level if available.
    """
    progress = get_user_progress()
    categories_info = []
    for category, data in progress.items():
        total_levels = len(SURVEY_QUESTIONS[category])
        completed_levels = data["level"]
        # Compute percentage progress based on completed levels
        percent_complete = int((completed_levels / total_levels) * 100)
        categories_info.append({
            "name": category.capitalize(),
            "key": category,
            "percent_complete": percent_complete,
            "badges": data["badges"],
            "next_level": completed_levels + 1 if completed_levels < total_levels else None,
        })
    return render_template("index.html", categories_info=categories_info)


@app.route("/survey/<category>", methods=["GET", "POST"])
def survey(category: str):
    """
    Display and handle a survey for a given category. If the user submits
    answers they are stored and progress is updated. Once all levels for a
    category are completed the user receives a badge.

    Parameters
    ----------
    category : str
        The category key (e.g. 'spiritual', 'physical', 'mental').
    """
    category = category.lower()
    if category not in SURVEY_QUESTIONS:
        return redirect(url_for("index"))

    progress = get_user_progress()
    user_cat_data = progress[category]
    current_level = user_cat_data["level"] + 1  # level to present
    total_levels = len(SURVEY_QUESTIONS[category])

    # If all levels completed, redirect back to index
    if current_level > total_levels:
        return redirect(url_for("index"))

    level_data = next((lvl for lvl in SURVEY_QUESTIONS[category] if lvl["level"] == current_level), None)
    if not level_data:
        return redirect(url_for("index"))

    if request.method == "POST":
        # Collect answers from the form
        answers = []
        for idx, q in enumerate(level_data["questions"]):
            answer = request.form.get(f"q{idx}", "")
            answers.append({"question": q, "answer": answer})
        # Append responses
        user_cat_data["responses"].append({"level": current_level, "answers": answers})
        # Update level completed
        user_cat_data["level"] = current_level
        # Award badge if this was the last level
        if current_level == total_levels:
            badge_name = f"{category.capitalize()} Champion"
            user_cat_data["badges"].append(badge_name)
        # Save back to session
        session["progress"] = progress
        return redirect(url_for("index"))

    return render_template("survey.html", category=category, level=current_level, questions=level_data["questions"])


if __name__ == "__main__":
    # Run the app. Debug mode is enabled for convenience.
    app.run(debug=True, host="0.0.0.0")
