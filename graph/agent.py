from __future__ import annotations

import os
from typing import Any, Dict, Optional

from langchain.memory import ConversationBufferMemory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

class Agent:
    def __init__(
        self,
        *,
        name: str,
        role: str,
        llm: BaseChatModel,
        plan_template: str,
        reasoning_template: str,
        reason_llm: Optional[BaseChatModel] = None,
        plan_parser: Optional[Runnable] = None,
        reason_parser: Optional[Runnable] = None,
        memory: Optional[ConversationBufferMemory] = None,
    ) -> None:
        self.name = name
        self.role = role
        self.llm = llm
        self.reason_llm = reason_llm or llm
        self.memory = memory or ConversationBufferMemory(
            memory_key="history",
            return_messages=False,
        )
        self._last_plan: str = ""
        self._last_reasoning: str = ""
        plan_chain: Runnable = ChatPromptTemplate.from_template(plan_template) | self.llm
        if plan_parser is not None:
            plan_chain = plan_chain | plan_parser
        self.plan_chain = plan_chain

        reasoning_chain: Runnable = ChatPromptTemplate.from_template(reasoning_template) | self.reason_llm
        if reason_parser is not None:
            reasoning_chain = reasoning_chain | reason_parser
        self.reasoning_chain = reasoning_chain

    def remember_query(self, query: str) -> None:
        if query:
            self.memory.chat_memory.add_user_message(query.strip())

    def memory_as_text(self) -> str:
        history = self.memory.load_memory_variables({}).get("history", "")
        if isinstance(history, str):
            return history.strip()
        if isinstance(history, list):
            return "\n".join(str(entry).strip() for entry in history if entry)
        return ""

    def plan(self, context: Dict[str, Any]) -> str:
        response = self.plan_chain.invoke(self._augment_context(context))
        content = getattr(response, "content", response)
        plan_text = str(content).strip()
        self._last_plan = plan_text
        return content

    def reason(self, context: Dict[str, Any]) -> str:
        context_with_plan = {"plan": self._last_plan, **context}
        response = self.reasoning_chain.invoke(self._augment_context(context_with_plan))
        content = getattr(response, "content", response)
        reasoning_text = str(content).strip()
        self._last_reasoning = reasoning_text
        return content

    def snapshot(self) -> Dict[str, str]:
        return {
            "plan": self._last_plan,
            "reasoning": self._last_reasoning,
            "memory": self.memory_as_text(),
        }

    def reset(self) -> None:
        self.memory.clear()
        self._last_plan = ""
        self._last_reasoning = ""

    def _augment_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        base = {
            "agent_name": self.name,
            "agent_role": self.role,
            "memory": self.memory_as_text(),
        }
        base.update(context)
        return base
