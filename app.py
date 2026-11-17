import os
import json
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="BBIT E-Commerce Inventory Manager",
    description="Project 1: A persistent local inventory API for backend practice."
)

# File configuration for permanent storage
DATA_FILE = "inventory_data.json"

def load_inventory():
    """Helper function to load data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return [] # Return empty list if file doesn't exist yet
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_inventory(data):
    """Helper function to save data to the JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# 1. READ ALL ITEMS (GET)
@app.get("/items", tags=["Inventory Operations"])
def get_all_items():
    inventory = load_inventory()
    return {
        "total_products": len(inventory),
        "products": inventory
    }

# 2. READ SINGLE ITEM BY ID (GET)
@app.get("/items/{item_id}", tags=["Inventory Operations"])
def get_item_by_id(item_id: int):
    inventory = load_inventory()
    for item in inventory:
        if item["id"] == item_id:
            return {"found": True, "product_data": item}
    
    raise HTTPException(status_code=404, detail=f"Product with ID {item_id} not found.")

# 3. ADD NEW ITEM (POST)
@app.post("/items/add", tags=["Inventory Operations"])
def add_new_item(name: str, price: float, stock_size: int):
    if price <= 0 or stock_size < 0:
        raise HTTPException(status_code=400, detail="Price must be above 0 and stock cannot be negative.")
        
    inventory = load_inventory()
    
    # Auto-increment ID generation
    new_id = inventory[-1]["id"] + 1 if inventory else 1
    
    new_product = {
        "id": new_id,
        "name": name,
        "price": price,
        "stock": stock_size,
        "status": "In Stock" if stock_size > 0 else "Out of Stock"
    }
    
    inventory.append(new_product)
    save_inventory(inventory) # Write permanently to disk
    
    return {
        "message": f"Successfully added '{name}' to storage!",
        "added_item": new_product
    }

# 4. UPDATE STOCK LEVELS (PATCH)
@app.patch("/items/{item_id}/update-stock", tags=["Inventory Operations"])
def update_stock(item_id: int, items_added_or_removed: int):
    inventory = load_inventory()
    
    for item in inventory:
        if item["id"] == item_id:
            new_stock = item["stock"] + items_added_or_removed
            if new_stock < 0:
                raise HTTPException(status_code=400, detail="Operation failed. Stock cannot drop below 0.")
                
            item["stock"] = new_stock
            item["status"] = "In Stock" if new_stock > 0 else "Out of Stock"
            
            save_inventory(inventory)
            return {"message": "Stock updated successfully", "updated_product": item}
            
    raise HTTPException(status_code=404, detail=f"Product with ID {item_id} not found.")
