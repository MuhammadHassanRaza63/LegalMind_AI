import os
import time
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_cohere import ChatCohere 
from langchain_community.vectorstores import Chroma

class LegalMind:
    def __init__(self, pdf_folder):
        # API Keys Setup
        # Read API keys from environment variables. Do NOT hardcode secrets here.
        google_api_key = os.getenv("GOOGLE_API_KEY")
        cohere_api_key = os.getenv("COHERE_API_KEY")
        if not google_api_key or not cohere_api_key:
            print("Warning: GOOGLE_API_KEY or COHERE_API_KEY not set; external API calls may fail.")
        
        persist_directory = "./db_legal"
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # Database Load/Create Logic
        if os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0:
            print("--- Loading existing Gemini Database... ---")
            self.vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            print("--- Creating NEW database... ---")
            all_docs = []
            for file in os.listdir(pdf_folder):
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(os.path.join(pdf_folder, file))
                    all_docs.extend(loader.load())
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
            chunks = splitter.split_documents(all_docs)
            self.vector_store = Chroma.from_documents(chunks, embeddings, persist_directory=persist_directory)

        # 5. Initialize Cohere Chat Model (Gemini ki jagah)
        # Iska 'command-r' model legal queries ke liye best hai
        self.llm = ChatCohere(
            model=os.getenv("COHERE_CHAT_MODEL", "command-r-plus-08-2024"),
            cohere_api_key=cohere_api_key
            )

    def _detect_response_language(self, query):
        query = (query or "").strip()

        if re.search(r"[\u0600-\u06FF]", query):
            return "urdu"

        roman_urdu_markers = [
            "kya", "kaise", "kaisay", "kr", "kar", "mujhe", "mujhy", "aap",
            "agar", "mein", "main", "kyun", "nahi", "hain", "hai", "ho",
            "batao", "samjhao", "matlab", "pehle", "phly", "sawal", "jawab"
        ]
        lowered = query.lower()
        if any(marker in lowered.split() for marker in roman_urdu_markers):
            return "roman_urdu"

        return "english"

    def ask(self, query):
        try:
            # Context dhoondo
            docs = self.vector_store.similarity_search(query, k=3)
            context = "\n".join([d.page_content for d in docs])
            response_language = self._detect_response_language(query)
            
            # Prompt design
            full_prompt = f"""
            You are LegalMind AI, a warm and professional Pakistani legal assistant.

            Follow these rules in every reply:
            1. Start with a short natural greeting before the main answer.
            2. After the greeting, briefly acknowledge the user's legal concern and help with it directly.
            3. Match the user's language exactly:
               - If user writes in English, reply in English.
               - If user writes in Roman Urdu, reply in Roman Urdu.
               - If user writes in Urdu script, reply in Urdu script.
            4. Do not mix languages unless the user mixes them first.
            5. Keep the tone helpful, respectful, and realistic.
            6. Base the legal answer on the provided context only. If context is insufficient, say so clearly.
            7. Prefer a clean pattern:
               - Greeting
               - Short understanding of the issue
               - Clear legal answer
               - Practical next step if relevant

            Detected response language: {response_language}

            Context from Law Books:
            {context}
            
            User Question:
            {query}
            """
            
            response = self.llm.invoke(full_prompt)
            return response.content
        except Exception as e:
            return f"Cohere Error: {str(e)}"
