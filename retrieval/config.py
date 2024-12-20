from __future__ import annotations

from typing import Callable
from data_utils import Movie
from retrieval.indexing_pipeline_utils import get_enriched_text


class RetrievalExpsConfig:
    """
    Configuración del experimento de recuperación.
    """
    def __init__(self):
        # Función a emplear para generar el texto a indexar con embeddings
        self._text_to_embed_fn: Callable = get_enriched_text

        # Modelo de embeddings a utilizar
        self.model_name: str = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
        self.normalize_embeddings: bool = True  # Normaliza los embeddings a longitud 1

        # Preprocesador inicializado más tarde (evita circular import)
        self._query_prepro_fn: Callable = None

    def initialize_preprocessor(self):
        """
        Inicializa la función de preprocesamiento para evitar circular imports.
        """
        from retrieval.retrieval_pipeline_utils import clean_query_txt  # Importación local
        self._query_prepro_fn = clean_query_txt

    def text_to_embed_fn(self, movie: Movie) -> str:
        return self._text_to_embed_fn(movie)

    def query_prepro_fn(self, query: dict) -> str:
        if not self._query_prepro_fn:
            raise RuntimeError("La función de preprocesamiento no ha sido inicializada. Llama a 'initialize_preprocessor()' antes.")
        return self._query_prepro_fn(query)

    @property
    def index_config_unique_id(self) -> str:
        mname = self.model_name.replace("/", "_")
        return f"{mname}_{self._text_to_embed_fn.__name__}_{self.normalize_embeddings}"

    @property
    def exp_params(self) -> dict:
        """
        Retorna los parámetros del experimento como un diccionario.
        """
        return {
            "model_name": self.model_name,
            "text_to_embed_fn": self._text_to_embed_fn.__name__,
            "normalize_embeddings": self.normalize_embeddings,
            "query_prepro_fn": self._query_prepro_fn.__name__ if self._query_prepro_fn else "None",
        }
