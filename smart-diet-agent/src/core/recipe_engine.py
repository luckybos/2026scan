from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.common.config import settings


class RecipeEngine:
    """食谱生成引擎"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url if settings.llm_base_url else None,
            temperature=0.7,
        )
        
        self.recipe_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的营养师和美食家，擅长根据用户需求生成健康美味的食谱。
            
            请遵循以下规则：
            1. 食谱必须健康、营养均衡
            2. 配料要常见、容易购买
            3. 步骤要清晰、易于操作
            4. 提供营养信息和烹饪时间
            5. 考虑用户的饮食偏好和限制
            
            输出格式：
            {
                "recipe_name": "菜名",
                "cooking_time": "XX分钟",
                "servings": "X人份",
                "ingredients": [{"name": "食材名", "quantity": "分量"}],
                "steps": ["步骤1", "步骤2", ...],
                "nutrition": {"calories": XX, "protein": XX, "fat": XX, "carbs": XX},
                "tips": "烹饪小贴士"
            }
            """),
            ("human", "请根据以下需求生成食谱：\n{requirements}")
        ])
        
        self.chain = self.recipe_prompt | self.llm
    
    def generate_recipe(self, requirements: str) -> Dict[str, Any]:
        """生成个性化食谱"""
        try:
            response = self.chain.invoke({"requirements": requirements})
            return self._parse_response(response.content)
        except Exception as e:
            return {
                "error": str(e),
                "recipe_name": "生成失败",
                "ingredients": [],
                "steps": [],
                "nutrition": {}
            }
    
    def generate_daily_plan(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成一日三餐计划"""
        goals = self._build_goal_string(user_profile)
        requirements = f"""
        用户信息：
        - 年龄：{user_profile.get('age', 30)}岁
        - 性别：{user_profile.get('gender', '男')}
        - 体重：{user_profile.get('weight', 70)}kg
        - 身高：{user_profile.get('height', 175)}cm
        - 活动水平：{user_profile.get('activity_level', '中等')}
        - 饮食目标：{user_profile.get('goal', '维持体重')}
        - 饮食偏好：{user_profile.get('preferences', '无特殊偏好')}
        - 饮食限制：{user_profile.get('restrictions', '无')}
        
        请为我设计一份完整的一日三餐计划，包括早餐、午餐、晚餐。
        每餐提供一个食谱，包含食材、做法和营养信息。
        """
        
        try:
            response = self.chain.invoke({"requirements": requirements})
            return self._parse_daily_plan(response.content)
        except Exception as e:
            return [{
                "error": str(e),
                "recipe_name": "生成失败",
                "ingredients": [],
                "steps": [],
                "nutrition": {}
            }]
    
    def _build_goal_string(self, profile: Dict[str, Any]) -> str:
        """构建目标字符串"""
        goal = profile.get("goal", "维持体重")
        if goal == "减脂":
            return "控制热量摄入，高蛋白、低碳水"
        elif goal == "增肌":
            return "高热量、高蛋白"
        return "营养均衡"
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """解析LLM响应"""
        import json
        try:
            return json.loads(content)
        except:
            return {
                "recipe_name": "未命名食谱",
                "cooking_time": "30分钟",
                "servings": "2人份",
                "ingredients": [],
                "steps": content.split("\n"),
                "nutrition": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0},
                "tips": ""
            }
    
    def _parse_daily_plan(self, content: str) -> List[Dict[str, Any]]:
        """解析一日三餐计划"""
        meals = []
        sections = content.split("餐")
        
        for i, section in enumerate(sections[1:], 1):
            meal_names = ["早餐", "午餐", "晚餐"]
            if i <= len(meal_names):
                meals.append({
                    "meal_type": meal_names[i-1],
                    "recipe_name": f"{meal_names[i-1]}食谱",
                    "ingredients": [],
                    "steps": section.strip().split("\n")[:5],
                    "nutrition": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
                })
        
        return meals if meals else [{
            "meal_type": "午餐",
            "recipe_name": "默认食谱",
            "ingredients": [],
            "steps": [],
            "nutrition": {}
        }]
