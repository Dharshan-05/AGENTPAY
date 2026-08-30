"""Embedding Vector Provider Service for AGENTPAY (Phase 169)."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence

VECTOR_DIMENSION = 128


class EmbeddingService:
    """Production service for computing text and product vector embeddings (Phase 169)."""

    def embed_text(self, text: str) -> list[float]:
        """Compute a normalized 128-dimensional vector embedding for text."""
        if not text or not text.strip():
            return [0.0] * VECTOR_DIMENSION

        clean = text.lower().strip()
        vec = [0.0] * VECTOR_DIMENSION

        # Tokenize and accumulate deterministic pseudo-random projections
        words = clean.split()
        for idx, word in enumerate(words):
            word_hash = hashlib.sha256(word.encode("utf-8")).digest()
            for dim in range(VECTOR_DIMENSION):
                byte_val = word_hash[dim % len(word_hash)]
                # Project byte value to range [-1.0, 1.0]
                val = (float(byte_val) / 127.5) - 1.0
                vec[dim] += val * (1.0 / (1.0 + 0.1 * idx))

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            return [round(x / norm, 6) for x in vec]
        return [0.0] * VECTOR_DIMENSION

    def embed_product(
        self,
        name: str,
        sku: str,
        description: str | None = None,
    ) -> list[float]:
        """Construct deterministic product text payload and compute product vector embedding."""
        parts = [name, sku]
        if description:
            parts.append(description)
        corpus = " ".join(parts)
        return self.embed_text(corpus)

    @staticmethod
    def cosine_similarity(v1: Sequence[float], v2: Sequence[float]) -> float:
        """Compute cosine similarity between two normalized vectors (returns float between 0.0 and 1.0)."""  # noqa: E501
        if len(v1) != len(v2) or not v1 or not v2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2, strict=False))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        sim = dot_product / (norm1 * norm2)
        return round(min(1.0, max(0.0, sim)), 4)
