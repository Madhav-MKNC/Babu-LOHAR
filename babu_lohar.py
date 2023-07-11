# ##### babu_lohar.py ####

import os
import sys

import pinecone

from langchain.document_loaders import (PyPDFLoader, CSVLoader,
                                        UnstructuredExcelLoader, TextLoader,
                                        Docx2txtLoader, YoutubeLoader)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain


# API Keys Error
class API_KEYS_ERROR(Exception):

  def __init__(self):
    super().__init__("Set required API Keys and all")


# The Model
class BabuLohar:

  def __init__(self, openai_api='', pinecone_api='', pinecone_env=''):
    if openai_api == '' or pinecone_api == '' == pinecone_env == '':
      raise API_KEYS_ERROR

    # Set the OpenAI API key
    os.environ["OPENAI_API_KEY"] = openai_api

    # Initialize Pinecone
    pinecone.init(api_key=pinecone_api, environment=pinecone_env)

    # model
    self.persist_directory = "./ok"  # path for persistence
    if not os.path.exists(self.persist_directory):
      os.makedirs(self.persist_directory)
    self.documents = []
    self.QA = self.process("./data")

    # summarizer
    self.summarizer = Summarizer()

  # Loading from a directory
  def load_PDFs_from_dir(self, dir_path='.'):
    nodata = True
    for file in os.listdir(dir_path):
      if file.endswith('.pdf'):
        print(f"[*] loading {file}")
        pdf_path = os.path.join(dir_path, file)
        loader = PyMuPDFLoader(pdf_path)
        self.documents.extend(loader.load())
        print(f"[+] loaded '{pdf_path}'")
        nodata = False

    if nodata:
      print("[!] No data Loaded")
      sys.exit()
    print(f"[+] '{dir_path}' directory loaded")
    return self.documents

  # Splitting the data
  def _split(self, docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512,
                                                   chunk_overlap=10)
    texts = text_splitter.split_documents(docs)
    return texts

  # embeddings, vectore store and retrival
  def process(self, dir_path):
    # Create an instance of OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()

    # loading PDF documents from a directory
    self.load_PDFs_from_dir(dir_path=dir_path)

    # NOTE: Using ChromaDB here
    # Vector Store  (chromadb)
    vectordb = Chroma.from_documents(documents=self._split(self.documents),
                                     embedding=embeddings,
                                     persist_directory=self.persist_directory)

    # Persist the vector store to the specified directory
    vectordb.persist()

    # Create a retriever from the vector store with search parameters
    retriever = vectordb.as_retriever(
      search_kwargs={"k": 1}  # k=3 was throwing a WARNING
    )

    # Create a RetrievalQA model from the -
    # language model, chain type, and retriever
    qa = RetrievalQA.from_chain_type(
      llm=ChatOpenAI(model_name='gpt-3.5-turbo'),
      chain_type="stuff",
      retriever=retriever)

    # return the model
    return qa

  # I/O
  def get_response(self, query='hello'):
    response = self.QA(query)["result"]
    return response

  # summarizer
  def summarize(self, content):
    if 'http' in content:
      if content.startswith("https://www.youtube.com"):
        return self.summarizer.summarize_yt(content)
      else:
        return "This Loader is under development"
    else:
      return self.summarizer.summarize_file(content)


# Summarizer
class Summarizer:

  def __init__(self):
    self.llm = OpenAI(temperature=0)

  def summarize_file(self, filepath):

    if filepath.endswith('.pdf'):
      loader = PyPDFLoader(filepath)

    if filepath.endswith('.csv'):
      loader = CSVLoader(filepath)

    if filepath.endswith('xlsx'):
      loader = UnstructuredExcelLoader(filepath)

    if filepath.endswith('.txt'):
      loader = TextLoader(filepath)

    if filepath.endswith('.doc'):
      loader = Docx2txtLoader(filepath)

    docs = loader.load_and_split()
    chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary

  def summarize_web(self, url):
    pass

  def summarize_yt(self, url):
    loader = YoutubeLoader(video_id=url.split("=")[-1])
    docs = loader.load_and_split()
    chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary


# main
if __name__ == "__main__":
  x = Summarizer()
