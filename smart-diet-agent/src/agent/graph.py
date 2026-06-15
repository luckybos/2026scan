from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from src.common.config import settings
from src.agent.tools import DietTools
from src.agent.prompts import DietPrompts
from src.agent.memory import MemoryManager


class DietAgentGraph:
    """LangGraph状态图定义"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url if settings.llm_base_url else None,
            temperature=0.7,
        )
        
        self.tools = DietTools()
        self.prompts = DietPrompts()
        self.memory = MemoryManager()
        
        # 定义状态
        self.graph = StateGraph(DietAgentState)
        
        # 添加节点
        self.graph.add_node("classify_intent", self._classify_intent_node)
        self.graph.add_node("call_tool", self._call_tool_node)
        self.graph.add_node("generate_response", self._generate_response_node)
        self.graph.add_node("update_profile", self._update_profile_node)
        
        # 添加边
        self.graph.add_edge("classify_intent", "route_intent")
        self.graph.add_conditional_edges(
            "route_intent",
            self._route_intent,
            {
                "tool_call": "call_tool",
                "profile_update": "update_profile",
                "direct_response": "generate_response",
            }
        )
        self.graph.add_edge("call_tool", "generate_response")
        self.graph.add_edge("update_profile", "generate_response")
        self.graph.add_edge("generate_response", END)
        
        # 设置入口
        self.graph.set_entry_point("classify_intent")
        
        # 编译图
        self.app = self.graph.compile()
    
    async def run(self, conversation_id: str, user_message: str, user_info: Dict[str, Any] = {}) -> Dict[str, Any]:
        """运行智能体"""
        # 添加用户消息到记忆
        self.memory.add_message(conversation_id, "user", user_message)
        
        # 执行图
        state = await self.app.ainvoke({
            "conversation_id": conversation_id,
            "user_message": user_message,
            "user_info": user_info,
            "history": self.memory.get_history(conversation_id),
        })
        
        # 添加助手回复到记忆
        if state.get("response"):
            self.memory.add_message(conversation_id, "assistant", state["response"])
        
        return {"response": state.get("response", ""), "state": state}
    
    def _classify_intent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """意图分类节点"""
        intent = self.prompts.extract_intent(state["user_message"])
        return {"intent": intent, **state}
    
    def _route_intent(self, state: Dict[str, Any]) -> str:
        """意图路由"""
        intent_type = state["intent"].get("intent", "general_question")
        
        if intent_type in ["nutrition_query", "recipe_request", "daily_plan", "calories_calculation"]:
            return "tool_call"
        elif intent_type == "profile_update":
            return "profile_update"
        else:
            return "direct_response"
    
    def _call_tool_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """工具调用节点"""
        intent = state["intent"]
        intent_type = intent.get("intent")
        entities = intent.get("entities", {})
        
        tool_result = {}
        
        if intent_type == "nutrition_query":
            food_name = entities.get("food", state["user_message"])
            tool_result = self.tools.calculate_food_nutrition(food_name)
        elif intent_type == "recipe_request":
            requirements = state["user_message"]
            tool_result = self.tools.generate_recipe(requirements)
        elif intent_type == "daily_plan":
            tool_result = self.tools.generate_daily_plan(state["user_info"])
        elif intent_type == "calories_calculation":
            tool_result = self.tools.calculate_daily_goal(state.get("user_id", "default"))
        
        return {"tool_result": tool_result, **state}
    
    def _update_profile_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """用户画像更新节点"""
        user_id = state.get("user_id", "default")
        updates = state["intent"].get("entities", {})
        
        result = self.tools.update_user_profile(user_id, updates)
        return {"profile_update_result": result, **state}
    
    def _generate_response_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """响应生成节点"""
        user_message = state["user_message"]
        tool_result = state.get("tool_result", {})
        profile_update = state.get("profile_update_result", {})
        
        if tool_result:
            # 如果有工具结果，基于结果生成回复
            response = self._generate_tool_response(user_message, tool_result)
        elif profile_update:
            response = f"已更新您的个人信息。"
        else:
            # 直接回答
            response = self._generate_direct_response(user_message, state["user_info"])
        
        return {"response": response, **state}
    
    def _generate_tool_response(self, question: str, tool_result: Dict[str, Any]) -> str:
        """基于工具结果生成回复"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一位专业的营养师，请用友好、易懂的语言总结以下信息。"),
            ("human", "用户问题：{question}\n工具结果：{tool_result}\n请总结回答。")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"question": question, "tool_result": str(tool_result)})
        return response.content
    
    def _generate_direct_response(self, question: str, user_info: Dict[str, Any]) -> str:
        """直接生成回复"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompts.get_system_prompt().format(user_info=str(user_info))),
            ("human", question)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content


class DietAgentState(Dict[str, Any]):
    """智能体状态定义"""
    conversation_id: str
    user_message: str
    user_info: Dict[str, Any] = {}
    history: List[Dict[str, str]] = []
    intent: Dict[str, Any] = {}
    tool_result: Dict[str, Any] = {}
    profile_update_result: Dict[str, Any] = {}
    response: str = ""
