import json
from itertools import combinations

from app.entities.category.category_codes import CategoryCode

for polygon_num, codes in enumerate(list(combinations(CategoryCode, 1)) + list(combinations(CategoryCode, 2)), start=1):
    with open(f"random_polygons/{polygon_num}.json") as f:
        polygon_list = json.load(f)

    shop_name = "_".join(codes)
    result = []
    for i, polygon in enumerate(polygon_list):
        result.append(
            {
                "name": f"{shop_name} shop {i}",
                "category_codes": [code.value for code in codes],
                "delivery_areas": [{"poly": polygon}],
            }
        )

    with open(f"shops/{shop_name}_shops.json", "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False)
        print(f"{shop_name} 생성 완료")
