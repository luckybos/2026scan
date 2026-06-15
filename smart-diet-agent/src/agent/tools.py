from typing import Dict, Any, List
from langchain.tools import tool
from src.core.nutrition_calc import NutritionCalculator
from src.core.recipe_engine import RecipeEngine
from src.core.user_profile import UserProfile


class DietTools:
    """工具函数封装"""
    
    def __init__(self):
        self.nutrition_calc = NutritionCalculator()
        self.recipe_engine = RecipeEngine()
        self.user_profile = UserProfile()
    
    @tool
    def calculate_food_nutrition(self, food_name: str, quantity: float = 100) -> Dict[str, float]:
        """
        计算食物的营养成分
        
        Args:
            food_name: 食物名称（如：苹果、鸡胸肉）
            quantity: 重量（克），默认100克
        
        Returns:
            营养成分字典，包含热量、蛋白质、脂肪、碳水化合物等
        """
        nutrition = self.nutrition_calc.get_food_nutrition(food_name)
        if nutrition:
            ratio = quantity / 100
            return {k: round(v * ratio, 1) for k, v in nutrition.items()}
        return {"error": f"未找到食物：{food_name}"}
    
    @tool
    def calculate_meal_nutrition(self, foods: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        计算一餐的总营养
        
        Args:
            foods: 食物列表，每个元素包含name（食物名）和quantity（重量克）
        
        Returns:
            总营养成分字典
        """
        return self.nutrition_calc.calculate_meal_nutrition(foods)
    
    @tool
    def generate_recipe(self, requirements: str) -> Dict[str, Any]:
        """
        根据需求生成食谱
        
        Args:
            requirements: 用户需求描述（如：低卡、高蛋白、适合减脂）
        
        Returns:
            食谱信息，包含食材、步骤、营养信息等
        """
        return self.recipe_engine.generate_recipe(requirements)
    
    @tool
    def generate_daily_plan(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成一日三餐计划
        
        Args:
            user_profile: 用户画像信息
        
        Returns:
            三餐食谱列表
        """
        return self.recipe_engine.generate_daily_plan(user_profile)
    
    @tool
    def calculate_daily_goal(self, user_id: str) -> Dict[str, float]:
        """
        计算用户每日营养目标
        
        Args:
            user_id: 用户ID
        
        Returns:
            营养目标字典（BMR、TDEE、目标热量等）
        """
        return self.user_profile.calculate_daily_goal(user_id)
    
    @tool
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户画像
        
        Args:
            user_id: 用户ID
            updates: 更新的用户信息
        
        Returns:
            更新后的用户画像
        """
        return self.user_profile.update_profile(user_id, updates)
    
    @tool
    def analyze_nutrition(self, daily_nutrition: Dict[str, float], goal_calories: float) -> Dict[str, Any]:
        """
        分析营养摄入是否达到目标
        
        Args:
            daily_nutrition: 每日营养摄入
            goal_calories: 目标热量
        
        Returns:
            分析结果和建议
        """
        return self.nutrition_calc.analyze_nutrition_goal(daily_nutrition, goal_calories)
    
    def get_tool_list(self) -> List:
        """获取所有工具列表"""
        return [
            self.calculate_food_nutrition,
            self.calculate_meal_nutrition,
            self.generate_recipe,
            self.generate_daily_plan,
            self.calculate_daily_goal,
            self.update_user_profile,
            self.analyze_nutrition,
        ]
