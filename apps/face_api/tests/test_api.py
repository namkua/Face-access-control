def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "module": "Face API"}

def test_enroll_success(client, mock_face_service):
    """Test trường hợp đăng ký thành công"""
    # 1. Setup Mock: Giả lập hàm enroll_face trả về True
    mock_face_service.enroll_face.return_value = True

    # 2. Chuẩn bị dữ liệu
    payload = {"id": "NV001", "name": "Nguyen Van A"}
    files = {"file": ("avatar.jpg", b"fake_image_bytes", "image/jpeg")}

    # 3. Gọi API
    response = client.post("/enroll", data=payload, files=files)

    # 4. Kiểm tra kết quả
    assert response.status_code == 200
    # Khớp với format trong main.py: "Successfully enrolled {id} {name}"
    expected_msg = "Successfully enrolled NV001 Nguyen Van A"
    assert response.json()["message"] == expected_msg

def test_enroll_fail_no_face(client, mock_face_service):
    """Test trường hợp gửi ảnh không có mặt"""
    # 1. Setup Mock: Giả lập hàm enroll_face trả về False
    mock_face_service.enroll_face.return_value = False

    payload = {"id": "NV001", "name": "A"}
    files = {"file": ("no_face.jpg", b"fake_bytes", "image/jpeg")}

    response = client.post("/enroll", data=payload, files=files)

    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"] == "Could not detect face in image"

def test_predict_success(client, mock_face_service):
    """Test nhận diện đúng người"""
    # 1. Setup Mock: Giả lập hàm recognize trả về kết quả tốt
    mock_face_service.recognize.return_value = {
        "status": "success",
        "id": "NV001",
        "name": "Nguyen Van A",
        "distance": 0.4
    }

    files = {"file": ("capture.jpg", b"fake_bytes", "image/jpeg")}
    response = client.post("/predict", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "NV001"
    assert data["name"] == "Nguyen Van A"

def test_predict_unknown(client, mock_face_service):
    """Test người lạ"""
    # 1. Setup Mock: Giả lập hàm recognize trả về Unknown
    mock_face_service.recognize.return_value = {
        "status": "success",
        "id": "Unknown",
        "name": "Unknown",
        "distance": 1.2
    }

    files = {"file": ("stranger.jpg", b"fake_bytes", "image/jpeg")}
    response = client.post("/predict", files=files)

    assert response.status_code == 200
    assert response.json()["id"] == "Unknown"