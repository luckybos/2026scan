import streamlit as st
import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# 页面配置
st.set_page_config(
    page_title="智能饮食助手",
    page_icon="🥗",
    layout="wide"
)

# 会话状态初始化
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = "default"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def call_api(endpoint, method="GET", data=None):
    """调用API接口"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data)
        elif method == "GET":
            response = requests.get(url, params=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        else:
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API调用失败: {e}")
        return None


def sidebar():
    """侧边栏组件"""
    st.sidebar.title("🥗 智能饮食助手")
    
    # 用户登录/注册状态
    if st.session_state.user_profile:
        st.sidebar.subheader(f"欢迎, {st.session_state.user_profile.get('name', '用户')}")
        if st.sidebar.button("退出登录"):
            st.session_state.user_profile = None
            st.rerun()
    else:
        st.sidebar.subheader("用户登录")
        with st.sidebar.form("login_form"):
            name = st.text_input("姓名")
            age = st.number_input("年龄", min_value=1, max_value=120, value=30)
            gender = st.selectbox("性别", ["male", "female"])
            weight = st.number_input("体重(kg)", min_value=30.0, max_value=300.0, value=70.0)
            height = st.number_input("身高(cm)", min_value=100.0, max_value=250.0, value=175.0)
            
            if st.form_submit_button("注册/登录"):
                profile_data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "weight": weight,
                    "height": height
                }
                result = call_api("/users/", method="POST", data=profile_data)
                if result:
                    st.session_state.user_profile = result
                    st.rerun()
    
    st.sidebar.divider()
    
    # 导航菜单
    st.sidebar.subheader("功能菜单")
    menu_options = ["智能对话", "营养查询", "食谱推荐", "每日计划", "我的信息"]
    selected = st.sidebar.radio("选择功能", menu_options)
    
    return selected


def chat_page():
    """智能对话页面"""
    st.title("💬 智能对话")
    
    # 显示聊天历史
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
    
    # 用户输入
    user_input = st.chat_input("输入您的问题...")
    if user_input:
        # 添加用户消息到历史
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # 调用API
        with st.spinner("思考中..."):
            data = {
                "conversation_id": st.session_state.conversation_id,
                "message": user_input,
                "user_info": st.session_state.user_profile or {}
            }
            result = call_api("/chat", method="POST", data=data)
            
            if result:
                response = result.get("response", "抱歉，我无法回答这个问题。")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)


def nutrition_page():
    """营养查询页面"""
    st.title("📊 营养查询")
    
    food_name = st.text_input("输入食物名称", placeholder="如：苹果、鸡胸肉")
    quantity = st.number_input("重量(克)", min_value=1, value=100)
    
    if st.button("查询营养"):
        if food_name:
            data = {"food_name": food_name, "quantity": quantity}
            result = call_api("/nutrition/food", method="POST", data=data)
            
            if result:
                st.subheader(f"{food_name} ({quantity}克) 的营养成分")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("热量", f"{result.get('calories', 0)} kcal")
                    st.metric("蛋白质", f"{result.get('protein', 0)} g")
                with col2:
                    st.metric("脂肪", f"{result.get('fat', 0)} g")
                    st.metric("碳水", f"{result.get('carbs', 0)} g")
                with col3:
                    st.metric("膳食纤维", f"{result.get('fiber', 0)} g")
                    st.metric("糖分", f"{result.get('sugar', 0)} g")


def recipe_page():
    """食谱推荐页面"""
    st.title("🍳 食谱推荐")
    
    requirements = st.text_area("输入您的需求", placeholder="如：低卡、高蛋白、适合减脂、素食等")
    
    if st.button("生成食谱"):
        if requirements:
            with st.spinner("正在生成食谱..."):
                data = {"requirements": requirements}
                result = call_api("/recipes/generate", method="POST", data=data)
                
                if result and "error" not in result:
                    st.subheader(result.get("recipe_name", "美味食谱"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"⏱️ 烹饪时间：{result.get('cooking_time', '')}")
                        st.write(f"🍽️ 份量：{result.get('servings', '')}")
                    
                    st.subheader("食材")
                    ingredients = result.get("ingredients", [])
                    if isinstance(ingredients, list):
                        for item in ingredients:
                            if isinstance(item, dict):
                                st.write(f"- {item.get('name')}: {item.get('quantity')}")
                            else:
                                st.write(f"- {item}")
                    
                    st.subheader("做法")
                    steps = result.get("steps", [])
                    for i, step in enumerate(steps, 1):
                        st.write(f"{i}. {step}")


def plan_page():
    """每日计划页面"""
    st.title("📅 每日饮食计划")
    
    if st.session_state.user_profile:
        if st.button("生成今日计划"):
            with st.spinner("正在生成饮食计划..."):
                data = {"user_profile": st.session_state.user_profile}
                result = call_api("/plans/daily", method="POST", data=data)
                
                if result:
                    meals = result.get("meals", [])
                    for meal in meals:
                        st.subheader(meal.get("meal_type", "餐食"))
                        st.write(f"**食谱**: {meal.get('recipe_name', '')}")
                        
                        ingredients = meal.get("ingredients", [])
                        if ingredients:
                            st.write("**食材**:")
                            for item in ingredients:
                                if isinstance(item, dict):
                                    st.write(f"- {item.get('name', '')}: {item.get('quantity', '')}")
        else:
            st.info("请先在侧边栏注册/登录")


def profile_page():
    """我的信息页面"""
    st.title("👤 我的信息")
    
    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**姓名**: {profile.get('name')}")
            st.write(f"**年龄**: {profile.get('age')}岁")
            st.write(f"**性别**: {'男' if profile.get('gender') == 'male' else '女'}")
        with col2:
            st.write(f"**体重**: {profile.get('weight')}kg")
            st.write(f"**身高**: {profile.get('height')}cm")
            st.write(f"**目标**: {profile.get('goal')}")
        
        # 计算并显示营养目标
        if st.button("查看营养目标"):
            user_id = profile.get("user_id")
            result = call_api(f"/users/{user_id}/goal", method="GET")
            
            if result:
                st.subheader("每日营养目标")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("基础代谢", f"{result.get('bmr', 0):.1f} kcal")
                with col2:
                    st.metric("每日消耗", f"{result.get('tdee', 0):.1f} kcal")
                with col3:
                    st.metric("目标热量", f"{result.get('target_calories', 0):.1f} kcal")
    else:
        st.info("请先在侧边栏注册/登录")


# 主应用逻辑
selected_menu = sidebar()

if selected_menu == "智能对话":
    chat_page()
elif selected_menu == "营养查询":
    nutrition_page()
elif selected_menu == "食谱推荐":
    recipe_page()
elif selected_menu == "每日计划":
    plan_page()
elif selected_menu == "我的信息":
    profile_page()
