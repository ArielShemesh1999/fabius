"""
Gmail LangChain Integration Package

This package provides Gmail functionality using the LangChain Community toolkit
for the cookie delivery agent system.
"""

from .email_utils import (
    get_gmail_message_details,
    search_gmail_messages,
    send_confirmation_email_langchain,
)
from .gmail_manager import (
    LANGCHAIN_GMAIL_AVAILABLE,
    LangChainGmailManager,
    gmail_manager,
)

__all__ = [
    "LANGCHAIN_GMAIL_AVAILABLE",
    "LangChainGmailManager",
    "get_gmail_message_details",
    "gmail_manager",
    "search_gmail_messages",
    "send_confirmation_email_langchain",
]
