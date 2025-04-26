import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain

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
    """Retrieve answer + source documents."""
    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=OpenAI(temperature=0.2),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    return qa_chain.invoke({"question": query})
