
"""
Model utilities for FinTalk application.
Handles Google Generative AI model initialization and configuration.
"""

import google.generativeai as genai
import streamlit as st
from typing import Optional


@st.cache_resource
def init_model(api_key: str) -> Optional[genai.GenerativeModel]:
    """
    Initialize Google Generative AI model with caching.
    
    Args:
        api_key (str): Google API key for authentication
        
    Returns:
        GenerativeModel: Initialized Gemini model instance
        
    Raises:
        Exception: If model initialization fails
    """
    if not api_key or not api_key.strip():
        raise ValueError("API key cannot be empty")
        
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Failed to initialize model: {str(e)}")
        raise
