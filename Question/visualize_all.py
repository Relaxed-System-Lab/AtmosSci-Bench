import streamlit as st
# from Questions import Question1, Question2, Question3
from question_collection import question_collection, INSTANCE_SIZE

# streamlit run visualize_all.py

# Main page title
st.title("Question Details")

# Sidebar: Quick Navigation
st.sidebar.title("Quick Navigation")

# Create hyperlink buttons for each question in the sidebar
for idx, question in enumerate(question_collection):
    st.sidebar.markdown(f"[Question {idx + 1}: {question.id} {'(ERROR)' if question.error else ''}](#question_{idx})")

# Total questions
st.write(f"### Total Questions: {len(question_collection)}")
# Total templates
st.write(f"### Total Templates: {len(question_collection) / INSTANCE_SIZE}")

# Number of questions of each type
type_dict = {}
for question in question_collection:
    if question.type in type_dict:
        type_dict[question.type] += 1
    else:
        type_dict[question.type] = 1
st.write("### Number of Questions by Type:")
for key, value in type_dict.items():
    st.write(f"+ {key}: {value / INSTANCE_SIZE}")

# Display all questions on the main page
for idx, question in enumerate(question_collection):
    # Add HTML anchor
    st.markdown(f"<div id='question_{idx}'></div>", unsafe_allow_html=True)

    # Display question details
    st.write(f"### Question {idx + 1}: {question.id}")
    st.write(f"+ Type: {question.type}")
    if question.id.split("_")[1] == "1":
        st.write(f"+ Question Generation: Original")
    else:
        st.write(f"+ Question Generation: {'GPT Generated' if question.gpt else 'Random Generated'}")
    st.write(f"+ Parameters: {question.variables}")
    st.write(f"+ Attempted Generation Count: {question.attempt}")

    # Display `question()` result
    st.write("#### Question:")
    st.markdown(question.question_md(), unsafe_allow_html=True)

    st.write("#### Plain Question:")
    st.markdown(question.question(), unsafe_allow_html=True)

    # Display `answer()` result
    st.write("#### Answer:")
    st.markdown(question.answer())

    # Options
    st.write("#### Options:")
    st.markdown(question.options_md(show_correct_option=True), unsafe_allow_html=True)

    # Options notes
    st.write("#### Options Notes:")
    for note in question.options_types:
        st.markdown(note)

    if question.error:
        st.write("#### Error:")
        st.markdown(question.error)

    # Add separator line
    st.markdown("---")
