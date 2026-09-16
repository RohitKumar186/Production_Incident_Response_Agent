from TASK4.rag.retriever import load_knowledge


def get_knowledge_base() -> list[dict]:
    return load_knowledge()