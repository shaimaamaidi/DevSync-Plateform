"""
GitHub commit relevance filtering utilities.

This module provides functions to rank and filter GitHub commits
based on their semantic similarity to ClickUp tasks.

It uses a TF-IDF + cosine similarity approach to estimate textual
relevance between commit messages and task descriptions.

Main purpose:
- Identify commits most relevant to a given ClickUp task
- Reduce noise by filtering low-similarity commits
- Return a ranked subset of meaningful commit candidates

Functions:
    filter_commits: Rank and filter commits based on semantic similarity
        to a ClickUp task using TF-IDF vectorization.
"""

from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.src.domain.entities.clickup.list_with_tasks import ClickUpTask
from backend.src.domain.entities.github.commit import CommitDTO


def filter_commits(commits: List[CommitDTO], task: ClickUpTask) -> List[CommitDTO]:
    """
    Filter and rank GitHub commits based on semantic similarity to a ClickUp task.

    This function uses a TF-IDF vectorization combined with cosine similarity
    to measure textual relevance between commit messages and a task description.

    Pipeline:
    1. Build a textual representation of the task
    2. Extract commit messages
    3. Compute TF-IDF vectors for task + commits
    4. Calculate cosine similarity scores
    5. Filter low-relevance commits
    6. Return top-N most relevant commits

    Args:
        commits: List of GitHub commits to evaluate.
        task: Reference ClickUp task used for similarity comparison.

    Returns:
        List of commits ordered by semantic relevance (descending),
        limited to the top-N most relevant entries.
    """
    TOP_N = 20
    MIN_SCORE = 0.05

    if not commits:
        return []

    task_text = _build_task_text(task)
    commit_texts = [c.message or "" for c in commits]

    corpus = [task_text] + commit_texts

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 3),
            min_df=1,
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return commits[:TOP_N]

    task_vector = tfidf_matrix[0]
    commit_vectors = tfidf_matrix[1:]

    scores = cosine_similarity(task_vector, commit_vectors).flatten()

    scored = [
        (commits[i], scores[i])
        for i in range(len(commits))
        if scores[i] >= MIN_SCORE
    ]

    scored.sort(key=lambda x: x[1], reverse=True)

    filtered = [commit for commit, _ in scored[:TOP_N]]

    return filtered


def _build_task_text(task: ClickUpTask) -> str:
    """
    Build a textual representation of a ClickUp task for NLP comparison.

    This function concatenates relevant textual fields of a task
    to create a single document suitable for vectorization methods
    such as TF-IDF or embeddings.

    Fields included:
    - Task name
    - Task description

    Args:
        task: ClickUp task object.

    Returns:
        A normalized string representation of the task.
    """
    parts = [
        task.name or "",
        task.description or "",
    ]
    return " ".join(p for p in parts if p).strip()