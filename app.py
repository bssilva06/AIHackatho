import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
import parse_book_entries

st.set_page_config(page_title="AI Book Boss", layout="wide")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize session state
if "user_submissions" not in st.session_state:
    st.session_state.user_submissions = []
if "cart" not in st.session_state:
    st.session_state.cart = []

# Parse collections
COLLECTION = parse_book_entries.parse_book_entries("data/book_entries.txt")

# Load LangChain retriever if API key exists
if OPENAI_API_KEY:
    from langchain_community.llms import OpenAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chains import RetrievalQA

    @st.cache_resource
    def load_books():
        with open("data/book_entries.txt", "r", encoding="utf-8") as f:
            text = f.read()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents([Document(page_content=text)])
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(docs, embeddings)
        return db.as_retriever()

    retriever = load_books()
else:
    st.warning("⚠️ OpenAI API key not found. AI features are disabled.")

# --- Streamlit Frontend ---

st.title("📚 AI Book Boss")
st.write("Your digital librarian and curriculum builder.")

# AI Search Form
grade = st.selectbox("Select Grade Level:", ["K - 2", "3 - 5", "6 - 8", "9 - 12"])
subject = st.selectbox("Select Subject:", [
    "Reading", "Writing", "Math", "Science", "Social Studies", "Phonics",
    "STEAM", "STEM", "Art", "Technology", "Health",
    "Diversity and Cultural Studies", "Social-Emotional Learning"
])
theme = st.text_input("Enter Theme (e.g., Innovation)")

if st.button("Find Collection"):
    if not OPENAI_API_KEY:
        st.error("OpenAI API key not found. Cannot generate book list.")
    else:
        query = (
            f"Find reading collections suitable for {grade} students. "
            f"Theme: '{theme}', Subject: '{subject}'. "
            "Return the collection name, a short description, and the list of books."
        )
        response = retriever.invoke(query)
        st.subheader("📚 Matching Collections:")

        found = False
        for r in response:
            if grade.lower() in r.page_content.lower():
                found = True
                st.markdown("---")
                st.write(r.page_content)

        if not found:
            st.warning("No collections exactly match that grade.")

        st.subheader("📚 Lesson Plan Idea:")
        st.write(f"Create a lesson using collections about '{theme}' for {grade} students in {subject}.")
        
        st.session_state.user_submissions.append({
            "grade": grade,
            "subject": subject,
            "theme": theme,
            "submission_number": len(st.session_state.user_submissions) + 1
        })

# Submission History
if st.session_state.user_submissions:
    if st.button("🧹 Clear Submission History"):
        st.session_state.user_submissions = []
        st.success("Submission history cleared!")

    df = pd.DataFrame(st.session_state.user_submissions)
    df["request_info"] = df["grade"] + " | " + df["subject"] + " | " + df["theme"]
    
    st.subheader("📈 Submission Requests Over Time")
    st.line_chart(df.set_index("request_info")["submission_number"])
    st.write(df)

    csv_buffer = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Submission History as CSV",
        data=csv_buffer,
        file_name="submission_history.csv",
        mime="text/csv"
    )

# --- Cart Section ---

st.header("🛒 Build Your Cart")

collection_names = [c["collection"] for c in COLLECTION]
chosen_name = st.selectbox("Select a Collection:", collection_names)

chosen_col = next(c for c in COLLECTION if c["collection"] == chosen_name)
grades_dict = chosen_col["grades"]

grade_price_labels = [f"{g} - {p}" for g, p in grades_dict.items()]
chosen_label = st.selectbox("Select Grade & Price:", grade_price_labels)

grade_selected, price_selected = chosen_label.split(" - ")

st.markdown(f"**Selected:** {grade_selected}   |   **Price:** {price_selected}")

if st.button("Add to Cart"):
    st.session_state.cart.append({
        "Collection": chosen_name,
        "Grade": grade_selected,
        "Price": price_selected
    })
    st.success(f"Added {chosen_name} – {grade_selected} ({price_selected}) to cart!")

st.subheader("Current Cart")

if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"{item['Collection']} ({item['Grade']}) {item['Price']}")
else:
    st.info("Cart is empty.")

# --- Cart Total and Checkout ---

def _price_to_float(price_str):
    return float(price_str.replace("$", "").replace(",", "").strip())

cart_total = sum(_price_to_float(it["Price"]) for it in st.session_state.cart)
st.markdown(f"**Cart Total**: ${cart_total}")

if st.session_state.cart and st.button("Checkout"):
    st.success(f"Thank you! Your payment of **${cart_total:,.2f}** was processed!")
    st.session_state.cart = []