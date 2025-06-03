from app.main import app as fastapi_app
from mangum import Mangum

handler = Mangum(fastapi_app)
