import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

# Thêm đường dẫn để Python tìm thấy code trong apps/face_api
sys.path.append(os.path.abspath("apps/face_api"))

# Import app từ src.main (Lưu ý đường dẫn import phải khớp với cấu trúc folder)
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_face_service():
    """
    Mock service AI để bypass việc load model nặng
    """
    with patch("src.main.face_service") as mock:
        yield mock


        