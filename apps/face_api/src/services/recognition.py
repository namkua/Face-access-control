import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image
import numpy as np
import os

class FaceRecognitionService:
    def __init__(self):
        # Kiểm tra xem máy có GPU không, nếu không dùng CPU
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print(f"Running on device: {self.device}")

        # MTCNN dùng để cắt khuôn mặt từ ảnh (detect face)
        self.mtcnn = MTCNN(image_size=160, margin=0, keep_all=False, device=self.device)
        
        # InceptionResnetV1 là model trích xuất đặc trưng (pretrained trên vggface2)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        
        # Database tạm thời (lưu trong RAM cho tuần 1)
        # Cấu trúc: {"id" : { "name" : name , "embedding" : embedding}}
        self.known_embeddings = {}

    def img_to_embedding(self, image_file):
        """Chuyển file ảnh upload thành vector"""
        img = Image.open(image_file)
        # Cắt mặt & tiền xử lý
        img_cropped = self.mtcnn(img)
        
        if img_cropped is not None:
            # Chuyển sang vector 512 chiều
            img_embedding = self.resnet(img_cropped.unsqueeze(0).to(self.device))
            return img_embedding.detach().cpu()
        return None

    def enroll_face(self, id : str, name: str, image_file):
        """Đăng ký người mới vào hệ thống tạm"""
        embedding = self.img_to_embedding(image_file)
        if embedding is not None:
            self.known_embeddings[id] = { "name" : name, "embedding" : embedding}
            return True
        return False

    def recognize(self, image_file, threshold=0.8):
        """So sánh ảnh input với database"""
        current_embedding = self.img_to_embedding(image_file)
        
        if current_embedding is None:
            return {"status": "error", "message": "No face detected"}

        best_match_name = "Unknown"
        best_match_id = "Unknown"
        min_dist = float('inf')

        for id, data in self.known_embeddings.items():
            name = data["name"]
            embedding = data["embedding"]
            dist = (current_embedding-embedding).norm().item()
            if dist < min_dist:
                min_dist = dist
                best_match_name = name
                best_match_id = id
                

        if min_dist < threshold:
            return {"status": "success", "id": best_match_id , "name": best_match_name, "distance": min_dist}
        else:
            return {"status": "success","id": "Unknown" , "name": "Unknown", "distance": min_dist}