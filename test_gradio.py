from gradio_client import Client
import json

features_list = [{
    "brightness": 320.5, "frp": 45.2, "confidence": 80.0,
    "pixel_area": 1.0, "dist_to_industry_m": 500.0,
    "persistence_hours": 2.5, "recurrence_count": 1,
    "spatial_cluster_size": 3, "spread_rate": 0.0,
    "month": 6, "hour": 14, "bright_t31": 290.0,
    "brightness_ratio": 1.1, "daynight": "D",
    "industrial_type": "refinery", "land_cover_class": "Urban"
}]

client = Client("https://suraj-codes-24-ignis-ml-inference.hf.space")
result_str = client.predict(features_json=json.dumps(features_list), api_name="/predict")
print(result_str)
