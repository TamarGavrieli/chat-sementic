Semantic Chat for Legal Verdicts 

System Description: 
This system implements a semantic chat interface for querying legal verdict documents. Users ask free-text questions and receive answers based on semantically relevant excerpts from court verdicts stored locally on the machine. 

Semantic Approach:
The semantic capability of the system is achieved through vector embeddings. Both document text chunks and user questions are converted into embedding vectors, and similarity search is used to retrieve relevant passages based on meaning rather than exact keyword matching. 
Document Download 
A scraper downloads 50 PDF files and 50 Word files of legal verdicts. All files are unique and stored locally under the data/raw directory. 

Technologies Used :
Backend: Python, FastAPI, SentenceTransformers, Selenium. 
Frontend: TypeScript, HTML, CSS. 

Run Instructions (Local Execution) 
1. Create a virtual environment: 
python -m venv .venv 
2. Activate the virtual environment (Windows): 
.venv\Scripts\activate 
3. Install dependencies: 
pip install -r requirements.txt 
4. Download the documents: nevigate to cd backend and run:
python scripts/download_documents.py 
5. Build the semantic database: nevigate to cd backend and run:
python scripts/build_index.py 
6. Run the backend server: 
uvicorn backend.app.main:app --reload 
Access: http://127.0.0.1:8000 
7. Run the frontend: nevigate to cd frontend and run:
python -m http.server 5500 
Access: http://localhost:5500
open localhost: 5500
This system runs fully locally and all responses reference the original source documents.
