import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

if "user_submissions" not in st.session_state:
    st.session_state.user_submissions = []

st.set_page_config(page_title="AI Book Boss", layout="wide")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Dummy book database
COLLECTION = [{"Title": "Sample Collection"}]
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
if st.button("Generate Book List"):
    if not OPENAI_API_KEY:
        st.error("OpenAI API key not found. Cannot generate book list.")
    else:
        st.success(f"Generated book list for Grade {grade}, Subject: {subject}, Theme: {theme}")

        query = (
            f"Find reading collections suitable for {grade} students. "
            f"The collections should match the theme '{theme}' and the subject area '{subject}'. "
            f"Return the collection name, a short description of the collection, and the list of books it includes."
        )

        response = retriever.invoke(query)

        st.subheader("📚 Matching Collections:")

        # ✅ New: Filter collections that match the grade
        found = False
        for r in response:
            page = r.page_content

            if grade.lower() in page.lower():
                found = True
                st.markdown("---")
                st.write(page)

        if not found:
            st.warning("No collections exactly match that grade. Try a different theme or subject.")

        # ✅ Lesson plan still shows
        st.subheader("📚 AI-Generated Lesson Plan Idea:")
        st.write(f"Create a lesson using one or more collections about '{theme}' for {grade} students focusing on {subject} concepts.")

        st.info(f"Search Saved: Grade={grade}, Subject={subject}, Theme={theme}")

        st.session_state.user_submissions.append({
            "grade": grade,
            "subject": subject,
            "theme": theme,
            "submission_number": len(st.session_state.user_submissions) + 1
        })



if st.session_state.user_submissions:
    # Clear Submissions Button
    if st.button("🧹 Clear Submission History"):
        st.session_state.user_submissions = []
        st.success("Submission history cleared! 🚀")

    df = pd.DataFrame(st.session_state.user_submissions)

    # Show Line Graph
    st.subheader("📈 Submissions Over Time")
    st.line_chart(df["submission_number"])
    st.write(df)

    # Only show Download Button if there are entries
    if not df.empty:
        import io
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Submission History as CSV",
            data=csv_buffer.getvalue(),
            file_name="submission_history.csv",
            mime="text/csv"
        )

# Buy Collection Section
st.title("🛒 Book Collection Purchase")

if st.button("Buy a Book Collection"):
    selected_collection = st.selectbox("Which collection would you like to purchase?", [col["Title"] for col in COLLECTION])
    st.success(f"Collection selected: {selected_collection}")

# Find Books by Keyword Section
st.title("🔍 Book Finder by Keyword")

keyword = st.text_input("Enter a keyword to search book descriptions:")

if keyword:
    st.subheader(f"Search Results for '{keyword}':")
    results = []
    for book in BOOKS:
        if keyword.lower() in book["description"].lower():
            results.append(book)

    if results:
        for book in results:
            st.write(f"- {book['title']} ({book['grade']} Grade)")
    else:
        st.warning("No books matched your keyword.")