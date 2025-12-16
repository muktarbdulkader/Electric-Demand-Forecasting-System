"""
AI Chatbot Route - Ethiopian Electric Utility
Provides intelligent responses about electricity demand, forecasts, and grid status
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

router = APIRouter(prefix="/chat", tags=["chatbot"])

class ChatMessage(BaseModel):
    message: str
    user_id: int = None

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    suggestions: list = []

class ChatBot:
    """Simple rule-based chatbot for electricity demand queries"""
    
    def __init__(self):
        self.knowledge_base = {
            "forecast": [
                "demand forecast", "predict demand", "next 24 hours", "peak demand",
                "electricity prediction", "load forecast", "demand prediction"
            ],
            "realtime": [
                "current demand", "grid status", "real-time", "current load",
                "power plants", "generation", "frequency", "voltage"
            ],
            "regions": [
                "addis ababa", "oromia", "amhara", "tigray", "snnpr",
                "somali", "afar", "benishangul", "gambela", "harari", "dire dawa"
            ],
            "analytics": [
                "analytics", "statistics", "average demand", "peak hour",
                "consumption", "energy usage", "demand pattern"
            ],
            "households": [
                "household", "consumption", "appliances", "usage",
                "residential", "home energy"
            ],
            "help": [
                "help", "how to", "guide", "tutorial", "what can you do",
                "features", "commands"
            ]
        }
    
    def get_intent(self, message: str) -> str:
        """Determine user intent from message"""
        msg_lower = message.lower()
        
        for intent, keywords in self.knowledge_base.items():
            for keyword in keywords:
                if keyword in msg_lower:
                    return intent
        
        return "general"
    
    def get_response(self, message: str) -> tuple:
        """Generate response based on message"""
        intent = self.get_intent(message)
        msg_lower = message.lower()
        
        if intent == "forecast":
            return self._forecast_response(msg_lower)
        elif intent == "realtime":
            return self._realtime_response(msg_lower)
        elif intent == "regions":
            return self._regions_response(msg_lower)
        elif intent == "analytics":
            return self._analytics_response(msg_lower)
        elif intent == "households":
            return self._households_response(msg_lower)
        elif intent == "help":
            return self._help_response()
        else:
            return self._general_response(message)
    
    def _forecast_response(self, msg: str) -> tuple:
        """Handle forecast queries"""
        suggestions = ["Show 24h forecast", "Peak demand today", "Forecast accuracy"]
        
        if "peak" in msg:
            response = "📈 Peak demand typically occurs between 18:00-21:00 (evening peak). "
            response += "Current peak is around 5,150 MW. Would you like to see the detailed 24-hour forecast?"
        elif "next" in msg or "tomorrow" in msg:
            response = "🔮 I can show you the forecast for the next 24 hours or 7 days. "
            response += "Go to the Forecast page to see detailed predictions with temperature impact analysis."
        else:
            response = "📊 I can help you with demand forecasting! "
            response += "Ask me about peak demand, next 24 hours, or forecast accuracy. "
            response += "Visit the Forecast page for detailed predictions."
        
        return response, suggestions
    
    def _realtime_response(self, msg: str) -> tuple:
        """Handle real-time grid queries"""
        suggestions = ["Current grid status", "Power plants", "Regional demand"]
        
        if "power plant" in msg or "generation" in msg:
            response = "🏭 Ethiopia has 13 major power plants: "
            response += "GERD (5,150 MW), Gilgel Gibe III (1,870 MW), and others. "
            response += "Check the Real-time page for live status of all plants."
        elif "frequency" in msg or "voltage" in msg:
            response = "⚡ Grid frequency should be around 50 Hz. "
            response += "Voltage levels: 230kV, 132kV, 66kV. "
            response += "See Real-time page for current values."
        elif "region" in msg:
            response = "🗺️ Demand varies by region. Addis Ababa has the highest demand. "
            response += "Check the Real-time page for regional breakdown."
        else:
            response = "📡 Real-time grid information available! "
            response += "Ask about power plants, frequency, voltage, or regional demand. "
            response += "Visit Real-time page for live updates."
        
        return response, suggestions
    
    def _regions_response(self, msg: str) -> tuple:
        """Handle regional queries"""
        suggestions = ["Addis Ababa demand", "Regional comparison", "Population served"]
        
        if "addis" in msg:
            response = "🏙️ Addis Ababa: ~1,200 MW average demand, 4.2M population, 850K households. "
            response += "Highest demand in Ethiopia."
        elif "oromia" in msg:
            response = "🌾 Oromia: ~800 MW average demand, 6M population, 1.2M households. "
            response += "Second largest region."
        else:
            response = "🗺️ Ethiopia has 11 regions with varying electricity demand. "
            response += "Addis Ababa leads with ~1,200 MW. "
            response += "Check Analytics for regional breakdown."
        
        return response, suggestions
    
    def _analytics_response(self, msg: str) -> tuple:
        """Handle analytics queries"""
        suggestions = ["Average demand", "Peak hours", "Consumption trends"]
        
        if "average" in msg or "mean" in msg:
            response = "📊 Average national demand: ~3,680 MW. "
            response += "Varies by hour and season. "
            response += "Check Analytics page for detailed statistics."
        elif "peak" in msg or "hour" in msg:
            response = "📈 Peak hours: 18:00-21:00 (evening peak). "
            response += "Minimum: 04:00-05:00 (night low). "
            response += "See Analytics for hourly breakdown."
        else:
            response = "📈 Analytics show demand patterns and trends. "
            response += "Ask about average demand, peak hours, or consumption. "
            response += "Visit Analytics page for charts and statistics."
        
        return response, suggestions
    
    def _households_response(self, msg: str) -> tuple:
        """Handle household queries"""
        suggestions = ["Add household", "Consumption estimate", "Appliances"]
        
        if "add" in msg or "create" in msg or "register" in msg:
            response = "🏠 You can register households in the Households page. "
            response += "Provide: name, address, region, people, rooms, appliances. "
            response += "System estimates monthly consumption."
        elif "consumption" in msg or "usage" in msg:
            response = "⚡ Consumption depends on appliances and usage patterns. "
            response += "AC, heater, EV charging increase demand significantly. "
            response += "Register your household to get personalized estimates."
        else:
            response = "🏠 Household management available! "
            response += "Register households, track consumption, get recommendations. "
            response += "Visit Households page to get started."
        
        return response, suggestions
    
    def _help_response(self) -> tuple:
        """Handle help requests"""
        suggestions = ["Dashboard", "Forecast", "Analytics", "Real-time"]
        
        response = "🤖 I'm your AI assistant for Ethiopian Electric Utility! Here's what I can help with:\n\n"
        response += "📊 **Dashboard** - Current demand overview\n"
        response += "🔮 **Forecast** - 24h and 7-day predictions\n"
        response += "📈 **Analytics** - Demand statistics and patterns\n"
        response += "📡 **Real-time** - Live grid status\n"
        response += "🏠 **Households** - Manage your consumption\n"
        response += "🤖 **AI Insights** - Smart recommendations\n\n"
        response += "Ask me about forecasts, grid status, regions, or anything electricity-related!"
        
        return response, suggestions
    
    def _general_response(self, message: str) -> tuple:
        """Handle general queries"""
        suggestions = ["Dashboard", "Forecast", "Real-time", "Help"]
        
        response = "🤖 I'm here to help with electricity demand forecasting! "
        response += "Ask me about:\n"
        response += "• Demand forecasts\n"
        response += "• Real-time grid status\n"
        response += "• Regional demand\n"
        response += "• Household consumption\n"
        response += "• Analytics and trends\n\n"
        response += "Or type 'help' for more information."
        
        return response, suggestions

# Initialize chatbot
chatbot = ChatBot()

@router.post("/message", response_model=ChatResponse)
async def chat(chat_msg: ChatMessage):
    """Send message to chatbot and get response"""
    try:
        if not chat_msg.message or len(chat_msg.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response, suggestions = chatbot.get_response(chat_msg.message)
        
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            suggestions=suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_suggestions():
    """Get chat suggestions"""
    return {
        "suggestions": [
            "What's the current demand?",
            "Show 24-hour forecast",
            "Peak demand today",
            "Real-time grid status",
            "Regional demand breakdown",
            "How do I add a household?",
            "Help"
        ]
    }
