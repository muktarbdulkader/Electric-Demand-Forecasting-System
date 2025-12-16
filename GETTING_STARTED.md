# 🚀 Getting Started - Ethiopian Electric Utility Platform

## Quick Start (5 minutes)

### 1. Prerequisites
```bash
# Check Python version
python --version  # 3.8+

# Check Node version
node --version    # 16+

# Check npm version
npm --version     # 8+
```

### 2. Clone & Setup
```bash
# Clone repository
git clone <repo-url>
cd electric-demand-forecasting-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 4. Start Services
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 5. Access Platform
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  Dashboard | Forecast | Analytics | Real-time | Chat   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Routes: Forecast | Auth | Households | AI | Chat │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ ML Models: Linear Regression | Pattern-based    │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ File I/O
┌────────────────────▼────────────────────────────────────┐
│              Data Layer (CSV/Files)                      │
│  electricity_demand.csv | Trained Models | Backups     │
└─────────────────────────────────────────────────────────┘
```

## Core Features

### 1. Dashboard
- **Current Demand** - Real-time electricity demand
- **24-Hour Forecast** - Hourly predictions
- **Peak Demand** - Highest demand period
- **Statistics** - Min, max, average demand

**Access**: http://localhost:5173/

### 2. Forecast
- **Custom Predictions** - Predict with specific parameters
- **24-Hour Forecast** - Detailed hourly breakdown
- **Confidence Intervals** - Prediction uncertainty
- **Trend Analysis** - Demand trends

**Access**: http://localhost:5173/forecast

### 3. Analytics
- **Historical Data** - Past demand patterns
- **Peak Hours** - When demand is highest
- **Consumption Trends** - Demand patterns
- **Data Upload** - Upload your own data

**Access**: http://localhost:5173/analytics

### 4. Real-time Grid
- **Grid Status** - Current grid health
- **Power Plants** - Generation status
- **Regional Demand** - Demand by region
- **Voltage Levels** - Grid voltage monitoring

**Access**: http://localhost:5173/realtime

### 5. Households
- **Register Household** - Add your household
- **Consumption Estimate** - Predicted usage
- **Appliances** - Track appliances
- **Regional Data** - Regional statistics

**Access**: http://localhost:5173/households

### 6. AI Insights
- **Peak Alerts** - High demand warnings
- **Recommendations** - Energy saving tips
- **National Analytics** - Country-wide data
- **Weekly Forecast** - 7-day predictions

**Access**: http://localhost:5173/ai

### 7. AI Chatbot
- **Smart Assistant** - Ask questions
- **Intent Recognition** - Understands queries
- **Suggestions** - Quick action buttons
- **24/7 Available** - Always accessible

**Access**: Click 💬 button (bottom-right)

## API Endpoints

### Authentication
```bash
# Register
POST /auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "region": "Addis Ababa"
}

# Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Forecast
```bash
# Get current forecast
GET /forecast

# Get 24-hour forecast
GET /forecast/24h?base_temperature=25

# Get analytics
GET /analytics

# Upload data
POST /upload (multipart/form-data)
```

### Real-time
```bash
# Get grid status
GET /realtime/status

# Get power plants
GET /realtime/power-plants

# Get regional demand
GET /realtime/regional

# Get alerts
GET /realtime/alerts
```

### Chatbot
```bash
# Send message
POST /chat/message
{
  "message": "What's the current demand?"
}

# Get suggestions
GET /chat/suggestions
```

## Data Format

### Upload CSV Format
```csv
datetime,demand,temperature,hour,day_of_week,month,humidity,is_holiday,region
2024-02-01 00:00:00,2900,19,0,3,2,64,0,National
2024-02-01 01:00:00,2700,18,1,3,2,67,0,National
```

### Required Columns
- `demand` - Electricity demand in MW (required)

### Optional Columns
- `datetime` - Timestamp (auto-generated if missing)
- `temperature` - Temperature in Celsius
- `hour` - Hour of day (0-23)
- `day_of_week` - Day of week (0-6)
- `month` - Month (1-12)
- `humidity` - Humidity percentage
- `is_holiday` - Holiday flag (0/1)
- `region` - Region name

## Common Tasks

### 1. Upload Your Data
```bash
# Through UI
1. Go to Analytics page
2. Click "📁 Select CSV File"
3. Choose your CSV file
4. Wait for success message

