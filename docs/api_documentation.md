# Electric Demand Forecasting API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
```
GET /health
```
Returns API health status.

**Response:**
```json
{ "status": "healthy" }
```

---

### Get Current Forecast
```
GET /forecast
```
Returns forecasted demand for current hour with default parameters.

**Response:**
```json
{
  "forecasted_demand": 5432.50,
  "timestamp": "2024-01-15T14:30:00"
}
```

---

### Predict Demand (Custom Parameters)
```
POST /forecast
```
Predict demand with custom input parameters.

**Request Body:**
```json
{
  "temperature": 15.0,
  "hour": 14,
  "day_of_week": 2,
  "month": 6
}
```

| Field | Type | Description |
|-------|------|-------------|
| temperature | float | Temperature in Celsius |
| hour | int | Hour of day (0-23) |
| day_of_week | int | Day of week (0=Monday, 6=Sunday) |
| month | int | Month (1-12) |

**Response:**
```json
{
  "forecasted_demand": 6200.75,
  "timestamp": "2024-01-15T14:30:00"
}
```

---

### Get 24-Hour Forecast
```
GET /forecast/24h?base_temperature=15
```
Returns demand forecast for the next 24 hours.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| base_temperature | float | 15.0 | Base temperature for forecast |

**Response:**
```json
{
  "forecasts": [
    { "hour": 0, "temperature": 13.0, "predicted_demand": 4500.00 },
    { "hour": 1, "temperature": 12.0, "predicted_demand": 4200.00 }
  ],
  "base_temperature": 15.0,
  "generated_at": "2024-01-15T14:30:00"
}
```

---

### Get Analytics
```
GET /analytics
```
Returns demand analytics based on 24-hour forecast.

**Response:**
```json
{
  "avg_demand": 5800.50,
  "max_demand": 7600.00,
  "min_demand": 3600.00,
  "peak_hour": 14,
  "low_hour": 4
}
```

---

### Upload Data
```
POST /upload
```
Upload CSV file with electricity demand data.

**Request:** `multipart/form-data` with file field

**Response:**
```json
{
  "message": "File uploaded successfully",
  "records_processed": 1000
}
```

---

## Error Responses

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "hour"],
      "msg": "ensure this value is less than or equal to 23",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Server Error (500):**
```json
{
  "detail": "Error message"
}
```

---

## Running the API

```bash
cd backend
pip install -r requirements.txt
python -m ml.train  # Train model first
uvicorn app.main:app --reload
```
