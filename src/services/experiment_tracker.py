"""MLflow experiment tracking for RAG pipeline."""

import time
from typing import Optional

import mlflow
from src.core.config import settings
from src.core.logging import logger


class ExperimentTracker:
    """Tracks RAG experiments using MLflow."""

    def __init__(self):
        self.enabled = settings.mlflow_enabled
        if not self.enabled:
            logger.info("MLflow tracking disabled")
            return

        try:
            mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
            mlflow.set_experiment(settings.mlflow_experiment_name)
            logger.info(
                f"MLflow tracking enabled: {settings.mlflow_tracking_uri}, "
                f"experiment: {settings.mlflow_experiment_name}"
            )
        except Exception as e:
            logger.warning(f"MLflow initialization failed: {e}. Disabling tracking.")
            self.enabled = False

    def log_query(
        self,
        question: str,
        answer: str,
        sources: list,
        model_used: str,
        latency: float,
        k: int = 3,
    ) -> Optional[str]:
        """Log a RAG query experiment."""
        if not self.enabled:
            return None

        try:
            with mlflow.start_run(run_name="rag_query") as run:
                # Log parameters
                mlflow.log_params({
                    "llm_provider": settings.llm_provider,
                    "llm_model": model_used,
                    "embedding_model": settings.embedding_model,
                    "chunk_size": settings.chunk_size,
                    "chunk_overlap": settings.chunk_overlap,
                    "top_k": k,
                    "question_length": len(question),
                })

                # Log metrics
                relevance_scores = [
                    s.get("relevance_score", 0) for s in sources
                ]
                mlflow.log_metrics({
                    "latency_seconds": round(latency, 4),
                    "num_sources": len(sources),
                    "avg_relevance_score": round(
                        sum(relevance_scores) / max(len(relevance_scores), 1), 4
                    ),
                    "max_relevance_score": round(
                        max(relevance_scores) if relevance_scores else 0, 4
                    ),
                    "min_relevance_score": round(
                        min(relevance_scores) if relevance_scores else 0, 4
                    ),
                    "answer_length": len(answer),
                })

                # Log query and answer as tags
                mlflow.set_tags({
                    "query_type": "rag_query",
                    "question": question[:250],
                    "answer_preview": answer[:250],
                })

                logger.info(f"MLflow: Logged query run {run.info.run_id}")
                return run.info.run_id

        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}")
            return None

    def log_ingestion(
        self,
        source: str,
        title: str,
        chunks_created: int,
        total_documents: int,
        latency: float,
        file_type: str = "text",
    ) -> Optional[str]:
        """Log a document ingestion experiment."""
        if not self.enabled:
            return None

        try:
            with mlflow.start_run(run_name="document_ingestion") as run:
                mlflow.log_params({
                    "source": source[:250],
                    "title": title[:250],
                    "file_type": file_type,
                    "embedding_model": settings.embedding_model,
                    "chunk_size": settings.chunk_size,
                    "chunk_overlap": settings.chunk_overlap,
                })

                mlflow.log_metrics({
                    "chunks_created": chunks_created,
                    "total_documents": total_documents,
                    "ingestion_latency_seconds": round(latency, 4),
                })

                mlflow.set_tags({
                    "query_type": "ingestion",
                })

                logger.info(f"MLflow: Logged ingestion run {run.info.run_id}")
                return run.info.run_id

        except Exception as e:
            logger.warning(f"MLflow logging failed: {e}")
            return None


# Singleton
_tracker: Optional[ExperimentTracker] = None


def get_experiment_tracker() -> ExperimentTracker:
    """Get or create the experiment tracker singleton."""
    global _tracker
    if _tracker is None:
        _tracker = ExperimentTracker()
    return _tracker