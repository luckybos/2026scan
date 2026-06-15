from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from src.api.schemas import (
    UserProfileCreate, UserProfileResponse,
    NutritionQueryRequest, NutritionResponse,
    MealNutritionRequest,
    RecipeRequest, RecipeResponse,
    DailyPlanRequest, DailyPlanResponse,
    ChatRequest, ChatResponse
)
from src.core.user_profile import UserProfile
from src.core.nutrition_calc import NutritionCalculator
from src.core.recipe_engine import RecipeEngine
from src.agent.graph import DietAgentGraph

router = APIRouter()

# 初始化服务
user_profile_service = UserProfile()
nutrition_calc_service = NutritionCalculator()
recipe_engine_service = RecipeEngine()
diet_agent = DietAgentGraph()


@router.post("/users/", response_model=UserProfileResponse)
async def create_user_profile(profile: UserProfileCreate):
    """创建用户画像"""
    user_id = f"user_{hash(profile.name + str(profile.age))}"
    result = user_profile_service.create_profile(user_id, profile.dict())
    
    if not result:
        raise HTTPException(status_code=400, detail="创建用户失败")
    
    return result


@router.get("/users/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """获取用户画像"""
    profile = user_profile_service.get_profile(user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return profile


@router.put("/users/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: str, updates: Dict[str, Any]):
    """更新用户画像"""
    result = user_profile_service.update_profile(user_id, updates)
    
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return result


@router.delete("/users/{user_id}")
async def delete_user_profile(user_id: str):
    """删除用户画像"""
    success = user_profile_service.delete_profile(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"message": "删除成功"}


@router.post("/nutrition/food", response_model=NutritionResponse)
async def get_food_nutrition(request: NutritionQueryRequest):
    """查询食物营养成分"""
    nutrition = nutrition_calc_service.get_food_nutrition(request.food_name)
    
    if not nutrition:
        raise HTTPException(status_code=404, detail=f"未找到食物：{request.food_name}")
    
    ratio = request.quantity / 100
    return NutritionResponse(
        food_name=request.food_name,
        **{k: round(v * ratio, 1) for k, v in nutrition.items()}
    )


@router.post("/nutrition/meal")
async def calculate_meal_nutrition(request: MealNutritionRequest):
    """计算一餐营养"""
    foods = [{"name": item.name, "quantity": item.quantity} for item in request.foods]
    result = nutrition_calc_service.calculate_meal_nutrition(foods)
    return result


@router.post("/recipes/generate", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    """生成食谱"""
    result = recipe_engine_service.generate_recipe(request.requirements)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.post("/plans/daily", response_model=DailyPlanResponse)
async def generate_daily_plan(request: DailyPlanRequest):
    """生成每日饮食计划"""
    result = recipe_engine_service.generate_daily_plan(request.user_profile.dict())
    return {"meals": result}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """智能对话"""
    result = await diet_agent.run(
        conversation_id=request.conversation_id,
        user_message=request.message,
        user_info=request.user_info
    )
    
    return ChatResponse(
        conversation_id=request.conversation_id,
        response=result["response"]
    )


@router.get("/users/{user_id}/goal")
async def get_daily_goal(user_id: str):
    """获取每日营养目标"""
    result = user_profile_service.calculate_daily_goal(user_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return result
