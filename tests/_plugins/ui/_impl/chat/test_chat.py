# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

from typing import Dict, List

import pytest

from marimo._plugins import ui
from marimo._plugins.ui._impl.chat.chat import SendMessageRequest
from marimo._plugins.ui._impl.chat.types import (
    ChatMessage,
    ChatModelConfig,
    ChatModelConfigDict,
)
from marimo._runtime.functions import EmptyArgs


def test_chat_init():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    chat = ui.chat(mock_model)
    assert chat._model == mock_model
    assert chat._chat_history == []
    assert chat.value == []


def test_chat_with_prompts():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    prompts: List[str] = ["Hello", "How are you?"]
    chat = ui.chat(mock_model, prompts=prompts)
    assert chat._component_args["prompts"] == prompts


def test_chat_with_config():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    config: ChatModelConfigDict = {"temperature": 0.7, "max_tokens": 100}
    chat = ui.chat(mock_model, config=config)
    assert chat._component_args["config"] == config


def test_chat_send_prompt():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del config
        return f"Response to: {messages[-1].content}"

    chat = ui.chat(mock_model)
    request = SendMessageRequest(
        messages=[ChatMessage(role="user", content="Hello")],
        config=ChatModelConfig(),
    )
    response: str = chat._send_prompt(request)

    assert response == "Response to: Hello"
    assert len(chat._chat_history) == 2
    assert chat._chat_history[0].role == "user"
    assert chat._chat_history[0].content == "Hello"
    assert chat._chat_history[1].role == "assistant"
    assert chat._chat_history[1].content == "Response to: Hello"


def test_chat_get_history():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    chat = ui.chat(mock_model)
    chat._chat_history = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there!"),
    ]

    history = chat._get_chat_history(EmptyArgs())
    assert len(history.messages) == 2
    assert history.messages[0].role == "user"
    assert history.messages[0].content == "Hello"
    assert history.messages[1].role == "assistant"
    assert history.messages[1].content == "Hi there!"


def test_chat_convert_value():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    chat = ui.chat(mock_model)
    value: Dict[str, List[Dict[str, str]]] = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    }

    converted: List[ChatMessage] = chat._convert_value(value)
    assert len(converted) == 2
    assert converted[0].role == "user"
    assert converted[0].content == "Hello"
    assert converted[1].role == "assistant"
    assert converted[1].content == "Hi there!"


def test_chat_convert_value_invalid():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    chat = ui.chat(mock_model)

    with pytest.raises(ValueError, match="Invalid chat history format"):
        chat._convert_value({"invalid": "format"})


def test_chat_with_on_message():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    on_message_called = False

    def on_message(messages: List[ChatMessage]) -> None:
        del messages
        nonlocal on_message_called
        on_message_called = True

    chat = ui.chat(mock_model, on_message=on_message)
    request = SendMessageRequest(
        messages=[ChatMessage(role="user", content="Hello")],
        config=ChatModelConfig(),
    )
    chat._send_prompt(request)

    assert on_message_called


def test_chat_with_show_configuration_controls():
    def mock_model(
        messages: List[ChatMessage], config: ChatModelConfig
    ) -> str:
        del messages, config
        return "Mock response"

    chat = ui.chat(mock_model, show_configuration_controls=True)
    assert chat._component_args["show-configuration-controls"] is True
