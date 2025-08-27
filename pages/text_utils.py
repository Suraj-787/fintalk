"""
Text processing utilities for FinTalk application.
Provides functions for text manipulation and chunking.
"""


def split_text(text: str, max_length: int = 500) -> list[str]:
    """
    Split text into chunks of specified maximum length.
    
    Args:
        text (str): The text to split
        max_length (int): Maximum length per chunk (default: 500)
        
    Returns:
        list[str]: List of text chunks
    """
    if not text or not text.strip():
        return []
        
    words = text.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        # Check if adding the word would exceed max_length
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += " " + word if current_chunk else word
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = word
            
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks
