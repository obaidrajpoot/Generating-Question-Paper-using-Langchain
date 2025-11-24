from prompt import questions_prompt
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import  DirectoryLoader, PyMuPDFLoader
from document_preprocess import preprocess


splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)

doc = DirectoryLoader(
    "C:/Users/obaid/Desktop/questions_chatbot/pdf_files",
    loader_cls=PyMuPDFLoader, 
    glob="*.pdf"
)

load = doc.load()
doc_load = [d.page_content for d in load]



document = preprocess(doc_load)
document = " ".join(document)

chunks = splitter.split_text(document)

pdf_text = " ".join(chunks)

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

model = ChatOpenAI(model = 'google/gemma-3n-e2b-it:free',
                   api_key='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',
                   base_url="https://openrouter.ai/api/v1")


def generate_question(level,short_ques,long_ques,mcq_ques,fill_ques):

     final_prompt =questions_prompt.format(pdf_text=pdf_text,difficulty=level,
                                         short_size=short_ques,long_size=long_ques,
                                           mcq_size=mcq_ques,fill_size=fill_ques  )

     return model.invoke(final_prompt).content