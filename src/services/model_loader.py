# services/model_loader.py
import torch
import json
from pathlib import Path
from typing import Dict, Any
from .recommendation_model import TwoTowerModel

class ModelLoader:
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def load_model(self) -> Dict[str, Any]:
        """Загружает модель и словари"""
        model_path = self.model_dir / "recsys_model.pth"
        stack_vocab_path = self.model_dir / "stack_vocab.json"
        roles_vocab_path = self.model_dir / "roles_vocab.json"
        print(f"Looking for model files in: {self.model_dir}")
        print(f"Checking: {model_path}")
        print(f"Checking: {stack_vocab_path}")
        print(f"Checking: {roles_vocab_path}")

        if not all([model_path.exists(), stack_vocab_path.exists(), roles_vocab_path.exists()]):
            raise FileNotFoundError("Не все файлы модели найдены")
        
        with open(stack_vocab_path, 'r') as f:
            stack_vocab = json.load(f)
            
        with open(roles_vocab_path, 'r') as f:
            roles_vocab = json.load(f)
        

        student_dim = len(stack_vocab) + len(roles_vocab)
        project_dim = student_dim + 384 
        
        model = TwoTowerModel(student_dim, project_dim).to(self.device)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        
        return {
            "model": model,
            "stack_vocab": stack_vocab,
            "roles_vocab": roles_vocab,
            "device": self.device
        }