-- 智能饮食助手数据库初始化脚本

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS smart_diet;

-- 切换到 smart_diet 数据库
-- \c smart_diet;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    height DECIMAL(5,2) NOT NULL,
    activity_level VARCHAR(50) DEFAULT 'moderate',
    goal VARCHAR(50) DEFAULT 'maintain',
    preferences TEXT[],
    restrictions TEXT[],
    allergies TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 食物营养表
CREATE TABLE IF NOT EXISTS food_nutrition (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    calories DECIMAL(10,2) NOT NULL,
    protein DECIMAL(10,2) NOT NULL,
    fat DECIMAL(10,2) NOT NULL,
    carbs DECIMAL(10,2) NOT NULL,
    fiber DECIMAL(10,2) DEFAULT 0,
    sugar DECIMAL(10,2) DEFAULT 0,
    sodium DECIMAL(10,2) DEFAULT 0,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 食谱表
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cooking_time VARCHAR(50),
    servings INT,
    ingredients TEXT NOT NULL,
    steps TEXT NOT NULL,
    nutrition_info JSONB,
    tips TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户饮食记录
CREATE TABLE IF NOT EXISTS user_meals (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    foods JSONB NOT NULL,
    total_nutrition JSONB,
    meal_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 每日营养汇总
CREATE TABLE IF NOT EXISTS daily_nutrition (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    record_date DATE NOT NULL,
    total_calories DECIMAL(10,2),
    total_protein DECIMAL(10,2),
    total_fat DECIMAL(10,2),
    total_carbs DECIMAL(10,2),
    target_calories DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE (user_id, record_date)
);

-- 对话历史表
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 创建索引
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_food_nutrition_name ON food_nutrition(name);
CREATE INDEX idx_user_meals_user_date ON user_meals(user_id, meal_date);
CREATE INDEX idx_daily_nutrition_user_date ON daily_nutrition(user_id, record_date);
CREATE INDEX idx_conversations_conversation_id ON conversations(conversation_id);

-- 插入示例食物数据
INSERT INTO food_nutrition (name, calories, protein, fat, carbs, fiber, sugar, sodium) VALUES
('apple', 52.00, 0.30, 0.20, 14.00, 2.40, 10.00, 1.00),
('banana', 89.00, 1.10, 0.30, 23.00, 2.60, 12.00, 1.00),
('chicken breast', 165.00, 31.00, 3.60, 0.00, 0.00, 0.00, 74.00),
('rice', 130.00, 2.70, 0.30, 28.00, 0.40, 0.10, 1.00),
('salmon', 208.00, 22.00, 12.00, 0.00, 0.00, 0.00, 50.00),
('broccoli', 34.00, 2.80, 0.40, 7.00, 2.60, 1.70, 31.00),
('eggs', 143.00, 13.00, 10.00, 1.10, 0.00, 1.10, 124.00),
('milk', 60.00, 3.20, 3.20, 4.80, 0.00, 4.80, 42.00)
ON CONFLICT (name) DO NOTHING;

-- 插入示例食谱
INSERT INTO recipes (name, cooking_time, servings, ingredients, steps, nutrition_info) VALUES
('鸡胸肉沙拉', '20分钟', 2, '["鸡胸肉100g", "生菜50g", "番茄50g", "橄榄油10ml"]', '["鸡胸肉切片煮熟", "生菜番茄洗净切块", "加入橄榄油拌匀"]', '{"calories": 250, "protein": 28, "fat": 12, "carbs": 5}')
ON CONFLICT DO NOTHING;

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_modtime
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_modified_column();
