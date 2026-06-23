from fastapi.templating import Jinja2Templates
import pathlib

templates = Jinja2Templates(
    directory=str(pathlib.Path(__file__).resolve().parent / "templates")
)
