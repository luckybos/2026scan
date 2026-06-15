"""
Open Food Facts 数据清洗脚本

用于从 Open Food Facts 数据集提取和清洗营养数据。
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Any


class FoodDataCleaner:
    """食物数据清洗器"""
    
    def __init__(self, input_dir: str = "data/raw", output_dir: str = "data/cleaned"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_csv_file(self, input_file: str, output_file: str):
        """清洗CSV文件"""
        input_path = self.input_dir / input_file
        output_path = self.output_dir / output_file
        
        cleaned_data = []
        
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                cleaned_row = self._clean_row(row)
                if cleaned_row:
                    cleaned_data.append(cleaned_row)
        
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=cleaned_data[0].keys())
            writer.writeheader()
            writer.writerows(cleaned_data)
        
        print(f"清洗完成，共处理 {len(cleaned_data)} 条记录")
    
    def clean_json_file(self, input_file: str, output_file: str):
        """清洗JSON文件"""
        input_path = self.input_dir / input_file
        output_path = self.output_dir / output_file
        
        with open(input_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned_data = [self._clean_food_item(item) for item in data if self._is_valid_item(item)]
        
        with open(output_path, mode='w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        print(f"清洗完成，共处理 {len(cleaned_data)} 条记录")
    
    def _clean_row(self, row: Dict[str, str]) -> Dict[str, float]:
        """清洗单行数据"""
        result = {}
        
        try:
            # 基础信息
            result["product_name"] = self._clean_text(row.get("product_name", ""))
            
            # 营养数据（每100克）
            result["energy_kcal"] = self._parse_float(row.get("energy-kcal_100g"))
            result["protein"] = self._parse_float(row.get("proteins_100g"))
            result["fat"] = self._parse_float(row.get("fat_100g"))
            result["carbs"] = self._parse_float(row.get("carbohydrates_100g"))
            result["fiber"] = self._parse_float(row.get("fiber_100g"))
            result["sugar"] = self._parse_float(row.get("sugars_100g"))
            result["sodium"] = self._parse_float(row.get("sodium_100g"))
            
            # 验证必需字段
            if not result["product_name"] or result["energy_kcal"] is None:
                return None
            
            return result
            
        except Exception as e:
            print(f"清洗行数据失败: {e}")
            return None
    
    def _clean_food_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """清洗单个食物项"""
        result = {
            "name": self._clean_text(item.get("product_name", "")),
            "category": item.get("categories", ""),
            "brands": item.get("brands", ""),
            "nutrition": {
                "energy_kcal": self._parse_float(item.get("nutriments", {}).get("energy-kcal_100g")),
                "protein": self._parse_float(item.get("nutriments", {}).get("proteins_100g")),
                "fat": self._parse_float(item.get("nutriments", {}).get("fat_100g")),
                "carbs": self._parse_float(item.get("nutriments", {}).get("carbohydrates_100g")),
                "fiber": self._parse_float(item.get("nutriments", {}).get("fiber_100g")),
                "sugar": self._parse_float(item.get("nutriments", {}).get("sugars_100g")),
                "sodium": self._parse_float(item.get("nutriments", {}).get("sodium_100g")),
            }
        }
        return result
    
    def _is_valid_item(self, item: Dict[str, Any]) -> bool:
        """检查食物项是否有效"""
        name = self._clean_text(item.get("product_name", ""))
        energy = self._parse_float(item.get("nutriments", {}).get("energy-kcal_100g"))
        
        return bool(name) and energy is not None and energy > 0
    
    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""
        
        # 移除多余空格和特殊字符
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    def _parse_float(self, value: Any) -> float:
        """解析浮点数值"""
        if value is None or value == "":
            return None
        
        try:
            return float(value)
        except ValueError:
            return None
    
    def generate_nutrition_db(self, input_files: List[str], output_file: str = "nutrition_db.json"):
        """生成营养数据库"""
        all_foods = []
        
        for input_file in input_files:
            input_path = self.input_dir / input_file
            
            if input_file.endswith('.json'):
                with open(input_path, mode='r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    cleaned = self._clean_food_item(item)
                    if self._is_valid_item(item):
                        all_foods.append(cleaned)
            
            elif input_file.endswith('.csv'):
                with open(input_path, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        cleaned = self._clean_row(row)
                        if cleaned:
                            all_foods.append(cleaned)
        
        output_path = self.output_dir / output_file
        with open(output_path, mode='w', encoding='utf-8') as f:
            json.dump(all_foods, f, ensure_ascii=False, indent=2)
        
        print(f"营养数据库生成完成，共 {len(all_foods)} 条记录")


if __name__ == "__main__":
    cleaner = FoodDataCleaner()
    
    # 示例：清洗JSON数据
    # cleaner.clean_json_file("en.openfoodfacts.org.products.json", "cleaned_foods.json")
    
    # 示例：清洗CSV数据
    # cleaner.clean_csv_file("food_data.csv", "cleaned_foods.csv")
    
    # 示例：生成营养数据库
    # cleaner.generate_nutrition_db(["en.openfoodfacts.org.products.json"])
    
    print("数据清洗脚本已准备就绪")
