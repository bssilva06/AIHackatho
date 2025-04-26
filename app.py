import streamlit as st
import os
import pandas as pd
import io
from dotenv import load_dotenv
import parse_book_entries

st.set_page_config(page_title="AI Book Boss", layout="wide")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Dummy book database
COLLECTION = parse_book_entries.parse_book_entries("data/book_entries.txt")
title_set = {col["collection"] for col in COLLECTION}

# Only load LangChain if API Key is available
if OPENAI_API_KEY:
    from langchain_community.llms import OpenAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chains import RetrievalQA
    import re
    from filters import grade_in_page

    @st.cache_resource
    def load_books():
        with open("data/book_entries.txt", "r", encoding="utf-8") as f:
            text = f.read()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents([Document(page_content=text)])
        
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(docs, embeddings)
        
        retriever = db.as_retriever()
        return retriever

    def get_response(query, retriever):
        qa = RetrievalQA.from_chain_type(
            llm=OpenAI(temperature=0.2),
            retriever=retriever
        )
        return qa.run(query)

    retriever = load_books()
else:
    st.warning("⚠️ OpenAI API key not found. AI features are disabled. You can still develop the app layout!")

# --- Streamlit Frontend ---
st.title("📚 AI Book Boss")
st.write("This is a digital assistant that acts like a genius librarian meets a curriculum builder.")

# User Inputs
grade = st.selectbox(
    "Select Grade Level:",
    ["K - 2", "3 - 5", "6 - 8", "9 - 12"]
)

subject = st.text_input("Enter Subject (e.g., Reading, Math, Social Studies)")
theme = st.text_input("Enter Theme (e.g., Innovation)")

# ✅ Always initialize submission state
if "user_submissions" not in st.session_state:
    st.session_state.user_submissions = []

# ✅ Always initialize generated book list
if "generated_book_list" not in st.session_state:
    st.session_state.generated_book_list = None

if st.button("Find Collection"):
    if not OPENAI_API_KEY:
        st.error("OpenAI API key not found. Cannot generate book list.")
    else:
        if not subject or not theme:
            st.error("⚠️ Please enter both a subject and a theme before searching.")
            st.stop()

        st.success(f"Searching for Grade {grade}, Subject: {subject}, Theme: {theme}...")

        # ✅ First, try strict matching
        strict_query = (
            f"Find book collections specifically for {grade} students about '{theme}' in the subject '{subject}'. "
            f"Return the collection name, description, and list of books."
        )
        strict_response = get_response(strict_query, retriever)

        st.subheader("📚 Matching Collections:")

        if strict_response and "i don't know" in strict_response.lower():
            st.error("Sorry, no collections found matching that grade, subject, and theme. Please try broader keywords.")
            st.session_state.generated_book_list = None
        elif strict_response and strict_response.strip():
            st.session_state.generated_book_list = strict_response
        else:
            # Fallback broad search
            st.warning("No exact match found! Searching more broadly...")

            broad_query = (
                f"Find any book collections related to '{theme}' or '{subject}' for elementary to high school students. "
                f"Return the collection name, description, and list of books."
            )
            broad_response = get_response(broad_query, retriever)

            if broad_response and "i don't know" in broad_response.lower():
                st.error("Sorry, no collections found even after broad search. Please try different keywords.")
                st.session_state.generated_book_list = None
            elif broad_response and broad_response.strip():
                st.session_state.generated_book_list = broad_response
            else:
                st.error("No results found. Please try again later.")
                st.session_state.generated_book_list = None

        # ✅ Always save the submission, whether strict or broad
        st.session_state.user_submissions.append({
            "grade": grade,
            "subject": subject,
            "theme": theme,
            "submission_number": len(st.session_state.user_submissions) + 1
        })

        # ✅ Force Streamlit to rerun and refresh
        st.rerun()

# ✅ Show generated book list
if st.session_state.generated_book_list:
    st.subheader("📚 Last Generated Book List:")
    st.write(st.session_state.generated_book_list)

# ✅ Submission Graph
st.title("📈 Submission Request History")

if st.button("🧹 Clear Submission History"):
    st.session_state.user_submissions = []
    st.success("Submission history cleared!")

if st.session_state.user_submissions:
    df = pd.DataFrame(st.session_state.user_submissions)

    # Count most searched themes
    theme_counts = df["theme"].value_counts()

    # Bar Chart
    st.subheader("🔍 Most Searched Topics (Themes)")
    st.bar_chart(theme_counts)

    # Submissions Table
    st.subheader("📋 Submission History Table")
    st.dataframe(df)

    # Download Button
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Submission History as CSV",
        data=csv_buffer.getvalue(),
        file_name="submission_history.csv",
        mime="text/csv"
    )
else:
    st.info("No submissions yet. Try finding a collection first!")

# ✅ Shopping Cart Section
st.title("🛒 Choose a Collection to Add to Cart")

if "cart" not in st.session_state:
    st.session_state.cart = []

selected_collection_title = st.selectbox(
    "Select a Collection:",
    sorted(list(title_set))
)

available_grades = [col["grade"] for col in COLLECTION if col["collection"] == selected_collection_title]

selected_grade = st.selectbox(
    "Select a Grade Level:",
    available_grades
)

if st.button("Add to Cart"):
    st.session_state.cart.append({
        "Collection": selected_collection_title,
        "Grade": selected_grade
    })
    st.success(f"✅ Added {selected_collection_title} ({selected_grade}) to your cart!")

# View Cart
if st.session_state.cart:
    st.subheader("🛒 Your Cart:")
    for item in st.session_state.cart:
        st.write(f"- {item['Collection']} ({item['Grade']})")
else:
    st.info("Your cart is empty.")
