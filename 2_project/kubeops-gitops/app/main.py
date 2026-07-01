"""KubeNotes API — a deliberately simple FastAPI service.

Storage is in-memory: a dict guarded by a lock. All data is lost when the
process restarts. This is intentional for this stage of the project and must
not be relied upon for persistence.
"""

from __future__ import annotations

import logging
import sys
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app import __version__
from app.models import Note, NoteCreate, NoteUpdate
from app.settings import settings

# ---------------------------------------------------------------------------
# Logging: emit to stdout so container runtimes can collect it.
# ---------------------------------------------------------------------------
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("kubenotes")


# ---------------------------------------------------------------------------
# In-memory store. Data resets on restart — intentional at this stage.
# ---------------------------------------------------------------------------
class NoteStore:
    """Thread-safe in-memory note store."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._notes: dict[int, Note] = {}
        self._next_id = 1

    def list(self) -> list[Note]:
        with self._lock:
            return list(self._notes.values())

    def create(self, data: NoteCreate) -> Note:
        with self._lock:
            note = Note(id=self._next_id, **data.model_dump())
            self._notes[note.id] = note
            self._next_id += 1
            return note

    def get(self, note_id: int) -> Note | None:
        with self._lock:
            return self._notes.get(note_id)

    def update(self, note_id: int, data: NoteUpdate) -> Note | None:
        with self._lock:
            if note_id not in self._notes:
                return None
            note = Note(id=note_id, **data.model_dump())
            self._notes[note_id] = note
            return note

    def delete(self, note_id: int) -> bool:
        with self._lock:
            return self._notes.pop(note_id, None) is not None

    def reset(self) -> None:
        """Clear all data. Used by tests to isolate state."""
        with self._lock:
            self._notes.clear()
            self._next_id = 1


store = NoteStore()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Log a startup line, then hand control to the app."""
    logger.info("KubeNotes API starting: env=%s version=%s", settings.app_env, __version__)
    yield


app = FastAPI(
    title="KubeNotes API",
    version=__version__,
    description="A minimal notes API with in-memory storage (resets on restart).",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Readiness probe."""
    return {"status": "ready"}


@app.get("/notes", response_model=list[Note])
def list_notes() -> list[Note]:
    return store.list()


@app.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteCreate) -> Note:
    note = store.create(payload)
    logger.info("created note id=%s", note.id)
    return note


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    note = store.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return note


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, payload: NoteUpdate) -> Note:
    note = store.update(note_id, payload)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    logger.info("updated note id=%s", note_id)
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    if not store.delete(note_id):
        raise HTTPException(status_code=404, detail="note not found")
    logger.info("deleted note id=%s", note_id)
