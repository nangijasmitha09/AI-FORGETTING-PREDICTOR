from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from dotenv import load_dotenv
import os

from database import (
    init_database,
    create_user,
    get_user_by_email,
    add_topic,
    get_topics,
    get_statistics
)

from predictor import calculate_forgetting_risk
from ai_service import ask_ai


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "development-secret-key"
)

init_database()


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "user_id" in session:
        return redirect("/dashboard")

    return redirect("/login")


# ---------------- SIGN UP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:

            return render_template(
                "signup.html",
                error="Please complete all fields."
            )

        if password != confirm_password:

            return render_template(
                "signup.html",
                error="Passwords do not match."
            )

        if len(password) < 6:

            return render_template(
                "signup.html",
                error="Password must contain at least 6 characters."
            )

        hashed_password = generate_password_hash(password)

        user_id = create_user(
            name,
            email,
            hashed_password
        )

        if user_id is None:

            return render_template(
                "signup.html",
                error="An account with this email already exists."
            )

        session["user_id"] = user_id
        session["user_name"] = name

        return redirect("/dashboard")

    return render_template("signup.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = get_user_by_email(email)

        if user is None:

            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        if not check_password_hash(
            user["password"],
            password
        ):

            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect("/dashboard")

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )


# ---------------- TOPICS API ----------------

@app.route("/api/topics", methods=["GET"])
def api_topics():

    if "user_id" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    topics = get_topics(
        session["user_id"]
    )

    return jsonify([
        dict(topic)
        for topic in topics
    ])


# ---------------- ADD TOPIC API ----------------

@app.route("/api/topics", methods=["POST"])
def create_topic():

    if "user_id" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json()

    try:

        topic = data["topic"]
        subject = data["subject"]

        difficulty = int(
            data["difficulty"]
        )

        quiz_score = int(
            data["quiz_score"]
        )

        days_since_study = int(
            data["days_since_study"]
        )

        revisions = int(
            data["revisions"]
        )

    except (KeyError, TypeError, ValueError):

        return jsonify({
            "error": "Invalid input."
        }), 400

    risk, risk_level = calculate_forgetting_risk(
        difficulty,
        quiz_score,
        days_since_study,
        revisions
    )

    add_topic(
        session["user_id"],
        topic,
        subject,
        difficulty,
        quiz_score,
        days_since_study,
        revisions,
        risk,
        risk_level
    )

    return jsonify({
        "success": True,
        "risk": risk,
        "risk_level": risk_level
    })


# ---------------- STATISTICS API ----------------

@app.route("/api/statistics")
def statistics():

    if "user_id" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    return jsonify(
        get_statistics(
            session["user_id"]
        )
    )


# ---------------- AI STUDY PLAN ----------------

@app.route("/api/ai-plan", methods=["POST"])
def ai_plan():

    if "user_id" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    data = request.get_json()

    topic = data.get(
        "topic",
        "general learning"
    )

    risk = data.get(
        "risk",
        50
    )

    prompt = f"""
Create a personalized revision plan.

Topic: {topic}
Forgetting risk: {risk}%

Give:
1. What to revise
2. How long to revise
3. Active recall activity
4. Short quiz idea
5. Recommended next revision time

Keep it practical and student-friendly.
"""

    answer = ask_ai(prompt)

    return jsonify({
        "plan": answer
    })


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )