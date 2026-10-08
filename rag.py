import os
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


class RAGSystem:

    def __init__(self):

        # ==========================================
        # EMBEDDING MODEL
        # ==========================================

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # ==========================================
        # CHROMADB
        # ==========================================

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="document_knowledge",
                metadata={
                    "hnsw:space": "cosine"
                }
            )
        )

        # Number of uploaded documents
        self.document_count = 0


    # ==========================================
    # READ DOCUMENT
    # ==========================================

    def read_document(
        self,
        file_path
    ):

        extension = os.path.splitext(
            file_path
        )[1].lower()

        # ------------------------------------------
        # PDF
        # ------------------------------------------

        if extension == ".pdf":

            reader = PdfReader(
                file_path
            )

            pages = []

            for page_number, page in enumerate(
                reader.pages,
                start=1
            ):

                text = (
                    page.extract_text()
                    or ""
                )

                if text.strip():

                    pages.append(
                        f"[Page {page_number}]\n"
                        f"{text}"
                    )

            return "\n\n".join(
                pages
            )

        # ------------------------------------------
        # TXT / MARKDOWN
        # ------------------------------------------

        elif extension in [
            ".txt",
            ".md"
        ]:

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    return file.read()

            except UnicodeDecodeError:

                with open(
                    file_path,
                    "r",
                    encoding="latin-1"
                ) as file:

                    return file.read()

        return ""


    # ==========================================
    # CREATE CHUNKS
    # ==========================================

    def create_chunks(
        self,
        text,
        chunk_size=500,
        overlap=100
    ):

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk = " ".join(
                words[start:end]
            )

            if chunk.strip():

                chunks.append(
                    chunk
                )

            start += (
                chunk_size - overlap
            )

        return chunks


    # ==========================================
    # CLEAR OLD DATABASE
    # ==========================================

    def clear_database(self):

        try:

            self.client.delete_collection(
                "document_knowledge"
            )

        except Exception:
            pass

        self.collection = (
            self.client.get_or_create_collection(
                name="document_knowledge",
                metadata={
                    "hnsw:space": "cosine"
                }
            )
        )


    # ==========================================
    # BUILD VECTOR DATABASE
    # ==========================================

    def build_database(
        self,
        file_paths
    ):

        # Start with clean database
        self.clear_database()

        all_chunks = []
        all_ids = []
        all_metadata = []

        chunk_counter = 0
        processed_documents = 0

        # ==========================================
        # READ ALL DOCUMENTS
        # ==========================================

        for file_path in file_paths:

            filename = os.path.basename(
                file_path
            )

            # Remove UUID from displayed filename
            if "_" in filename:

                display_name = (
                    filename.split("_", 1)[1]
                )

            else:

                display_name = filename

            text = self.read_document(
                file_path
            )

            if not text.strip():
                continue

            processed_documents += 1

            chunks = self.create_chunks(
                text
            )

            for chunk in chunks:

                all_chunks.append(
                    chunk
                )

                all_ids.append(
                    f"chunk_{chunk_counter}"
                )

                all_metadata.append(
                    {
                        "source": display_name
                    }
                )

                chunk_counter += 1


        # ==========================================
        # NO TEXT
        # ==========================================

        if not all_chunks:

            return {
                "success": False,
                "message": (
                    "No readable text found "
                    "in the uploaded documents."
                ),
                "documents": 0,
                "chunks": 0
            }


        # ==========================================
        # GENERATE EMBEDDINGS
        # ==========================================

        embeddings = (
            self.embedding_model.encode(
                all_chunks,
                show_progress_bar=True
            )
        )

        embeddings = embeddings.tolist()


        # ==========================================
        # STORE IN CHROMADB
        # ==========================================

        self.collection.add(

            ids=all_ids,

            documents=all_chunks,

            embeddings=embeddings,

            metadatas=all_metadata
        )


        # Save document count
        self.document_count = (
            processed_documents
        )


        return {
            "success": True,

            "documents":
                processed_documents,

            "chunks":
                len(all_chunks),

            "message":
                (
                    "Documents processed, "
                    "embeddings generated and "
                    "saved in ChromaDB successfully."
                )
        }


    # ==========================================
    # SEMANTIC SEARCH
    # ==========================================

    def search(
        self,
        question,
        top_k=3
    ):

        if self.collection.count() == 0:
            return []


        # ==========================================
        # QUESTION EMBEDDING
        # ==========================================

        question_embedding = (
            self.embedding_model.encode(
                [question]
            ).tolist()
        )


        # ==========================================
        # CHROMADB SEARCH
        # ==========================================

        results = self.collection.query(

            query_embeddings=
                question_embedding,

            n_results=min(
                top_k,
                self.collection.count()
            )
        )


        retrieved = []

        documents = results.get(
            "documents",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]


        # ==========================================
        # FORMAT RESULTS
        # ==========================================

        for i in range(
            len(documents)
        ):

            distance = float(
                distances[i]
            )

            # Cosine distance -> similarity
            similarity = max(
                0,
                1 - distance
            )

            retrieved.append(
                {
                    "content":
                        documents[i],

                    "distance":
                        round(
                            distance,
                            4
                        ),

                    "similarity":
                        round(
                            similarity,
                            4
                        ),

                    "similarity_percent":
                        round(
                            similarity * 100,
                            2
                        ),

                    "source":
                        metadatas[i][
                            "source"
                        ]
                }
            )

        return retrieved