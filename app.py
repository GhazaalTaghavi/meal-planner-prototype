import cohere
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# ----------------------------------------------------------------
# Set Page Configuration 
# ----------------------------------------------------------------
st.set_page_config(page_title="Advanced Health & Fitness Planner", page_icon="🏋️", layout="wide")

st.markdown(
    """
    <style>
    body {
        background-color: #f2f2f2;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-size: 16px;
    }
    .css-18e3th9 {
        padding: 0 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Health & Fitness Planner")
st.sidebar.info(
    "Welcome! This app provides personalized meal and workout plans and tracks your progress over time.\n\n"
    "Use the tabs to navigate:\n- **Profile:** Update your personal data\n- **Meal Plan:** Chat with AI about your meal plan\n"
    "- **Workout Plan:** Chat with AI about your workout plan\n- **Progress:** View interactive progress charts"
)

# ----------------------------------------------------------------
# 1. Load Cohere API Key and Initialize Client
# ----------------------------------------------------------------
with open("cohere.key") as f:
    COHERE_API_KEY = f.read().strip()
co = cohere.Client(COHERE_API_KEY)

# ----------------------------------------------------------------
# 2. LLM Utility Functions
# ----------------------------------------------------------------

def generate_weekly_meal_plan(user_profile):
    """
    Generates an initial 7-day meal plan based on user profile.
    """
    prompt = f"""
    You are a nutrition expert. Generate a 7-day meal plan for the following user profile:
    
    - Gender: {user_profile['gender']}
    - Body Shape: {user_profile['body_shape']}
    - Height (cm): {user_profile['height']}
    - Current Weight (kg): {user_profile['current_weight']}
    - Goal Weight (kg): {user_profile['goal_weight']}
    - Waist Circumference (cm): {user_profile['waist_circumference']}
    - Hip Circumference (cm): {user_profile['hip_circumference']}
    - Dietary Restrictions: {user_profile['dietary_restrictions']}
    - Nutritional Goal: {user_profile['nutritional_goal']}
    - Ingredient Preferences: {user_profile['ingredient_preferences']}
    - Allergies: {user_profile['allergies']}
    
    The meal plan should have 3 meals + 2 snacks per day (Breakfast, Snack, Lunch, Snack, Dinner).
    Return the plan in a JSON-like structure with a 'Total Daily Calories' estimate for each day.
    """
    response = co.generate(
        model="command-xlarge",
        prompt=prompt,
        max_tokens=2000,
        temperature=0.7
    )
    return response.generations[0].text.strip()

def chat_meal_plan(conversation):
    """
    Uses the conversation history (including the profile info) to generate the next AI reply.
    """
    profile = st.session_state.get("user_profile", {})
    prompt = "You are a nutrition expert and conversational AI. Use the following user profile to inform your responses:\n"
    if profile:
        prompt += (
            f"- Gender: {profile.get('gender', '')}\n"
            f"- Body Shape: {profile.get('body_shape', '')}\n"
            f"- Height (cm): {profile.get('height', '')}\n"
            f"- Current Weight (kg): {profile.get('current_weight', '')}\n"
            f"- Goal Weight (kg): {profile.get('goal_weight', '')}\n"
            f"- Waist Circumference (cm): {profile.get('waist_circumference', '')}\n"
            f"- Hip Circumference (cm): {profile.get('hip_circumference', '')}\n"
            f"- Dietary Restrictions: {profile.get('dietary_restrictions', '')}\n"
            f"- Nutritional Goal: {profile.get('nutritional_goal', '')}\n"
            f"- Ingredient Preferences: {profile.get('ingredient_preferences', '')}\n"
            f"- Allergies: {profile.get('allergies', '')}\n\n"
        )
    prompt += "The following is a conversation between a user and you about generating a meal plan.\n"
    for msg in conversation:
        if msg["role"] == "user":
            prompt += "User: " + msg["message"] + "\n"
        else:
            prompt += "AI: " + msg["message"] + "\n"
    prompt += "AI:"
    response = co.generate(
        model="command-xlarge",
        prompt=prompt,
        max_tokens=2000,
        temperature=0.7
    )
    return response.generations[0].text.strip()

def generate_workout_plan(user_profile, workout_prefs):
    prompt = f"""
    You are a personal fitness coach. Based on the following user profile and workout preferences,
    generate a 7-day workout plan. **Do not exceed {workout_prefs['days_per_week']} workout days.**
    For the remaining {7 - workout_prefs['days_per_week']} days, label them as "Rest Day" or
    "Active Recovery" days.

    User Profile:
    - Gender: {user_profile['gender']}
    - Body Shape: {user_profile['body_shape']}
    - Height (cm): {user_profile['height']}
    - Current Weight (kg): {user_profile['current_weight']}
    - Goal Weight (kg): {user_profile['goal_weight']}

    Workout Preferences:
    - Days per week: {workout_prefs['days_per_week']}
    - Workout Style: {workout_prefs['workout_style']}
    - Equipment Available: {workout_prefs['equipment']}
    - Workout Location: {workout_prefs['location']}
    - Session Duration (minutes): {workout_prefs['session_duration']}
    - Other Notes: {workout_prefs['other_workout_notes']}

    Return the plan in a structured format, for example:

    Day 1:
      - Warm-up:
      - Main Workout:
      - Cool-down:
    Day 2:
      ...
    ...
    Day 7:
      ...

    **Important**: You must provide exactly {workout_prefs['days_per_week']} workout days. The remaining days must be labeled as rest or active recovery.
    """
    response = co.generate(
        model="command-xlarge",
        prompt=prompt,
        max_tokens=2000,
        temperature=0.7
    )
    return response.generations[0].text.strip()

def chat_workout_plan(conversation):
    """
    Uses the conversation history (including user profile + workout prefs) to generate the next AI reply.
    """
    profile = st.session_state.get("user_profile", {})
    workout_prefs = st.session_state.get("workout_prefs", {})
    prompt = "You are a personal fitness coach and a conversational AI. Use the following user profile and workout preferences:\n"
    if profile:
        prompt += (
            f"- Gender: {profile.get('gender', '')}\n"
            f"- Body Shape: {profile.get('body_shape', '')}\n"
            f"- Height (cm): {profile.get('height', '')}\n"
            f"- Current Weight (kg): {profile.get('current_weight', '')}\n"
            f"- Goal Weight (kg): {profile.get('goal_weight', '')}\n"
        )
    if workout_prefs:
        prompt += (
            f"- Days per week: {workout_prefs.get('days_per_week', '')}\n"
            f"- Workout Style: {workout_prefs.get('workout_style', '')}\n"
            f"- Equipment: {workout_prefs.get('equipment', '')}\n"
            f"- Location: {workout_prefs.get('location', '')}\n"
            f"- Session Duration: {workout_prefs.get('session_duration', '')} min\n"
            f"- Other Notes: {workout_prefs.get('other_workout_notes', '')}\n\n"
        )
    prompt += "The following is a conversation between a user and you about generating or refining a workout plan.\n"
    for msg in conversation:
        if msg["role"] == "user":
            prompt += "User: " + msg["message"] + "\n"
        else:
            prompt += "AI: " + msg["message"] + "\n"
    prompt += "AI:"
    response = co.generate(
        model="command-xlarge",
        prompt=prompt,
        max_tokens=2000,
        temperature=0.7
    )
    return response.generations[0].text.strip()

# ----------------------------------------------------------------
# 3. Streamlit App with Four Tabs: "Profile", "Meal Plan", "Workout Plan", and "Progress"
# ----------------------------------------------------------------
def main():
    st.title("Advanced Health & Fitness Planner")

    # Create four tabs: Profile, Meal Plan, Workout Plan, and Progress
    tab_profile, tab_mealplan, tab_workout, tab_progress = st.tabs(
        ["Profile", "Meal Plan", "Workout Plan", "Progress"]
    )

    # -------------------------
    # Tab 1: User Profile
    # -------------------------
    with tab_profile:
        st.subheader("Select Your Body Shape")
        cols = st.columns(5)
        with cols[0]:
            st.image("image/apple.png", use_container_width=True)
            if st.button("Select Apple", key="select_apple"):
                st.session_state["body_shape"] = "Apple"
        with cols[1]:
            st.image("image/pear.png", use_container_width=True)
            if st.button("Select Pear", key="select_pear"):
                st.session_state["body_shape"] = "Pear"
        with cols[2]:
            st.image("image/hourglass.png", use_container_width=True)
            if st.button("Select Hourglass", key="select_hourglass"):
                st.session_state["body_shape"] = "Hourglass"
        with cols[3]:
            st.image("image/rectangle.png", use_container_width=True)
            if st.button("Select Rectangle", key="select_rectangle"):
                st.session_state["body_shape"] = "Rectangle"
        with cols[4]:
            st.image("image/inverted-triangle.png", use_container_width=True)
            if st.button("Select Inverted Triangle", key="select_inverted"):
                st.session_state["body_shape"] = "Inverted Triangle"

        st.header("User Profile")
        st.write("Fill out or edit your personal details below, then click 'Save Profile'.")
        with st.form("user_profile_form"):
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="gender")
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170, key="height")
            current_weight = st.number_input("Current Weight (kg)", min_value=30, max_value=200, value=70, key="current_weight")
            goal_weight = st.number_input("Goal Weight (kg)", min_value=30, max_value=200, value=65, key="goal_weight")
            waist_circumference = st.number_input("Waist Circumference (cm)", min_value=40, max_value=200, value=70, key="waist_circumference")
            hip_circumference = st.number_input("Hip Circumference (cm)", min_value=40, max_value=200, value=90, key="hip_circumference")
            dietary_restrictions = st.text_input("Dietary Restrictions (e.g., vegan, vegetarian, gluten-free)", key="dietary_restrictions")
            nutritional_goal = st.selectbox("Nutritional Goal", ["Weight Loss", "Muscle Gain", "Maintenance", "Other"], key="nutritional_goal")
            ingredient_preferences = st.text_input("Ingredient Preferences (e.g., likes/dislikes)", key="ingredient_preferences")
            allergies = st.text_input("Allergies (if any)", key="allergies")
            submitted_profile = st.form_submit_button("Save Profile")

        if submitted_profile:
            profile_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gender": gender,
                "body_shape": st.session_state.get("body_shape", "Not Selected"),
                "height": height,
                "current_weight": current_weight,
                "goal_weight": goal_weight,
                "waist_circumference": waist_circumference,
                "hip_circumference": hip_circumference,
                "dietary_restrictions": dietary_restrictions,
                "nutritional_goal": nutritional_goal,
                "ingredient_preferences": ingredient_preferences,
                "allergies": allergies,
            }
            st.session_state["user_profile"] = profile_data
            st.success("Profile saved successfully!")
            if "profile_history" not in st.session_state:
                st.session_state["profile_history"] = []
            st.session_state["profile_history"].append(profile_data)

    # -------------------------
    # Tab 2: Meal Plan Chatbot
    # -------------------------
    with tab_mealplan:
        st.header("Meal Plan Chatbot")
        if "user_profile" not in st.session_state:
            st.warning("Please fill in and save your profile first in the 'Profile' tab.")
        else:
            # Initialize conversation if not already done
            if "meal_chat" not in st.session_state:
                st.session_state["meal_chat"] = []
                # Generate an initial response using the full meal plan prompt
                initial_response = generate_weekly_meal_plan(st.session_state["user_profile"])
                st.session_state["meal_chat"].append({"role": "assistant", "message": initial_response})
            
            st.markdown("### Conversation")
            # Display conversation history
            for msg in st.session_state["meal_chat"]:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['message']}")
                else:
                    st.markdown(f"**AI:** {msg['message']}")
            
            # User input for chat
            user_input = st.text_input("Type your message here:", key="meal_input")
            if st.button("Send", key="meal_send") and user_input:
                # Append user message
                st.session_state["meal_chat"].append({"role": "user", "message": user_input})
                # Generate AI response
                ai_response = chat_meal_plan(st.session_state["meal_chat"])
                st.session_state["meal_chat"].append({"role": "assistant", "message": ai_response})
                st.rerun()

    # -------------------------
    # Tab 3: Workout Plan Chatbot
    # -------------------------
    with tab_workout:
        st.header("Workout Plan Chatbot")
        # Step 1: Gather user workout prefs
        if "user_profile" not in st.session_state:
            st.warning("Please fill in and save your profile first in the 'Profile' tab.")
        else:
            st.write("Provide your workout preferences below. Once saved, an initial plan will be generated and you can chat about it.")
            if "workout_prefs" not in st.session_state:
                # Form to gather workout preferences
                with st.form("workout_prefs_form"):
                    days_per_week = st.slider("How many days per week do you want to work out?", 1, 7, 4)
                    workout_style = st.selectbox("Workout Style", ["Strength", "Cardio", "Yoga", "Mixed", "Other"])
                    equipment = st.text_input("Equipment Available (e.g., dumbbells, resistance bands, treadmill)")
                    location = st.selectbox("Workout Location", ["Home", "Gym", "Outdoor", "Mixed"])
                    session_duration = st.number_input("Preferred Session Duration (minutes)", min_value=10, max_value=180, value=45)
                    other_workout_notes = st.text_area("Other Workout Notes (injuries, special requests, etc.)")
                    submitted_workout_prefs = st.form_submit_button("Save Workout Preferences")
                
                if submitted_workout_prefs:
                    st.session_state["workout_prefs"] = {
                        "days_per_week": days_per_week,
                        "workout_style": workout_style,
                        "equipment": equipment,
                        "location": location,
                        "session_duration": session_duration,
                        "other_workout_notes": other_workout_notes
                    }
                    st.success("Workout preferences saved successfully!")
                    st.rerun()
            else:
                # Step 2: Initialize workout chatbot if not already done
                if "workout_chat" not in st.session_state:
                    st.session_state["workout_chat"] = []
                    # Generate an initial plan using the user profile + workout prefs
                    initial_workout = generate_workout_plan(st.session_state["user_profile"], st.session_state["workout_prefs"])
                    st.session_state["workout_chat"].append({"role": "assistant", "message": initial_workout})
                
                st.markdown("### Conversation")
                # Display conversation history
                for msg in st.session_state["workout_chat"]:
                    if msg["role"] == "user":
                        st.markdown(f"**You:** {msg['message']}")
                    else:
                        st.markdown(f"**AI:** {msg['message']}")

                # Step 3: Chat interface
                user_input = st.text_input("Type your message here:", key="workout_input")
                if st.button("Send", key="workout_send") and user_input:
                    # Append user message
                    st.session_state["workout_chat"].append({"role": "user", "message": user_input})
                    # Generate AI response
                    ai_response = chat_workout_plan(st.session_state["workout_chat"])
                    st.session_state["workout_chat"].append({"role": "assistant", "message": ai_response})
                    st.rerun()

    # -------------------------
    # Tab 4: Progress
    # -------------------------
    with tab_progress:
        st.header("Progress Tracker")
        if "profile_history" not in st.session_state or len(st.session_state["profile_history"]) == 0:
            st.info("No profile history available. Please update your profile in the 'Profile' tab.")
        else:
            st.subheader("Profile History")
            history_df = pd.DataFrame(st.session_state["profile_history"])
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_df = history_df.sort_values(by='timestamp')
            st.dataframe(history_df)

            history_df['BMI'] = history_df.apply(lambda row: row['current_weight'] / ((row['height']/100)**2), axis=1)
            
            st.subheader("Interactive Progress Charts")
            fig_weight = px.line(history_df, x="timestamp", y="current_weight", title="Weight Progress (kg)")
            st.plotly_chart(fig_weight, use_container_width=True)

            fig_waist = px.line(history_df, x="timestamp", y="waist_circumference", title="Waist Circumference Progress (cm)")
            st.plotly_chart(fig_waist, use_container_width=True)

            fig_hip = px.line(history_df, x="timestamp", y="hip_circumference", title="Hip Circumference Progress (cm)")
            st.plotly_chart(fig_hip, use_container_width=True)

            fig_bmi = px.line(history_df, x="timestamp", y="BMI", title="BMI Progress")
            st.plotly_chart(fig_bmi, use_container_width=True)

            st.subheader("Summary Metrics")
            initial = history_df.iloc[0]
            latest = history_df.iloc[-1]
            weight_change = latest['current_weight'] - initial['current_weight']
            waist_change = latest['waist_circumference'] - initial['waist_circumference']
            hip_change = latest['hip_circumference'] - initial['hip_circumference']
            initial_bmi = initial['current_weight'] / ((initial['height']/100)**2)
            latest_bmi = latest['BMI']
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Current Weight (kg)", f"{latest['current_weight']} kg", delta=f"{weight_change:+.1f} kg", delta_color="inverse")
            col2.metric("Waist (cm)", f"{latest['waist_circumference']} cm", delta=f"{waist_change:+.1f} cm", delta_color="inverse")
            col3.metric("Hip (cm)", f"{latest['hip_circumference']} cm", delta=f"{hip_change:+.1f} cm", delta_color="inverse")
            col4.metric("BMI", f"{latest_bmi:.1f}", delta=f"{(latest_bmi - initial_bmi):+.1f}", delta_color="inverse")

if __name__ == "__main__":
    main()
