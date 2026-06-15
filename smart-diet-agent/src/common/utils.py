from typing import Any, Dict, Optional
from datetime import datetime


def format_nutrition_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化营养数据"""
    return {
        "calories": round(data.get("calories", 0), 1),
        "protein": round(data.get("protein", 0), 1),
        "fat": round(data.get("fat", 0), 1),
        "carbs": round(data.get("carbs", 0), 1),
        "fiber": round(data.get("fiber", 0), 1),
        "sugar": round(data.get("sugar", 0), 1),
        "sodium": round(data.get("sodium", 0), 1),
    }


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """计算基础代谢率 (BMR)"""
    if gender.lower() == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)


def calculate_tdee(bmr: float, activity_level: str = "moderate") -> float:
    """计算每日总能量消耗 (TDEE)"""
    activity_factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return bmr * activity_factors.get(activity_level, 1.55)


def get_current_time() -> str:
    """获取当前时间字符串"""
    return datetime.now().isoformat()


def validate_food_name(name: str) -> bool:
    """验证食物名称"""
    if not name or len(name.strip()) < 2:
        return False
    return True
