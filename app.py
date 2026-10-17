import os
import sqlite3

import streamlit as st


DB_PATH = os.path.join(os.path.dirname(__file__), "tcc_database.db")

ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725,
}


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                activity_level TEXT,
                bmr REAL,
                tdee REAL
            )
            """
        )
        conn.commit()


def calculate_bmr(weight, height, age):
    return 10 * weight + 6.25 * height - 5 * age + 5


def calculate_tdee(bmr, activity_level):
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return bmr * multiplier


def calculate_goals(tdee):
    return {
        "Fat Loss": round(tdee - 300, 2),
        "Maintenance": round(tdee, 2),
        "Muscle Gain": round(tdee + 350, 2),
    }


def save_profile(name, age, height, weight, activity_level, bmr, tdee):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO user_profiles (name, age, height, weight, activity_level, bmr, tdee)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, age, height, weight, activity_level, bmr, tdee),
        )
        conn.commit()


def load_recent_profiles(limit=5):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT name, age, height, weight, activity_level, bmr, tdee FROM user_profiles ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return rows


def main():
    init_db()

    st.title("Thomas Paul Calorie Counter")
    st.caption("A beginner-friendly calorie calculator built with Python and Streamlit")

    with st.form("calorie_form"):
        name = st.text_input("Your name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
        activity_level = st.selectbox(
            "Activity Level",
            list(ACTIVITY_MULTIPLIERS.keys()),
        )

        submitted = st.form_submit_button("Calculate")

    if submitted:
        bmr = calculate_bmr(weight, height, age)
        tdee = calculate_tdee(bmr, activity_level)
        goals = calculate_goals(tdee)

        save_profile(name, age, height, weight, activity_level, bmr, tdee)

        st.success(f"Welcome, {name or 'friend'}! Your results are ready.")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("BMR", f"{bmr:.2f} kcal/day")
        with col2:
            st.metric("TDEE", f"{tdee:.2f} kcal/day")

        st.subheader("Recommended calorie targets")
        for goal_name, goal_value in goals.items():
            st.write(f"- {goal_name}: {goal_value} kcal/day")

    st.subheader("Recent saved profiles")
    recent = load_recent_profiles()
    if recent:
        for profile in recent:
            st.write(
                f"{profile['name']} | Age: {profile['age']} | "
                f"Height: {profile['height']} cm | Weight: {profile['weight']} kg | "
                f"Activity: {profile['activity_level']} | BMR: {profile['bmr']:.2f} | "
                f"TDEE: {profile['tdee']:.2f}"
            )
    else:
        st.info("No saved profiles yet. Fill in the form to create your first one.")


if __name__ == "__main__":
    main()
