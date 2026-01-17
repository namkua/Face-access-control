pipeline {
    agent any
    
    environment {
        // --- CẤU HÌNH CỦA BẠN (SỬA LẠI CHO ĐÚNG) ---
        // Thay 'your_dockerhub_username' bằng tên tài khoản Docker Hub của bạn
        DOCKER_IMAGE = 'namkua/face-access-control'
        
        // Đây là ID của credential bạn phải tạo trong Jenkins (xem hướng dẫn dưới)
        DOCKER_CREDENTIALS_ID = 'dockerhub'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                script {
                    echo '--- Building Test Image ---'
                    // Build image tại chỗ để có môi trường chạy test
                    sh 'docker build -t face-api-test -f apps/face_api/Dockerfile .'
                    
                    echo '--- Running Pytest ---'
                    // Chạy test bên trong container
                    // Lưu ý: set PYTHONPATH để tìm thấy module src
                    sh 'docker run --rm -e PYTHONPATH=/app face-api-test pytest apps/face_api/tests/test_api.py'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo '--- Building Production Image ---'
                    // Build image với tag latest và tag theo số Build Jenkins
                    sh "docker build -t ${DOCKER_IMAGE}:latest -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."

                    echo '--- Pushing to Docker Hub ---'
                    // Sử dụng plugin credentials của Jenkins để đăng nhập an toàn
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                        sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    }
                }
            }
        }
    }

    post {
        always {
            echo '--- Cleaning up ---'
            // Xóa image local để tránh đầy ổ cứng server
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "docker rmi face-api-test || true"
        }
    }
}