from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from database import db, create_document, get_documents, get_document_by_id
from schemas import Product, ContactMessage, CartItem

app = FastAPI(title="Urban Wheel Pottery API", version="1.0.0")

# CORS to allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sample_products() -> List[dict]:
    return [
        {
            "name": "Terracotta Mug",
            "description": "Hand-thrown terracotta mug with matte finish.",
            "price": 28.0,
            "image": "https://images.unsplash.com/photo-1607301405391-027cb30d2e05?q=80&w=1200&auto=format&fit=crop",
            "type": "mug",
            "in_stock": True,
        },
        {
            "name": "Clay Bowl",
            "description": "Warm clay bowl for soups and salads.",
            "price": 36.0,
            "image": "https://images.unsplash.com/photo-1522770179533-24471fcdba45?q=80&w=1200&auto=format&fit=crop",
            "type": "bowl",
            "in_stock": True,
        },
        {
            "name": "Olive Plate",
            "description": "Muted olive glazed dinner plate.",
            "price": 24.0,
            "image": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?q=80&w=1200&auto=format&fit=crop",
            "type": "plate",
            "in_stock": True,
        },
        {
            "name": "Minimal Vase",
            "description": "Tall vase inspired by modern craftsmanship.",
            "price": 58.0,
            "image": "https://images.unsplash.com/photo-1556228453-efd1f4e3f7d5?q=80&w=1200&auto=format&fit=crop",
            "type": "vase",
            "in_stock": True,
        },
        {
            "name": "Beige Cup",
            "description": "Small cup with warm beige glaze.",
            "price": 18.0,
            "image": "https://images.unsplash.com/photo-1563205570-03bfb1c006a1?q=80&w=1200&auto=format&fit=crop",
            "type": "mug",
            "in_stock": True,
        },
        {
            "name": "Textured Bowl",
            "description": "Hand-textured bowl, perfect for noodles.",
            "price": 42.0,
            "image": "https://images.unsplash.com/photo-1543168256-418811576931?q=80&w=1200&auto=format&fit=crop",
            "type": "bowl",
            "in_stock": True,
        },
    ]


@app.get("/test")
def test_connection():
    try:
        db.list_collection_names()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# Seed sample products if collection empty, ignore errors in serverless envs
@app.on_event("startup")
def seed_products():
    try:
        if db["product"].count_documents({}) == 0:
            for s in sample_products():
                db["product"].insert_one(s)
    except Exception:
        # DB might be unavailable; continue without seeding
        pass


@app.get("/products", response_model=List[Product])
def list_products(type: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    q: dict = {}
    if type:
        q["type"] = type
    if min_price is not None or max_price is not None:
        price_q = {}
        if min_price is not None:
            price_q["$gte"] = float(min_price)
        if max_price is not None:
            price_q["$lte"] = float(max_price)
        q["price"] = price_q

    try:
        docs = get_documents("product", q, limit=100)
        result: List[Product] = [Product(**{k: d[k] for k in ["name","description","price","image","type","in_stock"]}) for d in docs]
        if result:
            return result
    except Exception:
        pass

    # Fallback to in-process samples if DB not reachable
    fallback = sample_products()
    # Filter fallback according to query
    if type:
        fallback = [p for p in fallback if p["type"] == type]
    if min_price is not None:
        fallback = [p for p in fallback if p["price"] >= float(min_price)]
    if max_price is not None:
        fallback = [p for p in fallback if p["price"] <= float(max_price)]
    return [Product(**p) for p in fallback]


@app.get("/products/{product_id}")
def get_product(product_id: str):
    try:
        doc = get_document_by_id("product", product_id)
        if not doc:
            raise HTTPException(404, "Product not found")
        return doc
    except Exception:
        # Fallback search by name in samples
        for p in sample_products():
            if p["name"].lower().replace(" ", "-") == product_id.lower():
                return p
        raise HTTPException(404, "Product not found")


@app.post("/contact")
def submit_contact(msg: ContactMessage):
    try:
        saved = create_document("contactmessage", msg.model_dump())
        return {"success": True, "id": saved.get("id")}
    except Exception:
        # Accept the message even if DB is unavailable
        return {"success": True}


@app.post("/cart/add")
def add_to_cart(item: CartItem):
    try:
        product = get_document_by_id("product", item.product_id)
        if not product:
            raise HTTPException(404, "Product not found")
        return {"success": True, "item": {"product": product, "quantity": item.quantity}}
    except Exception:
        return {"success": True, "item": {"product_id": item.product_id, "quantity": item.quantity}}
