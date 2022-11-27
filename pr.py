from fastapi import APIRouter

HH = APIRouter()

@HH.get("/gg")
def gg():
    return "ggreturn"