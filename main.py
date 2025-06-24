import aiohttp
import asyncio
import logging
from typing import List, Dict, Optional
from bring_api import Bring
from bring_api.bring import BringItemOperation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Bring Shopping List API")

class BringAPI:
    def __init__(self, email: str, password: str):
        """Initialize the BringAPI with credentials.
        
        Args:
            email: Your Bring account email
            password: Your Bring account password
        """
        self.email = email
        self.password = password
        self.session = None
        self.bring = None
        self.lists = None

    async def connect(self):
        """Connect to the Bring API and login."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self.bring = Bring(self.session, self.email, self.password)
            await self.bring.login()
            response = await self.bring.load_lists()
            self.lists = response.lists  # Access the lists attribute directly

    async def close(self):
        """Close the API connection."""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_lists(self) -> List[Dict]:
        """Get all available shopping lists.
        
        Returns:
            List of shopping lists with their details
        """
        if not self.lists:
            await self.connect()
        return self.lists

    async def get_list_items(self, list_uuid: str) -> Dict:
        """Get all items from a specific shopping list.
        
        Args:
            list_uuid: UUID of the shopping list
            
        Returns:
            Dictionary containing the list items
        """
        if not self.bring:
            await self.connect()
        return await self.bring.get_list(list_uuid)

    async def add_item(self, list_uuid: str, item_name: str, specification: Optional[str] = None):
        """Add an item to a shopping list.
        
        Args:
            list_uuid: UUID of the shopping list
            item_name: Name of the item to add
            specification: Optional specification for the item
        """
        if not self.bring:
            await self.connect()
        await self.bring.save_item(list_uuid, item_name, specification)

    async def remove_item(self, list_uuid: str, item_name: str):
        """Remove an item from a shopping list.
        
        Args:
            list_uuid: UUID of the shopping list
            item_name: Name of the item to remove
        """
        if not self.bring:
            await self.connect()
        await self.bring.remove_item(list_uuid, item_name)

    async def complete_item(self, list_uuid: str, item_name: str):
        """Mark an item as completed in a shopping list.
        
        Args:
            list_uuid: UUID of the shopping list
            item_name: Name of the item to mark as completed
        """
        if not self.bring:
            await self.connect()
        await self.bring.complete_item(list_uuid, item_name)

class ItemCreate(BaseModel):
    item_name: str
    specification: Optional[str] = None

class ListResponse(BaseModel):
    listUuid: str
    name: str

# Globale API-Instanz
bring_api = BringAPI("<yourBringEMail>", "<yourBringPassword>")

@app.on_event("startup")
async def startup_event():
    """Verbinde zur Bring API beim Server-Start"""
    await bring_api.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Schließe die Verbindung beim Server-Shutdown"""
    await bring_api.close()

@app.get("/lists", response_model=List[ListResponse])
async def get_lists():
    """Hole alle verfügbaren Einkaufslisten"""
    try:
        lists = await bring_api.get_lists()
        return lists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lists/{list_uuid}/items")
async def get_list_items(list_uuid: str):
    """Hole alle Items einer spezifischen Liste"""
    try:
        items = await bring_api.get_list_items(list_uuid)
        # Versuche, das Objekt in ein Dictionary zu konvertieren
        if hasattr(items, "to_dict"):
            items_dict = items.to_dict()
        else:
            items_dict = dict(items) if hasattr(items, "__iter__") else vars(items)
        purchase_items = items_dict.get("items", {}).get("purchase", [])
        return {"items": {"purchase": purchase_items}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lists/{list_uuid}/items")
async def add_item(list_uuid: str, item: ItemCreate):
    """Füge ein Item zur Einkaufsliste hinzu"""
    try:
        await bring_api.add_item(list_uuid, item.item_name, item.specification)
        return {"message": f"Item {item.item_name} wurde erfolgreich hinzugefügt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/lists/{list_uuid}/items/{item_name}")
async def remove_item(list_uuid: str, item_name: str):
    """Entferne ein Item von der Einkaufsliste"""
    try:
        await bring_api.remove_item(list_uuid, item_name)
        return {"message": f"Item {item_name} wurde erfolgreich entfernt"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lists/{list_uuid}/items/{item_name}/complete")
async def complete_item(list_uuid: str, item_name: str):
    """Markiere ein Item als erledigt"""
    try:
        await bring_api.complete_item(list_uuid, item_name)
        return {"message": f"Item {item_name} wurde als erledigt markiert"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
