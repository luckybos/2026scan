from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class UserProfileCreate(BaseModel):
    """用户注册请求模型"""
    name: str = Field(..., description="用户姓名")
    age: int = Field(..., ge=1, le=120, description="年龄")
    gender: str = Field(..., pattern="^(male|female)$", description="性别")
    weight: float = Field(..., ge=30, le=300, description="体重(kg)")
    height: float = Field(..., ge=100, le=250, description="身高(cm)")
    activity_level: str = Field("moderate", description="活动水平")
    goal: str = Field("maintain", description="目标：maintain/lose/gain")
    preferences: Optional[List[str]] = Field([], description="饮食偏好")
    restrictions: Optional[List[str]] = Field([], description="饮食限制")
    allergies: Optional[List[str]] = Field([], description="食物过敏")


class UserProfileResponse(BaseModel):
    """用户信息响应模型"""
    user_id: str
    name: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: str
    goal: str
    preferences: List[str]
    restrictions: List[str]
    allergies: List[str]
    created_at: str
    updated_at: str


class NutritionQueryRequest(BaseModel):
    """营养查询请求模型"""
    food_name: str = Field(..., description="食物名称")
    quantity: Optional[float] = Field(100, ge=1, description="重量(克)")


class NutritionResponse(BaseModel):
    """营养信息响应模型"""
    food_name: str
    calories: float = Field(..., description="热量(kcal)")
    protein: float = Field(..., description="蛋白质(g)")
    fat: float = Field(..., description="脂肪(g)")
    carbs: float = Field(..., description="碳水化合物(g)")
    fiber: float = Field(..., description="膳食纤维(g)")
    sugar: float = Field(..., description="糖分(g)")
    sodium: float = Field(..., description="钠(mg)")


class MealItem(BaseModel):
    """餐食项目模型"""
    name: str = Field(..., description="食物名称")
    quantity: float = Field(..., ge=1, description="重量(克)")


class MealNutritionRequest(BaseModel):
    """餐食营养计算请求模型"""
    foods: List[MealItem] = Field(..., description="食物列表")


class RecipeRequest(BaseModel):
    """食谱生成请求模型"""
    requirements: str = Field(..., description="食谱需求描述")


class RecipeResponse(BaseModel):
    """食谱响应模型"""
    recipe_name: str
    cooking_time: str
    servings: str
    ingredients: List[Dict[str, str]]
    steps: List[str]
    nutrition: NutritionResponse
    tips: Optional[str]


class DailyPlanRequest(BaseModel):
    """每日计划请求模型"""
    user_profile: UserProfileCreate


class DailyPlanResponse(BaseModel):
    """每日计划响应模型"""
    meals: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    """对话请求模型"""
    conversation_id: str = Field(..., description="对话ID")
    message: str = Field(..., description="用户消息")
    user_info: Optional[Dict[str, Any]] = Field({}, description="用户信息")


class ChatResponse(BaseModel):
    """对话响应模型"""
    conversation_id: str
    response: str
