from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from src.common.config import settings


class MemoryManager:
    """对话记忆管理"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, conversation_id: str, role: str, content: str):
        """添加对话消息"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "role": role,
            "content": content
        })
        
        # 保持历史记录在限制范围内
        if len(self.conversations[conversation_id]) > self.max_history * 2:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history * 2:]
    
    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversations.get(conversation_id, [])
    
    def clear_history(self, conversation_id: str):
        """清除对话历史"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def build_prompt_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """构建提示词格式的对话历史"""
        history = self.get_history(conversation_id)
        formatted = []
        
        for msg in history:
            if msg["role"] == "user":
                formatted.append({"type": "human", "content": msg["content"]})
            elif msg["role"] == "assistant":
                formatted.append({"type": "ai", "content": msg["content"]})
        
        return formatted