# Through API
curl -X POST http://localhost:8000/upload \
  -F "file=@your_data.csv"
```

### 2. Get Forecast
```bash
# Through UI
1. Go to Dashboard or Forecast page
2. View 24-hour forecast
3. Check peak demand

# Through API
curl http://localhost:8000/forecast/24h
```

### 3. Check Real-time Status
```bash
# Through UI
1. Go to Real-time page
2. View grid status
3. Check power plants

# Through API
curl http://localhost:8000/realtime/status
```

### 4. Ask Chatbot
```bash
# Through UI
1. Click 💬 button
2. Type your question
3. Get instant response

# Example questions
- "What's the peak demand?"
- "Show 24-hour forecast"
- "Real-time grid status"
- "Help"
```

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep fastapi

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port 8000 is available
netstat -an | grep 8000
```

### Frontend Won't Start
```bash
# Check Node version
node --version

# Clear cache
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Check port 5173 is available
netstat -an | grep 5173
```

### API Connection Issues
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS is enabled
curl -H "Origin: http://localhost:5173" \
  http://localhost:8000/forecast

# Check firewall
# Allow ports 8000 and 5173
```

### Data Upload Issues
```bash
# Check CSV format
# Must have 'demand' column

# Check file size
# Should be < 10MB

# Check encoding
# Must be UTF-8

# Check for errors
# Look at backend logs
```

## Performance Tips

### Optimize Frontend
```bash
# Build for production
npm run build

# Analyze bundle
npm run build -- --analyze

# Enable caching
# Configure nginx for static files
```

### Optimize Backend
```bash
# Use production server
gunicorn app.main:app

# Enable caching
# Configure Redis

# Use database
# Switch from CSV to PostgreSQL
```

### Monitor Performance
```bash
# Check response time
curl -w "@curl-format.txt" http://localhost:8000/forecast

# Monitor memory
top -p $(pgrep -f uvicorn)

# Check logs
tail -f backend.log
```

## Next Steps

### 1. Explore Features
- [ ] Create account
- [ ] Upload sample data
- [ ] View forecasts
- [ ] Check real-time status
- [ ] Ask chatbot questions

### 2. Customize System
- [ ] Modify forecast models
- [ ] Add new regions
- [ ] Customize alerts
- [ ] Update chatbot responses

### 3. Deploy to Production
- [ ] Set up database (PostgreSQL)
- [ ] Configure Docker
- [ ] Deploy to cloud (AWS/GCP)
- [ ] Set up monitoring
- [ ] Configure backups

### 4. Advanced Features
- [ ] Implement LSTM models
- [ ] Add anomaly detection
- [ ] Enable renewable integration
- [ ] Set up automated reporting
- [ ] Create admin dashboard

## Documentation

- **PLATFORM_ARCHITECTURE.md** - Complete system design
- **IMPLEMENTATION_ROADMAP.md** - Development timeline
- **CHATBOT_GUIDE.md** - Chatbot documentation
- **UPLOAD_FEATURE.md** - Data upload guide
- **VERIFY_UPLOAD.md** - Upload verification
- **README.md** - Project overview

## Support

### Getting Help
1. Check documentation files
2. Review API documentation: http://localhost:8000/docs
3. Check backend logs
4. Check browser console (F12)
5. Ask chatbot for help

### Reporting Issues
1. Describe the problem
2. Include error messages
3. Provide steps to reproduce
4. Check logs for details

## Resources

### Learning
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- scikit-learn: https://scikit-learn.org/
- Chart.js: https://www.chartjs.org/

### Tools
- Postman: API testing
- VS Code: Code editor
- Git: Version control
- Docker: Containerization

## Quick Reference

### Keyboard Shortcuts
- `Ctrl+Shift+R` - Hard refresh frontend
- `F12` - Open browser console
- `Ctrl+K` - Search in VS Code
- `Ctrl+/` - Comment code

### Common Commands
```bash
# Start backend
uvicorn app.main:app --reload

# Start frontend
npm run dev

# Build frontend
npm run build

# Run tests
pytest tests/

# Format code
black backend/

# Lint code
flake8 backend/
```

### Useful URLs
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

**Ready to get started?** Follow the Quick Start section above! 🚀

**Questions?** Check the documentation or ask the AI chatbot! 🤖

**Last Updated**: December 15, 2025
