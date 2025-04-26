import os
from dotenv import load_dotenv
from langchain_community.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

def load_books():
    """Load the book entries and prepare the retriever."""
    with open("data/book_entries.txt", "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents([Document(page_content=text)])

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    retriever = db.as_retriever()
    return retriever

def get_response(query, retriever):
    """Run a query through the retrieval QA chain."""
    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0.2),
        retriever=retriever
    )
    return qa.run(query)
