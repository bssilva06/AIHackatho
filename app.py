import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
import parse_book_entries

st.set_page_config(page_title="Scholastic Nest", layout="wide")

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
        return db.as_retriever()

    retriever = load_books()
else:
    st.warning("OpenAI API key not found. AI features are disabled. You can still develop the app layout!")

# --- Streamlit Frontend ---

st.title("Scholastic Nest")
st.write("This is a digital assistant that acts like a genius librarian meets a curriculum builder.")

# User Inputs
grade = st.selectbox(
    "Select Grade Level:",
    ["K - 2", "3 - 5", "6 - 8", "9 - 12"]
)

subject = st.text_input("Enter Subject (e.g., Reading, Math, Social Studies)")


theme = st.text_input("Enter Theme (e.g., Innovation)")

if st.button("Find Collection"):
    if not OPENAI_API_KEY:
        st.error("OpenAI API key not found. Cannot generate book list.")
    else:
        st.success(f"Generated book list for Grade {grade}, Subject: {subject}, Theme: {theme}")

        # ✅ First, try strict matching
        strict_query = (
            f"Find book collections specifically for {grade} students about '{theme}' in the subject '{subject}'. "
            f"Return the collection name, description, and list of books."
        )
        strict_response = get_response(strict_query, retriever)

        # st.write("DEBUG RESPONSE:")
        # st.write(strict_response)

        st.subheader("Matching Collections:")

        if strict_response and "i don't know" in strict_response.lower():
            # ❌ If AI says "I don't know"
            st.error("Sorry, no collections found matching that grade, subject, and theme. Please try broader keywords.")
        elif strict_response and strict_response.strip():
            # ✅ Good strict match
            st.write(strict_response)
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
            elif broad_response and broad_response.strip():
                st.write(broad_response)
            else:
                st.error("No results found. Please try again later.")


st.title("📈 Submission Request History")

if "user_submissions" not in st.session_state:
    st.session_state.user_submissions = []

# Submission History
if st.session_state.user_submissions:
    if st.button("🧹 Clear Submission History"):
        st.session_state.user_submissions = []
        st.success("Submission history cleared!")

    df = pd.DataFrame(st.session_state.user_submissions)
    df["request_info"] = df["grade"] + " | " + df["subject"] + " | " + df["theme"]

    # Set request_info as X-axis and submission number as Y-axis
    st.subheader("Submission Requests Over Time")
    chart_data = df.set_index("request_info")["submission_number"]
    st.line_chart(chart_data)

    # Show the submissions table
    st.write(df)

    # Only show Download Button if there are entries
    if not df.empty:
        import io
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Submission History as CSV",
            data=csv_buffer.getvalue(),
            file_name="submission_history.csv",
            mime="text/csv"
        )

# --- Cart Section ---

st.title("Build Your Cart")

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
    st.subheader("🛒 Your Cart:")
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