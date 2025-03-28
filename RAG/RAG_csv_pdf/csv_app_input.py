import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()  # take environment variables from .env (especially openai api key)

# 1) Create LLM model
llm = ChatGroq(
    temperature=0, 
    groq_api_key=os.environ["GROQ_API_KEY"], 
    model_name="llama-3.3-70b-versatile"
)

# 2) Initialize embedding model
embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cuda"}
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs=model_kwargs
)
vectordb_file_path = "faiss_index"
    # file paths can be intialised outside and be used in functions.

# 3) Load CAV data, Create vector Database
def create_vector_db():
    # Load data from FAQ sheet
    loader = CSVLoader(file_path='sample_faqs.csv', source_column="prompt")
    data = loader.load()

    # Create a FAISS instance for vector database from 'data'
    vectordb = FAISS.from_documents(data, embeddings)

    # Save vector database locally
    vectordb.save_local(vectordb_file_path)

    # TEST = "till this step we can run and test vector db creating, running -if main create_vector_db()"

# Q&A Chain
def get_qa_chain():
    # Load the vector database from the local folder
    vectordb = FAISS.load_local(vectordb_file_path, embeddings, allow_dangerous_deserialization=True)

    # Create a retriever for querying the vector database
    retriever = vectordb.as_retriever(score_threshold=0.7)

    prompt_template = """Given the following context and a question, generate an answer based on this context only.
    In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
    If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

    CONTEXT: {context}

    QUESTION: {question}"""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type="stuff",
                                        retriever=retriever,
                                        input_key="query",
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt": PROMPT})

    return chain


if __name__ =="__main__":
    # create_vector_db()
    chain = get_qa_chain()
   
    # Tests
    # print(chain("Do you have javascript course?"))
    # print(chain("Do you provide intership? Do you have EMI option?"))