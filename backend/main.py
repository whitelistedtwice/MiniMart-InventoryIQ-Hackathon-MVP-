from fastapi import FastAPI

app = FastAPI(title="InventoryIQ API")


@app.get("/health")
def health():
    return {"status": "ok"}
