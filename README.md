# Solar Equipment Inventory & Quotation System

A REST API service for managing solar equipment inventory and generating quotations for solar installation projects.

## Overview

This system allows solar equipment suppliers and installers to:
- Manage their inventory of solar equipment (panels, inverters, mounting structures, etc.)
- Generate and retrieve quotations based on available inventory
- Store company information for quotation purposes

## API Endpoints

### Inventory Management

#### Get Inventory
```
GET /api/inventory/
```
Returns the complete inventory associated with the authenticated user.

#### Update Inventory
```
POST /api/inventory/?user_id={user_id}
```
Updates the inventory for a specific user. Requires a JSON payload with inventory categories and items.

Example payload:
```json
{
  "SolarPanels": [
    ["SPR-X22-370", "300", "100"],
    ["NeON R", "300", "100"],
    ["HiKu CS3W-415", "300", "100"]
  ],
  "Inverters": [
    ["SMA Sunny Boy 7.7-US", "50", "7700"],
    ["Fronius Primo 6.0-1", "30", "6000"],
    ["Enphase IQ7+", "100", "295"]
  ],
  "MountingStructures": [
    ["IronRidge XR100", "600", "333"],
    ["UniRac SolarMount", "150", "44"]
  ],
  "BOSComponents": [
    ["10AWG PV Wire", "5000", "555"],
    ["MC4 Connectors", "400", "66"],
    ["Junction Boxes", "100", "55"]
  ],
  "ProtectionEquipment": [
    ["DC Disconnect", "84", "55"],
    ["AC Disconnect", "80", "55"],
    ["Surge Protector", "100", "66"]
  ],
  "EarthingSystems": [
    ["Ground Rod Kit", "140", "22"],
    ["Grounding Lugs", "300", "2"]
  ],
  "NetMetering": [
    ["Bidirectional Meter", "75", "44"]
  ]
}
```

### User Information

#### Add/Update User Information
```
POST /api/add_user_info
```
Updates company information for the authenticated user.

Example payload:
```json
{
  "gstin": "29AADCB2230M1ZT",
  "phone": "9876543210",
  "company_name": "Solar Solutions Inc.",
  "company_address": "123 Sun Street, Solar City"
}
```

### Quotations

#### Get Quotations
```
GET /api/inventory//quotations
```
Retrieves all quotations associated with the user's inventory along with company information.

## Data Model

### Inventory
- **_id**: MongoDB ObjectId
- **user_id**: Email or unique identifier
- **SolarPanels**: Array of [model_name, price, profit]
- **Inverters**: Array of [model_name, price, profit]
- **MountingStructures**: Array of [model_name, price, profit]
- **BOSComponents**: Array of [model_name, price, profit]
- **ProtectionEquipment**: Array of [model_name, price, profit]
- **EarthingSystems**: Array of [model_name, price, profit]
- **NetMetering**: Array of [model_name, price, profit]
- **created_at**: Timestamp
- **updated_at**: Timestamp

### Quotation
- **user_id**: Email or unique identifier
- **inventory_id**: Reference to inventory
- **quotation**: Selected components
  - **SolarPanel**: Selected panel model
  - **Inverter**: Selected inverter model
  - **MountingStructure**: Selected mounting structure
  - **EarthingSystem**: Selected earthing system
  - **BOSComponents**: Array of selected BOS components
  - **ProtectionEquipment**: Array of selected protection equipment
  - **NetMetering**: Array of selected net metering equipment
- **total_cost**: Calculated total cost
- **total_profit**: Calculated total profit

### User Info
- **gstin**: GST Identification Number
- **phone**: Contact phone number
- **company_name**: Name of the company
- **company_address**: Address of the company

## Installation

1. Clone the repository
2. Install dependencies
   ```
   pip install -r requirements.txt
   ```
3. Configure MongoDB connection in config.py
4. Start the server
   ```
   python app.py
   ```

## Usage

1. First, add company information using the `/api/add_user_info` endpoint.
2. Add inventory using the `/api/inventory/?user_id={user_id}` endpoint.
3. Get quotations using the `/api/inventory//quotations` endpoint.

## Authentication

The API uses token-based authentication. Include the authentication token in the request header:
```
Authorization: Bearer {token}
```

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Development

### Requirements
- Python 3.8+
- MongoDB
- FastAPI

### Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET`: Secret for JWT token generation
- `PORT`: Port to run the server (default: 8000)

## License

[MIT License](LICENSE)
