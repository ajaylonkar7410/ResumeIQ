import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
    SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'sample_resumes')
