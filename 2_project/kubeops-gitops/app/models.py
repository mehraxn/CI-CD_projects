"""Pydantic models for the KubeNotes API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class NoteBase(BaseModel):
    """Shared fields and validation for note payloads."""

    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(default="", max_length=1000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        """Reject titles that are empty or only whitespace."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be empty or whitespace")
        return stripped


class NoteCreate(NoteBase):
    """Payload for creating a note."""


class NoteUpdate(NoteBase):
    """Payload for updating a note (full replacement of editable fields)."""


class Note(NoteBase):
    """A stored note, including its server-assigned id."""

    id: int
