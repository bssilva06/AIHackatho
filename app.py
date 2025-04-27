import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import io
from parse_book_entries import parse_book_entries
from langchain_helper import load_book_retriever, query_books
from filters import grade_in_page

st.set_page_config(page_title="AI Book Boss", layout="wide")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if "user_submissions" not in st.session_state:
    st.session_state.user_submissions = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "generated_book_list" not in st.session_state:
    st.session_state.generated_book_list = None

COLLECTION = parse_book_entries("data/book_entries.txt")

retriever = load_book_retriever() if OPENAI_API_KEY else None

if not OPENAI_API_KEY:
    st.warning("OpenAI API key not found. AI features are disabled.")

st.title("Scholastic Nest")
st.write("Your smart book and curriculum building assistant.")

grade = st.selectbox("Select Grade Level:", ["K - 2", "3 - 5", "6 - 8", "9 - 12"])
subject = st.text_input("Enter Subject (e.g., Reading, Math, Social Studies)")
theme = st.text_input("Enter Theme (e.g., Innovation)")

if st.button("Find Collection"):
    if not OPENAI_API_KEY:
        st.error("OpenAI API key missing.")
        st.stop()

    if not subject or not theme:
        st.error("Please enter both a subject and a theme.")
        st.stop()

    strict_query = f"Find book collections for {grade} students about '{theme}' in '{subject}'."
    strict_response = query_books(strict_query, retriever)

    st.subheader("Matching Collections:")

    if not strict_response or "i don't know" in strict_response.lower():
        broad_query = f"Find any collections related to '{theme}' or '{subject}' for all grades."
        broad_response = query_books(broad_query, retriever)

        if not broad_response or "i don't know" in broad_response.lower():
            st.error("No collections found. Try broader keywords.")
            st.session_state.generated_book_list = None
        else:
            st.session_state.generated_book_list = broad_response
    else:
        st.session_state.generated_book_list = strict_response

    st.session_state.user_submissions.append({
        "grade": grade,
        "subject": subject,
        "theme": theme,
        "submission_number": len(st.session_state.user_submissions) + 1
    })
    st.rerun()

if st.session_state.generated_book_list:
    st.subheader("Last Generated Book List:")
    st.write(st.session_state.generated_book_list)

st.title("Submission History")

if st.session_state.user_submissions:
    df = pd.DataFrame(st.session_state.user_submissions)

    if st.button("Clear Submission History"):
        st.session_state.user_submissions = []
        st.success("Submission history cleared!")
        st.rerun()

    st.bar_chart(df["theme"].value_counts())
    st.dataframe(df)

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download Submission History", csv_buffer.getvalue(), "submission_history.csv", "text/csv")
else:
    st.info("No submissions yet.")

st.title("Build Your Cart")

collection_names = [c["collection"] for c in COLLECTION]
chosen_name = st.selectbox("Select a Collection:", collection_names)
chosen_col = next(c for c in COLLECTION if c["collection"] == chosen_name)

grades_dict = chosen_col["grades"]
grade_price_labels = [f"{g} - {p}" for g, p in grades_dict.items()]
selected_grade = st.selectbox("Select Grade:", grade_price_labels)

if st.button("Add to Cart"):
    st.session_state.cart.append({"Collection": chosen_name, "Grade": selected_grade})
    st.success(f"Added {chosen_name} - {selected_grade} to cart!")

if st.session_state.cart:
    st.subheader("Your Cart")
    for item in st.session_state.cart:
        st.write(f"- {item['Collection']} ({item['Grade']})")
else:
    st.info("Your cart is empty.")
