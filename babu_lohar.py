# ##### babu_lohar.py ####

import os
import pinecone
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import TextLoader


class API_KEYS_ERROR(Exception):
    def __init__():
        super().__init__("Set required API Keys and all")
      

# The Model
class BabuLohar:
  def __init__(self, openai_api='', pinecone_api='', pinecone_env=''):
    if openai_api == '' or pinecone_api == '' == pinecone_env == '':
      raise API_KEYS_ERROR
    # Set the OpenAI API key
    os.environ["OPENAI_API_KEY"] = openai_api
    # Initialize Pinecone
    pinecone.init(
      api_key = pinecone_api,
      environment = pinecone_env
    )
    # model
    self.QA = self.process()
    
  # Loading Documents
  def load_PDFs_from_dir(self, dir_path='.'):
    documents = []
    for file in os.listdir(dir_path):
      if file.endswith('.pdf'):
        print(f"[*] loading {file}")
        pdf_path = os.path.join(dir_path, file)
        loader = PyMuPDFLoader(pdf_path)
        documents.extend(loader.load())
    print(f"[+] '{dir_path}' directory loaded")
    return documents

  # Splitting the data  
  def _split(self, docs):
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size = 512,
      chunk_overlap = 10
    )
    texts = text_splitter.split_documents(docs)
    return texts

  # embeddings, vectore store and retrival
  def process(self):
    # Create an instance of OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()

    # Set the directory path for persistence
    persist_directory = "./ok"

    # loading PDF documents from a directory
    docs = self.load_PDFs_from_dir(
      dir_path = "./data"
    )

    """ NOTE: Using ChromaDB here """
    # Vector Store  (chromadb)
    vectordb = Chroma.from_documents(
      documents = self._split(docs),
      embedding = embeddings,
      persist_directory = persist_directory
    )

    # Persist the vector store to the specified directory
    vectordb.persist()

    # Create a retriever from the vector store with search parameters
    retriever = vectordb.as_retriever(
      search_kwargs = {"k": 1} # k=3 was throwing a WARNING
    )  

    # Create a RetrievalQA model from the -
    # language model, chain type, and retriever
    qa = RetrievalQA.from_chain_type(
      llm = ChatOpenAI(model_name='gpt-3.5-turbo'),
      chain_type = "stuff",
      retriever = retriever
    )

    # return the model 
    return qa

  # I/O 
  def get_response(self, query='hello'):
    response = self.QA(query)["result"]
    return response
    
    
# main
if __name__ == "__main__":
  babu = BabuLohar()
  query = 'tell me about yourself'
  response = babu.get_response(query)
  print(response)
  





