# Advanced Health & Fitness Planner

## Overview

The Advanced Health & Fitness Planner is a personalized web application designed to help users achieve their health goals. It provides customized meal and workout plans through interactive chatbot interfaces and tracks user progress with interactive charts. The app leverages Cohere's LLM API to generate and refine plans based on detailed user profiles.

## Utility of the Prototype

- **Personalized Planning:**  
  Generates 7-day meal and workout plans tailored to the user’s personal data, dietary restrictions, fitness preferences, and goals.

- **Conversational Interaction:**  
  Chatbot interfaces allow users to interact naturally with AI to generate and refine both meal and workout plans.

- **Progress Tracking:**  
  Maintains a history of user profiles and visualizes key metrics (e.g., weight, waist, hip, BMI) through interactive charts, helping users monitor their progress over time.

## Main Design Decisions

- **Tabbed Layout:**  
  The app is divided into four tabs:
  - **Profile:** For entering and updating personal data.
  - **Meal Plan:** A chatbot interface for generating and refining meal plans.
  - **Workout Plan:** A chatbot interface for generating and refining workout plans.
  - **Progress:** Interactive charts and summary metrics that track progress over time.

- **State Management:**  
  Uses Streamlit’s session state to persist user data and conversation history across tabs.

- **Conversational Chatbots:**  
  Both the meal and workout planning functionalities are implemented as chatbots, leveraging Cohere's LLM API to provide context-aware responses based on the user's profile and preferences.

- **Interactive Visualizations:**  
  Integrates Plotly Express to deliver responsive, interactive charts in the Progress tab.

- **Custom Styling:**  
  Custom CSS and a sidebar navigation enhance the visual appeal and usability of the app.

## Main Difficulties Encountered

- **LLM Compliance:**  
  Ensuring the LLM strictly adheres to constraints (such as generating exactly the specified number of workout days) required extensive prompt engineering.

- **Maintaining Conversation Context:**  
  Managing and preserving conversation history in a chatbot interface to generate coherent, context-aware responses posed challenges.

- **State Persistence and Rerun Logic:**  
  Handling user data across multiple tabs and triggering real-time updates with Streamlit’s session state and rerun functionality was nontrivial.

- **Integration Complexity:**  
  Combining meal planning, workout planning, and progress tracking in a unified, visually appealing interface required careful design and testing.

## Installation and Usage

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/advanced-health-fitness-planner.git
   cd advanced-health-fitness-planner
  ```

2. **Install Dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
  ```

3. **Configure Your Cohere API Key:**
   Create a file named cohere.key in the project directory and paste your API key into it.

4. **Run the Application:**
   Launch the app using:
   ```bash
   streamlit run app.py
   ```

5. **Usage:**
   - **Profile Tab:** Enter your personal details (including body shape selection via images) and save your profile.
   - **Meal Plan Tab:** Chat with the AI to generate and refine your personalized 7-day meal plan.
   - **Workout Plan Tab:** Enter your workout preferences and interact with the chatbot to obtain a customized 7-day workout plan.
   - **Progress Tab:** View your profile history and interactive progress charts to track your journey over time.
