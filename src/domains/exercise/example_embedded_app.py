"""
Example: Embedding Exercise Tracker in a Larger Application

This file demonstrates how to embed the Exercise Tracker app
into a larger Streamlit application with multiple sections.
"""

import streamlit as st
from src.exercise_app import render_exercise_app

# Page configuration
st.set_page_config(
    page_title="My Fitness Dashboard",
    page_icon="🏋️",
    layout="wide"
)

# Main app header
st.title("🏋️ My Complete Fitness Dashboard")
st.write("Track your workouts, nutrition, and progress all in one place")

st.write("---")

# Create main sections using tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "💪 Exercise Tracker",
    "🥗 Nutrition",
    "📈 Progress Reports"
])

# Dashboard tab
with tab1:
    st.header("📊 Dashboard Overview")
    st.write("Welcome to your fitness dashboard!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Workouts This Week",
            value="4",
            delta="1"
        )

    with col2:
        st.metric(
            label="Calories Burned",
            value="2,450",
            delta="320"
        )

    with col3:
        st.metric(
            label="Total Volume (lbs)",
            value="42,300",
            delta="3,200"
        )

    st.write("---")
    st.subheader("Recent Activity")
    st.write("- Completed 'Push Day A' on 2025-11-14")
    st.write("- Completed 'Leg Day' on 2025-11-12")
    st.write("- Completed 'Pull Day B' on 2025-11-10")
    st.write("- Completed 'Push Day B' on 2025-11-08")

# Exercise Tracker tab - THIS IS THE EMBEDDED APP
with tab2:
    # Simply call the render function - that's it!
    render_exercise_app()

# Nutrition tab (placeholder)
with tab3:
    st.header("🥗 Nutrition Tracking")
    st.write("Track your meals and macros here")

    st.subheader("Today's Meals")
    st.write("**Breakfast**: Oatmeal with berries (350 cal)")
    st.write("**Lunch**: Chicken salad (450 cal)")
    st.write("**Dinner**: Salmon with vegetables (500 cal)")

    st.write("---")
    st.subheader("Macro Targets")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Protein", "150g", "25g remaining")
    with col2:
        st.metric("Carbs", "200g", "50g remaining")
    with col3:
        st.metric("Fat", "60g", "10g remaining")

# Progress Reports tab (placeholder)
with tab4:
    st.header("📈 Progress Reports")
    st.write("View your long-term progress and trends")

    st.subheader("Strength Progress")
    st.write("Charts and graphs would go here showing:")
    st.write("- 1RM progression over time")
    st.write("- Volume progression by muscle group")
    st.write("- Workout frequency trends")
    st.write("- Personal records timeline")

    st.write("---")
    st.subheader("Body Composition")
    st.write("Track your body measurements and composition:")
    st.write("- Weight trends")
    st.write("- Body fat percentage")
    st.write("- Muscle mass estimates")
    st.write("- Progress photos")

# Footer
st.write("---")
st.caption("💡 This is an example of embedding the Exercise Tracker into a larger application")
