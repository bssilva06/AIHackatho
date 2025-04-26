import streamlit as st
import os
from dotenv import load_dotenv
import parse_book_entries

st.set_page_config(page_title="AI Book Boss", layout="wide")



# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Dummy book database
COLLECTION = parse_book_entries.parse_book_entries("data/book_entries.txt")
title_set = {col["collection"] for col in COLLECTION}
BOOKS = [{"title": "Sample Book", "grade": "5", "description": "A sample book about innovation and creativity."}]

# Only load LangChain if API Key is available
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
    ["Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", "4th Grade", "5th Grade"]
)

subject = st.selectbox(
    "Select Subject:",
    [
        "Reading", "Writing", "Math", "Science", "Social Studies", "Phonics",
        "STEAM", "STEM", "Art", "Technology", "Health",
        "Diversity and Cultural Studies", "Social-Emotional Learning"
    ]
)

theme = st.text_input("Enter Theme (e.g., Innovation)")

# Buttons
st.title("Choose a Collection to Add to Cart")

# --- Replace your dummy COLLECTION list ---
# Here's a better structured COLLECTION list (you can expand it based on what you shared before):

# Initialize session state for the cart
if "cart" not in st.session_state:
    st.session_state.cart = []

# Step 1: User selects collection
selected_collection_title = st.selectbox(
    "Select a Collection:",
    [col for col in title_set]
)

# Step 2: Find the selected collection's available grades
available_grades = [col["grade"] for col in COLLECTION if col["collection"] == selected_collection_title]

# Step 3: User selects grade from available grades
selected_grade = st.selectbox(
    "Select a Grade Level:",
    available_grades
)

# Step 4: Add to Cart
if st.button("Add to Cart"):
    st.session_state.cart.append({
        "Collection": selected_collection_title,
        "Grade": selected_grade
    })
    st.success(f"Added {selected_collection_title} - {selected_grade} to your cart!")

# Step 5: View Cart
if st.session_state.cart:
    st.subheader("🛒 Your Cart:")
    for item in st.session_state.cart:
        st.write(f"- {item['Collection']} ({item['Grade']})")
else:
    st.info("Your cart is empty.")