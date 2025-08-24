import uvicorn
from litestar import Litestar, get


@get("/")
async def health() -> str:
    return "OK"


app = Litestar([health])

if __name__ == "__main__":
    uvicorn.run("main:app")
