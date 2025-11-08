"""LLM service with LangChain wrapper for OpenAI."""
import os
from typing import List, Dict, AsyncIterator, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser

load_dotenv()


class LLMService:
    """Abstraction layer for LLM operations using LangChain."""

    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        streaming: bool = False
    ):
        self.model = model
        self.temperature = temperature

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            streaming=streaming,
            openai_api_key=api_key
        )

    def _build_messages(
        self,
        message: str,
        history: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> List:
        """Build message list for LangChain."""
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Add conversation history
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=message))

        return messages

    async def generate_response(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a response from the LLM."""
        history = history or []
        messages = self._build_messages(message, history, system_prompt)

        response = await self.llm.ainvoke(messages)
        return response.content

    async def stream_response(
        self,
        message: str,
        history: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream response tokens from the LLM."""
        history = history or []
        messages = self._build_messages(message, history, system_prompt)

        # Create streaming LLM if not already
        streaming_llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            streaming=True,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        async for chunk in streaming_llm.astream(messages):
            if chunk.content:
                yield chunk.content

    async def generate_structured_output(
        self,
        message: str,
        output_parser: PydanticOutputParser,
        history: List[Dict[str, str]] = None
    ) -> any:
        """Generate structured output using Pydantic parser."""
        history = history or []

        # Add format instructions to system prompt
        format_instructions = output_parser.get_format_instructions()
        system_prompt = f"You must respond with valid JSON following these instructions:\n{format_instructions}"

        messages = self._build_messages(message, history, system_prompt)

        response = await self.llm.ainvoke(messages)
        parsed_output = output_parser.parse(response.content)

        return parsed_output

