from typing import TypedDict, Optional


class ALIState(TypedDict):
    """Shared state object that flows through all 4 LangGraph nodes.
    
    This acts as the 'shared notebook' — every node reads from it
    and writes its results back into it.
    """
    hubspot_chunks: str
    discord_chunks: str
    hubspot_fields: list
    discord_fields: list
    field_mapping: dict
    generated_code: str
    validation_passed: bool
    error_log: str
    retry_count: int
