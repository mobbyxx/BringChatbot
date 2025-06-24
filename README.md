**A simple Bring! Chatbot**

Just install the Python requirements.txt

Execute the main.py (dont forget to set your Email and Password)

Execute the n8n Workflow

## API Endpoints

### get list

```bash
GET /lists
```

return every list

**example-response:**
```json
[
  {
    "listUuid": "12345-abcde",
    "name": "Meine Einkaufsliste"
  }
]
```

### get items from list

```bash
GET /lists/{list_uuid}/items
```

returns items from list

### add item

```bash
POST /lists/{list_uuid}/items
```

adds item to list

**Request Body:**
```json
{
  "item_name": "Milch",
  "specification": "1 Liter"
}
```

### deletes items

```bash
DELETE /lists/{list_uuid}/items/{item_name}
```

deletes items from list

### mark item as complete (bought)

```bash
POST /lists/{list_uuid}/items/{item_name}/complete
```

## Examples

### Curl

1. Request List:
```bash
curl http://localhost:8000/lists
```

2. Add item:
```bash
curl -X POST http://localhost:8000/lists/{list_uuid}/items \
  -H "Content-Type: application/json" \
  -d '{"item_name": "Milk", "specification": "1 Liter"}'
```

3. Delete item:
```bash
curl -X DELETE http://localhost:8000/lists/{list_uuid}/items/Milk
```

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Listen abrufen
lists = requests.get(f"{BASE_URL}/lists").json()

# Item hinzufügen
list_uuid = lists[0]["listUuid"]
requests.post(
    f"{BASE_URL}/lists/{list_uuid}/items",
    json={"item_name": "Milk", "specification": "1 Liter"}
)

# Item als erledigt markieren
requests.post(f"{BASE_URL}/lists/{list_uuid}/items/Milk/complete")
```
