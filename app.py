import streamlit as st
from pdf_parser import parse_pdf
from filters import filter_books
from langchain_helper import generate_lesson_plan
from db import save_search

st.set_page_config(page_title="AI Book Boss", layout="wide")

st.title("📚 AI Book Boss - Test Launch")
st.write("This is a test to check if the environment works.")

# Load the PDF book list (this is just a placeholder for now)
BOOKS = [{"title": "Sample Book", "grade": "5", "subject": "Science", "theme": "Innovation", "description": "A sample description."}]

# Simple form
grade = st.selectbox("Select Grade Level:", ["5"])
subject = st.selectbox("Select Subject:", ["Science"])
theme = st.text_input("Enter Theme (e.g., Innovation)")

if st.button("Generate Book List"):
    st.success(f"Generated book list for Grade {grade} Science Theme: {theme}")
    st.write(BOOKS[0])
    lesson_plan = generate_lesson_plan(BOOKS[0]["title"], grade, subject, theme)
    st.write(f"Lesson Plan: {lesson_plan}")

    save_search(grade, subject, theme)
