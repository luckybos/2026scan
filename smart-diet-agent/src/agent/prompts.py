from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from src.common.config import settings


class DietPrompts:
    """提示词模板管理"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url if settings.llm_base_url else None,
            temperature=0.1,
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
        你是一位专业的智能饮食助手，名叫"小食"。
        
        你的职责：
        1. 回答用户关于饮食、营养、健康的问题
        2. 根据用户情况提供个性化饮食建议
        3. 帮助用户制定健康的饮食计划
        4. 提供食谱推荐和烹饪建议
        
        要求：
        - 回答要专业、准确、易懂
        - 语气友好、亲切
        - 涉及医疗建议时要谨慎，建议咨询专业医生
        - 使用中文回复
        
        用户信息（如有）：
        {user_info}
        """
    
    def get_nutrition_query_prompt(self) -> ChatPromptTemplate:
        """营养查询提示词"""
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "用户问：{question}\n请提供详细的营养信息和建议。")
        ])
    
    def get_recipe_suggestion_prompt(self) -> ChatPromptTemplate:
        """食谱建议提示词"""
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "用户想要：{request}\n请推荐合适的食谱。")
        ])
    
    def get_daily_plan_prompt(self) -> ChatPromptTemplate:
        """每日计划提示词"""
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "请为我制定一份{meal_type}的饮食计划。\n用户偏好：{preferences}\n饮食限制：{restrictions}")
        ])
    
    def get_health_advice_prompt(self) -> ChatPromptTemplate:
        """健康建议提示词"""
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "用户健康状况：{health_conditions}\n请提供饮食建议。")
        ])
    
    def extract_intent(self, query: str) -> Dict[str, Any]:
        """提取用户意图"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            你是一个意图分类器，需要分析用户的问题并提取意图。
            
            可能的意图类型：
            - nutrition_query: 查询食物营养信息
            - recipe_request: 请求食谱推荐
            - daily_plan: 请求每日饮食计划
            - health_advice: 请求健康建议
            - profile_update: 更新用户信息
            - calories_calculation: 热量计算
            - general_question: 一般问题
            
            输出格式：
            {
                "intent": "意图类型",
                "entities": {"key": "value"},
                "confidence": 0.0-1.0
            }
            """),
            ("human", "用户输入：{query}")
        ])
        
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser
        
        try:
            return chain.invoke({"query": query})
        except:
            return {
                "intent": "general_question",
                "entities": {},
                "confidence": 0.5
            }
