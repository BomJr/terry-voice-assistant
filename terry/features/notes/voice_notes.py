"""
Voice Notes Manager - Terry v6.1
Save, search, and manage notes with semantic search using ChromaDB
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceNotesManager:
    """Manages voice notes with semantic search."""

    def __init__(self, db_path: Optional[str] = None, embeddings_path: Optional[str] = None):
        """
        Initialize Voice Notes Manager.

        Args:
            db_path: Path to SQLite database (default: ~/.terry/notes/notes.db)
            embeddings_path: Path to ChromaDB embeddings (default: ~/.terry/notes/embeddings)
        """
        # Setup paths
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = str(Path.home() / ".terry" / "notes" / "notes.db")

        if embeddings_path:
            self.chroma_path = embeddings_path
        else:
            self.chroma_path = str(Path.home() / ".terry" / "notes" / "embeddings")

        # Create directories
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.chroma_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self._init_db()
        self._init_embeddings()

        logger.info("Voice Notes Manager initialized")

    def _init_db(self):
        """Initialize SQLite database for notes metadata."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                completed BOOLEAN DEFAULT 0,
                priority INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
        logger.debug("Notes database initialized")

    def _init_embeddings(self):
        """Initialize ChromaDB for semantic search."""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection = self.chroma_client.get_or_create_collection("notes")

            # Load multilingual embedding model
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

            logger.debug("ChromaDB and embeddings initialized")

        except Exception as e:
            logger.warning(f"ChromaDB unavailable ({type(e).__name__}): {e}")
            logger.warning("Falling back to SQLite full-text search")
            self.chroma_client = None
            self.collection = None
            self.model = None

    def add_note(self, content: str, category: Optional[str] = None,
                 tags: Optional[List[str]] = None, priority: int = 0) -> int:
        """
        Add a new note.

        Args:
            content: Note content
            category: Optional category (e.g., "work", "personal", "shopping")
            tags: Optional list of tags
            priority: Priority level (0=normal, 1=high, 2=urgent)

        Returns:
            Note ID
        """
        # Insert into SQLite
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO notes (content, category, tags, priority) VALUES (?, ?, ?, ?)",
            (content, category, ",".join(tags) if tags else None, priority)
        )
        self.conn.commit()
        note_id = cursor.lastrowid

        # Add to vector DB if available
        if self.collection and self.model:
            try:
                embedding = self.model.encode(content).tolist()
                self.collection.add(
                    embeddings=[embedding],
                    documents=[content],
                    ids=[f"note_{note_id}"],
                    metadatas=[{
                        "category": category or "general",
                        "note_id": note_id,
                        "priority": priority
                    }]
                )
            except Exception as e:
                logger.error(f"Error adding to ChromaDB: {e}")

        logger.info(f"Note saved: ID={note_id}, category={category}")
        return note_id

    def search_notes(self, query: str, limit: int = 5,
                    category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Semantic search in notes.

        Args:
            query: Search query
            limit: Maximum number of results
            category: Optional category filter

        Returns:
            List of matching notes with similarity scores
        """
        if not self.collection or not self.model:
            # Fallback to simple text search
            logger.warning("Semantic search unavailable, using text search")
            return self._text_search(query, limit, category)

        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()

            # Search in ChromaDB
            where_filter = {"category": category} if category else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_filter
            )

            # Fetch full note data from SQLite
            notes = []
            for idx, doc in enumerate(results['documents'][0]):
                note_id = results['metadatas'][0][idx]['note_id']
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()

                if row:
                    notes.append({
                        'id': row[0],
                        'content': row[1],
                        'category': row[2],
                        'tags': row[3].split(',') if row[3] else [],
                        'created_at': row[4],
                        'completed': bool(row[6]),
                        'priority': row[7],
                        'similarity': 1.0 - results['distances'][0][idx]  # Convert distance to similarity
                    })

            return notes

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self._text_search(query, limit, category)

    def _text_search(self, query: str, limit: int,
                    category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fallback text search using SQLite LIKE."""
        cursor = self.conn.cursor()

        if category:
            cursor.execute("""
                SELECT * FROM notes
                WHERE content LIKE ? AND category = ? AND completed = 0
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{query}%", category, limit))
        else:
            cursor.execute("""
                SELECT * FROM notes
                WHERE content LIKE ? AND completed = 0
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{query}%", limit))

        notes = []
        for row in cursor.fetchall():
            notes.append({
                'id': row[0],
                'content': row[1],
                'category': row[2],
                'tags': row[3].split(',') if row[3] else [],
                'created_at': row[4],
                'completed': bool(row[6]),
                'priority': row[7],
                'similarity': 0.5  # Arbitrary for text search
            })

        return notes

    def get_recent_notes(self, limit: int = 10,
                        category: Optional[str] = None,
                        include_completed: bool = False) -> List[Dict[str, Any]]:
        """
        Get recent notes.

        Args:
            limit: Maximum number of notes
            category: Optional category filter
            include_completed: Include completed notes

        Returns:
            List of recent notes
        """
        cursor = self.conn.cursor()

        completed_filter = "" if include_completed else "completed = 0 AND"
        category_filter = f"category = '{category}' AND" if category else ""

        query = f"""
            SELECT id, content, category, tags, created_at, completed, priority
            FROM notes
            WHERE {category_filter} {completed_filter} 1=1
            ORDER BY priority DESC, created_at DESC
            LIMIT ?
        """

        cursor.execute(query, (limit,))

        notes = []
        for row in cursor.fetchall():
            notes.append({
                'id': row[0],
                'content': row[1],
                'category': row[2],
                'tags': row[3].split(',') if row[3] else [],
                'created_at': row[4],
                'completed': bool(row[5]),
                'priority': row[6]
            })

        return notes

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific note by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()

        if row:
            return {
                'id': row[0],
                'content': row[1],
                'category': row[2],
                'tags': row[3].split(',') if row[3] else [],
                'created_at': row[4],
                'updated_at': row[5],
                'completed': bool(row[6]),
                'priority': row[7]
            }
        return None

    def update_note(self, note_id: int, content: Optional[str] = None,
                   category: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   priority: Optional[int] = None):
        """Update an existing note."""
        updates = []
        params = []

        if content:
            updates.append("content = ?")
            params.append(content)

        if category:
            updates.append("category = ?")
            params.append(category)

        if tags is not None:
            updates.append("tags = ?")
            params.append(",".join(tags))

        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)

        if not updates:
            return

        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(note_id)

        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
        self.conn.execute(query, params)
        self.conn.commit()

        # Update vector DB if content changed
        if content and self.collection and self.model:
            try:
                embedding = self.model.encode(content).tolist()
                self.collection.update(
                    ids=[f"note_{note_id}"],
                    embeddings=[embedding],
                    documents=[content]
                )
            except Exception as e:
                logger.error(f"Error updating ChromaDB: {e}")

        logger.info(f"Note updated: {note_id}")

    def mark_completed(self, note_id: int):
        """Mark note as completed."""
        self.conn.execute(
            "UPDATE notes SET completed = 1, updated_at = ? WHERE id = ?",
            (datetime.now(), note_id)
        )
        self.conn.commit()
        logger.info(f"Note completed: {note_id}")

    def mark_uncompleted(self, note_id: int):
        """Mark note as not completed."""
        self.conn.execute(
            "UPDATE notes SET completed = 0, updated_at = ? WHERE id = ?",
            (datetime.now(), note_id)
        )
        self.conn.commit()
        logger.info(f"Note uncompleted: {note_id}")

    def delete_note(self, note_id: int):
        """Delete a note permanently."""
        # Delete from ChromaDB
        if self.collection:
            try:
                self.collection.delete(ids=[f"note_{note_id}"])
            except Exception as e:
                logger.error(f"Error deleting from ChromaDB: {e}")

        # Delete from SQLite
        self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()
        logger.info(f"Note deleted: {note_id}")

    def get_categories(self) -> List[str]:
        """Get list of all categories used in notes."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM notes WHERE category IS NOT NULL")
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close database connections."""
        if self.conn:
            self.conn.close()


# Singleton instance
_notes_manager: Optional[VoiceNotesManager] = None


def get_notes_manager() -> VoiceNotesManager:
    """
    Get the singleton VoiceNotesManager instance.

    Returns:
        VoiceNotesManager instance
    """
    global _notes_manager

    if _notes_manager is None:
        try:
            from terry.core.config.settings import settings
            config = settings.get("voice_notes", {})

            db_path = config.get("database_path")
            embeddings_path = config.get("embeddings_path")

            # Expand ~ in paths
            if db_path:
                db_path = str(Path(db_path).expanduser())
            if embeddings_path:
                embeddings_path = str(Path(embeddings_path).expanduser())

            _notes_manager = VoiceNotesManager(db_path, embeddings_path)

        except Exception as e:
            logger.warning(f"Could not load settings for notes: {e}")
            _notes_manager = VoiceNotesManager()

    return _notes_manager
