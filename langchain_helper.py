from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQAWithSourcesChain

def load_book_retriever():
    with open("data/book_entries.txt", "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_documents([Document(page_content=text)])

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(docs, embeddings)

    return db.as_retriever()

def query_books(query, retriever):
    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=OpenAI(temperature=0.2),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )
    return qa_chain.invoke({"question": query})
