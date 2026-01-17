from fastapi import FastAPI, UploadFile, File, Form
from src.services.recognition import FaceRecognitionService
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
import os
app = FastAPI(title="Face Access Control API")

# --- 1. Setup Prometheus ---
Instrumentator().instrument(app).expose(app)

# --- 2. Setup Jaeger (OpenTelemetry) ---
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"

if ENABLE_TRACING:
    # Lấy host từ biến môi trường (mặc định localhost nếu chạy local main.py)
    JAEGER_HOST = os.getenv("JAEGER_HOST", "localhost")
    
    resource = Resource(attributes={"service.name": "face-api-service"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    print(f"--> Tracing Enabled. Connecting to Jaeger at {JAEGER_HOST}:4317")
    
    otlp_exporter = OTLPSpanExporter(endpoint=f"http://{JAEGER_HOST}:4317", insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    FastAPIInstrumentor.instrument_app(app)
else:
    print("--> Tracing Disabled (Test Environment)")

# Tự động trace mọi request vào FastAPI
FastAPIInstrumentor.instrument_app(app)
# Khởi tạo service AI 1 lần duy nhất khi app start
face_service = FaceRecognitionService()

@app.get("/")
def health_check():
    return {"status": "healthy", "module": "Face API"}

@app.post("/enroll")
async def enroll_user(id: str = Form(...) ,name: str = Form(...), file: UploadFile = File(...)):
    """API đăng ký nhân viên mới"""
    success = face_service.enroll_face(id, name, file.file)
    if success:
        return {"message": f"Successfully enrolled {id} {name}"}
    return {"error": "Could not detect face in image"}

@app.post("/predict")
async def predict_user(file: UploadFile = File(...)):
    """API nhận diện (Check-in)"""
    result = face_service.recognize(file.file)
    return result
