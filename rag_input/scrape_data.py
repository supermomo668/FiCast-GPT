import os

from unstructured.ingest.connector.wikipedia import SimpleWikipediaConfig
from unstructured.ingest.interfaces import PartitionConfig, ProcessorConfig, ReadConfig
from unstructured.ingest.runner import WikipediaRunner

from unstructured.ingest.connector.pinecone import (
    PineconeAccessConfig,
    PineconeWriteConfig,
    SimplePineconeConfig,
)

from unstructured.ingest.connector.local import SimpleLocalConfig
from unstructured.ingest.interfaces import (
    ChunkingConfig,
    EmbeddingConfig,
    PartitionConfig,
    ProcessorConfig,
    ReadConfig,
)
from unstructured.ingest.runner import LocalRunner
from unstructured.ingest.runner.writers.pinecone import (
    PineconeWriter,
)
from unstructured.ingest.runner.writers.base_writer import Writer

from unstructured.ingest.interfaces import PartitionConfig, ProcessorConfig, ReadConfig

from dotenv import load_dotenv

load_dotenv()


def get_writer() -> Writer:
    return PineconeWriter(
        connector_config=SimplePineconeConfig(
            access_config=PineconeAccessConfig(api_key=os.getenv("PINECONE_API_KEY")),
            index_name=os.getenv("PINECONE_INDEX_NAME"),
            environment=os.getenv("PINECONE_ENVIRONMENT_NAME"),
        ),
        write_config=PineconeWriteConfig(batch_size=80),
    )


def get_wiki_and_pinecone_write(character_name):
    runner = WikipediaRunner(
            processor_config=ProcessorConfig(
                verbose=True,
                output_dir="wikipedia-ingest-output",
                num_processes=2,
            ),
            read_config=ReadConfig(),
            partition_config=PartitionConfig(
                partition_by_api=True,
                api_key=os.getenv("UNSTRUCTURED_API_KEY"),
                partition_endpoint = "https://api.unstructuredapp.io/general/v0/general"
            ),
            connector_config=SimpleWikipediaConfig(
                page_title=f"{character_name}",
                auto_suggest=False,
            ),
            chunking_config=ChunkingConfig(chunk_elements=True),
            embedding_config=EmbeddingConfig(
            provider="langchain-openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            ),
            writer=get_writer(),
            writer_kwargs={},
    )
        
    runner.run()

if __name__ == "__main__":
    get_wiki_and_pinecone_write("Elon Musk")
