# ##### babu_lohar.py ####

import os
import sys

import pinecone

from langchain.document_loaders import (PyPDFLoader, PyMuPDFLoader, TextLoader,
                                        Docx2txtLoader, WebBaseLoader,
                                        YoutubeLoader)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain


# The Model
class BabuLohar:

  def __init__(self, openai_api='', pinecone_api='', pinecone_env=''):
    if openai_api == '' or pinecone_api == '' == pinecone_env == '':
      print("[!] API Keys not found!!")
      exit()

    # Set the OpenAI API key
    os.environ["OPENAI_API_KEY"] = openai_api

    # Initialize Pinecone
    pinecone.init(api_key=pinecone_api, environment=pinecone_env)

    # model
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
        doc = PyMuPDFLoader(pdf_path).load()
        self.documents.extend(doc)
        print(f"[+] loaded '{pdf_path}'")
        nodata = False

    if nodata:
      print("[!] No data Loaded")
      sys.exit()
    print(f"[+] '{dir_path}' directory loaded")
    return self.documents

  def process(self, dir_path):
    # Create an instance of OpenAIEmbeddings
    embeddings = OpenAIEmbeddings()

    # loading PDF documents from a directory
    self.load_PDFs_from_dir(dir_path=dir_path)

    # splitting the data
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512,
                                                   chunk_overlap=10)
    self.documents = text_splitter.split_documents(self.documents)

    # NOTE: Using ChromaDB here
    # Vector Store  (chromadb)
    vectordb = Chroma.from_documents(documents=self.documents,
                                     embedding=embeddings,
                                     persist_directory="./persistence")

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
    # url input
    if 'http' in content:

      # youtube url
      if content.startswith("https://www.youtube.com"):
        return self.summarizer.summarize_yt(content)

      # other urls
      else:
        return self.summarizer.summarize_web(content)

    # file input
    else:
      return self.summarizer.summarize_file(content)


# Summarizer
class Summarizer:

  def __init__(self):
    self.llm = OpenAI(temperature=0)

  def summarize_file(self, filepath):

    if filepath.endswith('.pdf'):
      loader = PyPDFLoader(filepath)

    elif filepath.endswith('.txt'):
      loader = TextLoader(filepath)

    elif filepath.endswith('.doc'):
      loader = Docx2txtLoader(filepath)

    elif filepath.endswith('.docx'):
      loader = Docx2txtLoader(filepath)

    else:
      return "Error: This File Type is not supported"

    docs = loader.load_and_split()
    print(docs)
    chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary

  def summarize_web(self, url):
    loader = WebBaseLoader(url)
    docs = loader.load_and_split()
    print(docs)
    chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary

  def summarize_yt(self, url):
    if '=' not in url: return "Error: No YouTube video found"
    loader = YoutubeLoader(video_id=url.split("=")[-1])
    docs = loader.load_and_split()
    chain = load_summarize_chain(llm=self.llm, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary


# main
if __name__ == "__main__":
  x = Summarizer()
