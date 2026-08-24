import os
import json
import time
import base64
import cv2
import yaml
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv, set_key

class ProfileManager:
    """
    Manages Multi-Provider Model Configuration Packages (大模型配置包管理器).
    Supports switching active profiles, editing endpoints/keys, and live connection testing.
    """
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.env_path = os.path.join(self.base_dir, ".env")
        self.profiles_path = os.path.join(self.base_dir, "configs", "model_profiles.json")
        self.config_yaml_path = os.path.join(self.base_dir, "configs", "config.yaml")
        
        load_dotenv(self.env_path)
        self.data = self._load_profiles()

    def _load_profiles(self) -> dict:
        if os.path.exists(self.profiles_path):
            try:
                with open(self.profiles_path, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ProfileManager] Error loading profiles: {e}")
        return {"active_profile_id": "gemini_official_paid", "profiles": {}}

    def _save_profiles(self):
        try:
            with open(self.profiles_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ProfileManager] Error saving profiles: {e}")

    def get_all_profiles(self) -> Dict[str, dict]:
        return self.data.get("profiles", {})

    def get_active_profile(self) -> dict:
        active_id = self.data.get("active_profile_id", "gemini_official_paid")
        profiles = self.get_all_profiles()
        return profiles.get(active_id, list(profiles.values())[0] if profiles else {})

    def get_active_profile_id(self) -> str:
        return self.data.get("active_profile_id", "gemini_official_paid")

    def get_api_key_for_env(self, env_var_name: str) -> str:
        load_dotenv(self.env_path, override=True)
        return os.getenv(env_var_name, "")

    def set_api_key_for_env(self, env_var_name: str, key_val: str):
        if not os.path.exists(self.env_path):
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.write("")
        set_key(self.env_path, env_var_name, key_val)
        load_dotenv(self.env_path, override=True)

    def set_active_profile(self, profile_id: str) -> bool:
        profiles = self.get_all_profiles()
        if profile_id not in profiles:
            return False

        self.data["active_profile_id"] = profile_id
        self._save_profiles()

        # Synchronize with config.yaml
        prof = profiles[profile_id]
        try:
            cfg = {}
            if os.path.exists(self.config_yaml_path):
                with open(self.config_yaml_path, "r", encoding="utf-8-sig") as f:
                    cfg = yaml.safe_load(f) or {}

            if "brain" not in cfg:
                cfg["brain"] = {}
            if "llm" not in cfg["brain"]:
                cfg["brain"]["llm"] = {}

            cfg["brain"]["llm"]["profile_id"] = prof["id"]
            cfg["brain"]["llm"]["provider"] = prof["provider"]
            cfg["brain"]["llm"]["model"] = prof["model"]
            cfg["brain"]["llm"]["base_url"] = prof.get("base_url", "")
            cfg["brain"]["llm"]["decision_interval_sec"] = prof.get("decision_interval_sec", 2.0)

            with open(self.config_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(cfg, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"[ProfileManager] Error updating config.yaml: {e}")

        return True

    def save_profile_custom(self, profile_data: dict, api_key: Optional[str] = None):
        pid = profile_data["id"]
        if "profiles" not in self.data:
            self.data["profiles"] = {}
        self.data["profiles"][pid] = profile_data
        self._save_profiles()

        if api_key is not None and api_key.strip():
            env_var = profile_data.get("api_key_env", f"{pid.upper()}_API_KEY")
            self.set_api_key_for_env(env_var, api_key.strip())

    def test_profile_connection(self, profile_id: str) -> Tuple[bool, str, float]:
        """
        Executes a real multimodal ping to test provider connection and latency.
        Returns: (success: bool, message: str, latency_ms: float)
        """
        profiles = self.get_all_profiles()
        if profile_id not in profiles:
            return False, f"Profile '{profile_id}' not found.", 0.0

        prof = profiles[profile_id]
        provider = prof.get("provider", "gemini").lower()
        model_name = prof.get("model", "")
        base_url = prof.get("base_url", "")
        env_var = prof.get("api_key_env", "")
        api_key = self.get_api_key_for_env(env_var)

        if not api_key:
            return False, f"缺少 API Key！请在下方填入环境变量 '{env_var}' 对应的值并保存。", 0.0

        # Create 1x1 test image
        img = 255 * np.ones((64, 64, 3), dtype=np.uint8)
        cv2.putText(img, "HK", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        _, buffer = cv2.imencode(".jpg", img)
        b64_img = base64.b64encode(buffer).decode("utf-8")

        prompt = "Health check test. Return JSON: {\"status\": \"ok\"}"
        t0 = time.time()

        try:
            if provider == "gemini":
                from google import genai
                from google.genai import types
                from PIL import Image
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=[pil_img, prompt],
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                dt_ms = (time.time() - t0) * 1000.0
                if response and response.text:
                    return True, f"✅ 连接成功！响应耗时: {dt_ms:.1f}ms\n模型回复: {response.text.strip()[:100]}", dt_ms
                return False, "模型响应为空。", dt_ms

            else:
                from openai import OpenAI
                client = OpenAI(
                    base_url=base_url if base_url else "https://api.openai.com/v1",
                    api_key=api_key,
                    timeout=15.0
                )
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }
                    ],
                    max_tokens=50
                )
                dt_ms = (time.time() - t0) * 1000.0
                raw_text = response.choices[0].message.content
                return True, f"✅ 连接成功！响应耗时: {dt_ms:.1f}ms\n模型回复: {raw_text.strip()[:100]}", dt_ms

        except Exception as e:
            dt_ms = (time.time() - t0) * 1000.0
            return False, f"❌ 连接失败: {str(e)}", dt_ms
