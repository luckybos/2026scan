from typing import Dict, Any, Optional
from datetime import datetime
from src.common.utils import calculate_bmr, calculate_tdee


class UserProfile:
    """用户画像管理"""
    
    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}
    
    def create_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户画像"""
        profile = {
            "user_id": user_id,
            "name": data.get("name", "用户"),
            "age": data.get("age", 30),
            "gender": data.get("gender", "male"),
            "weight": data.get("weight", 70.0),
            "height": data.get("height", 175.0),
            "activity_level": data.get("activity_level", "moderate"),
            "goal": data.get("goal", "maintain"),
            "preferences": data.get("preferences", []),
            "restrictions": data.get("restrictions", []),
            "allergies": data.get("allergies", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        self.profiles[user_id] = profile
        return profile
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户画像"""
        return self.profiles.get(user_id)
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户画像"""
        profile = self.profiles.get(user_id)
        if not profile:
            return None
        
        profile.update(updates)
        profile["updated_at"] = datetime.now().isoformat()
        self.profiles[user_id] = profile
        return profile
    
    def delete_profile(self, user_id: str) -> bool:
        """删除用户画像"""
        if user_id in self.profiles:
            del self.profiles[user_id]
            return True
        return False
    
    def calculate_daily_goal(self, user_id: str) -> Dict[str, float]:
        """计算每日营养目标"""
        profile = self.profiles.get(user_id)
        if not profile:
            return {}
        
        bmr = calculate_bmr(profile["weight"], profile["height"], profile["age"], profile["gender"])
        tdee = calculate_tdee(bmr, profile["activity_level"])
        
        goal_multiplier = 1.0
        if profile["goal"] == "lose":
            goal_multiplier = 0.85  # 减脂：减少15%
        elif profile["goal"] == "gain":
            goal_multiplier = 1.15  # 增肌：增加15%
        
        target_calories = tdee * goal_multiplier
        
        # 计算宏量营养素目标（基于每日总热量）
        return {
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1),
            "target_calories": round(target_calories, 1),
            "target_protein": round(target_calories * 0.25 / 4, 1),   # 25%来自蛋白质
            "target_fat": round(target_calories * 0.3 / 9, 1),       # 30%来自脂肪
            "target_carbs": round(target_calories * 0.45 / 4, 1),    # 45%来自碳水
        }
    
    def get_dietary_restrictions(self, user_id: str) -> List[str]:
        """获取饮食限制"""
        profile = self.profiles.get(user_id)
        if not profile:
            return []
        return profile.get("restrictions", []) + profile.get("allergies", [])
