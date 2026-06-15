from typing import Dict, Any, Optional, List
from src.common.utils import format_nutrition_data, calculate_bmr, calculate_tdee


class NutritionCalculator:
    """营养计算引擎"""
    
    FOOD_NUTRITION_DB: Dict[str, Dict[str, float]] = {
        "apple": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14, "fiber": 2.4, "sugar": 10, "sodium": 1},
        "banana": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23, "fiber": 2.6, "sugar": 12, "sodium": 1},
        "chicken breast": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 74},
        "rice": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28, "fiber": 0.4, "sugar": 0.1, "sodium": 1},
        "salmon": {"calories": 208, "protein": 22, "fat": 12, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 50},
        "broccoli": {"calories": 34, "protein": 2.8, "fat": 0.4, "carbs": 7, "fiber": 2.6, "sugar": 1.7, "sodium": 31},
        "eggs": {"calories": 143, "protein": 13, "fat": 10, "carbs": 1.1, "fiber": 0, "sugar": 1.1, "sodium": 124},
        "milk": {"calories": 60, "protein": 3.2, "fat": 3.2, "carbs": 4.8, "fiber": 0, "sugar": 4.8, "sodium": 42},
    }
    
    def __init__(self):
        self.food_db = self.FOOD_NUTRITION_DB
    
    def get_food_nutrition(self, food_name: str) -> Optional[Dict[str, float]]:
        """获取食物营养成分"""
        food_name_lower = food_name.lower().strip()
        return self.food_db.get(food_name_lower)
    
    def calculate_meal_nutrition(self, foods: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算一餐的总营养"""
        total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 0}
        
        for food in foods:
            name = food.get("name", "")
            quantity = food.get("quantity", 100) / 100  # 转换为100g比例
            
            nutrition = self.get_food_nutrition(name)
            if nutrition:
                for key in total:
                    total[key] += nutrition[key] * quantity
        
        return format_nutrition_data(total)
    
    def calculate_daily_nutrition(self, meals: List[List[Dict[str, Any]]]) -> Dict[str, float]:
        """计算每日总营养"""
        total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 0}
        
        for meal in meals:
            meal_nutrition = self.calculate_meal_nutrition(meal)
            for key in total:
                total[key] += meal_nutrition[key]
        
        return format_nutrition_data(total)
    
    def analyze_nutrition_goal(self, daily_nutrition: Dict[str, float], goal_calories: float) -> Dict[str, Any]:
        """分析营养目标达成情况"""
        calories_diff = daily_nutrition["calories"] - goal_calories
        status = "balanced" if abs(calories_diff) < 100 else "over" if calories_diff > 0 else "under"
        
        return {
            "status": status,
            "calories_diff": round(calories_diff, 1),
            "percentage": round(daily_nutrition["calories"] / goal_calories * 100, 1),
            "recommendation": self._generate_recommendation(status, calories_diff),
        }
    
    def _generate_recommendation(self, status: str, diff: float) -> str:
        """生成营养建议"""
        if status == "balanced":
            return "您今天的热量摄入非常均衡！"
        elif status == "over":
            return f"您今天的热量摄入超出目标 {abs(round(diff))} 千卡，建议适当减少主食或增加运动。"
        else:
            return f"您今天的热量摄入低于目标 {abs(round(diff))} 千卡，建议适当增加优质蛋白质和健康脂肪的摄入。"
