"""Strict request transport schemas and validation base models."""

from pydantic import BaseModel, ConfigDict


class StrictRequestModel(BaseModel):
    """Base request model enforcing strict transport boundaries.

    Rejects unexpected extra fields cleanly without silent omission.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=False,
        validate_assignment=True,
    )
