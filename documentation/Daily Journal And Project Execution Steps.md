# Daily Journal And Project Execution Steps:

## Daily Journal

### Friday, June 13rd 2025
#### Tasks Performed:
- Implemented PDF file reading from local folder.
- Began working on PDF file reading from Google Drive URLs.
- Began working on raw text extraction from PDF files.
- Exploring prompt engineering techniques (one-shot prompting with structured responses), different types of responding objects (JSON, XML or XML-like objects) and drafting a prompt to extract information from PDF files.
- Debugged an error in PDF extraction related to gdown and Google Drive.
- Debugged an error in information extraction using OpenAI APIs related to incorrect prompting.
#### Challenges/Issues Faced And Solution
- GPT-4.1-mini parsing only the system prompt and hallucinates non-existent profiles.
  - Solution: Tweaking the prompt templates to make the one-shot example in the system prompt not an exact example but still demonstrate how to parse the file.
#### Decisions Made:
- Choosing OpenAI's GPT-4.1-mini model: Gemini API (even Gemini Pro models) is notorious for sometimes not responding the correct format even with prompting technique and parameters (like temperature tweak) and error catching (based on previous experience in other projects), while GPT-4o, GPT-4.1, and Deepseek models are too much and quite costly for what currently is need (CVs and resumes are nearly all texts so multi-modal capabilities are not needed, and reasoning capabilities aren't needed for this task too and may slow down the parsing even more).
- Choosing MariaDB as SQL database: I'm more familiar with MariaDB and my laptop don't have too much space left to install PostgreSQL, but since I used SQLModel (based on SQLAlchemy) and didn't use MySQL or MariaDB-only features switching to PostgreSQL would be more easily. Also using Sqlite isn't sufficient as I think as it's mentioned that it would be integrated with other applications.
- Using gdown: I initially attempted to use Google Drive  APIs but since the requirements only mention Google Drive public URLs and integrating with Google Drive APIs requires registering an application so I used gdown with is sufficents for this tasks (single file shared URL or directory of under 50 files).
#### Progress Made
- Initial modules to read and extract text from PDF CV files, and information extraction from CVs.
#### Next Steps:
- Learning about FastAPI (as I'm not familiar with the framework) and Langchain.
- Fixing further bugs in the modules to read and extract text from PDF CV files, and information extraction from CVs.
- Designing database schemas and controllers (for vector database and SQL database).
### Saturday, June 14th 2025
#### Tasks Performed
- Debugged some errors in PDF read and extract text module and information extraction modules.
- Learning about SQLModel and FastAPI (specifically routing).
- Designing the initial database schema for candidate personal details.
- Learning about Chroma and its Langchain integration, as well as different ways to extract embeddings of texts: (using embedding model APIs, Huggingface models, SpaCy, Fasttext,...)
- Creating the interface for database controllers.
#### Challenges/Issues Faced And Solution
- Vector databases don't support the same operations as SQL/no-SQL database (such as update): Using other workarounds for these operations right now (like deleting and adding a document with the same ID), will figure out if there's a better solution.
#### Decisions Made:
- Using HuggingFace embeddings for embedding extraction: SpaCy and Fasttext don't support embedding for multiple languages and may need routing for different languages, while there are HuggingFace models that can handle multiple languages (I currently use sentence-transformers/all-MiniLM-L6-v2 and it supports only English, but I can swap to sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 or other embedding models easily when needed), and embedding model APIs cost money for each request and may not the best solution (for sentitive and privacy-focused applications).
- Choosing Chroma as vector database: I'm more familiar with Chroma and FAISS over Milvus, also currently I don't have time and resources to setup a dedicated Milvus Docker or Kubernetes server for better performance so as a result I could only currently use flat storing for Milvus so the performance isn't that much better (at least currently). Some other options like Pinecone and ElasticSearch aren't open source (and unlike Milvus, Chroma, Pinecone and Faiss are all licensed in permissive licenses) and aren't mentioned in the requirements.
#### Progress Made
- Initial database schemas and database controller interfaces.
- Database (vector and SQL database) controller functions and methods.
#### Next Steps
- Completing database controllers and controller to read, parse and process parsed CV informations.
- Debugging the CV file reading and information extraction module.
### Sunday, June 15th 2025
#### Tasks Performed
- Developed controllers to extract information from candidate CV files, storing information in vector and SQL databases.
- Creating the initial API routes
- Debugging the CV processing and database controllers and fixing several bugs .
#### Challenges/Issues Faced And Solution
- Exceptions when adding documents to vector database: Vector databases like Chroma may not accept Langchain Document objects with metadata that aren't primitive types (string, float, int, double), so I used filter_complex_metadata function before adding the document to the vector database.
- There are errors when retrieving documents by IDs using Langchain's Chroma integration: It may come from the prior unfiltered document or some documents may not be filtered, I used a workaround by fetching the documents directly from Chroma, reconstruct the metadatas and create Document objects from that.
#### Decision Made
None
#### Next Steps
- Starting documenting API and creating API documentation.
- Fixing bugs in the APIs.
### Monday, June 16th 2025
- Because of personal circumstances, I couldn't proceed the project.
### Tuesday, June 17th 2025
#### Tasks Performed
- Complete the final schemas for database.
- Start documenting APIs and creating API documentation.
- Fixing bugs related to Google Drive downloading.
- Fixing the remaining bugs in database controllers and CV controllers.
#### Challenges/Issues Faced And Solution
- gdown doesn't download files correctly when using shared link for single file instead of download link: Fixed by using fuzzy=True so that it will retrieve the download file id instead so now it also works for public sharing link.
#### Decision Made
None
#### Next Steps
- Preparing initial technical documentation.
- Adding features and fixing bugs.
### Wednesday, June 18th 2025
#### Tasks Performed
- Drafting initial technical presentation.
- Fixing a bug related to updating documents where the the controller method returns the old object instead of the new object.
- Add orderBy (result order) in "/cv" route (get applications by page).
#### Challenges/Issues Faced And Solutions
None
#### Decision Made
None
#### Next Steps
- Writing final presentation.
### Thursday, June 19th 2025
#### Task Performed
- Start writing final technical presentation
- Completing project execution steps
#### Challenges/Issues Faced And Solutions
None
#### Decision Made
None
#### Next Steps
- Continue writing final technical presentation
- Complete daily journal and project execution steps
### Friday, June 20th 2025
#### Tasks Performed






