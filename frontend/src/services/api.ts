import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// ============ AUTH TYPES ============
export interface UserRegister {
  email: string;
  password: string;
  full_name: string;
  region: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  region: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ============ HOUSEHOLD TYPES ============
export interface HouseholdCreate {
  name: string;
  address: string;
  region: string;
  num_people: number;
  num_rooms: number;
  has_ac: boolean;
  has_heater: boolean;
  has_ev: boolean;
  appliances: string[];
}

export interface Household extends HouseholdCreate {
  id: number;
  estimated_monthly_kwh: number;
  estimated_monthly_cost: number;
}

export interface HouseholdAnalytics {
  total_households: number;
  total_population: number;
  avg_consumption_kwh: number;
  peak_demand_mw: number;
  regions: Record<string, { households: number; population: number }>;
}

// ============ FORECAST TYPES ============
export interface ForecastResponse {
  forecasted_demand: number;
  confidence?: number;
  timestamp?: string;
}

export interface HourlyForecast {
  hour: number;
  temperature: number;
  predicted_demand: number;
  confidence?: number;
}

export interface Forecast24hResponse {
  forecasts: HourlyForecast[];
  base_temperature: number;
  total_energy_mwh?: number;
  peak_hour?: number;
  peak_demand?: number;
  generated_at?: string;
}

export interface AnalyticsResponse {
  avg_demand: number;
  max_demand: number;
  min_demand: number;
  peak_hour: number;
  low_hour: number;
  total_energy_24h?: number;
  estimated_cost_birr?: number;
}

// ============ AI TYPES ============
export interface AIInsight {
  category: string;
  message: string;
  severity: string;
  recommendation: string;
}

export interface AIAnalysisResponse {
  insights: AIInsight[];
  demand_trend: string;
  efficiency_score: number;
  recommendations: string[];
}

export interface RegionAnalytics {
  region: string;
  households: number;
  population: number;
  avg_demand_mw: number;
  peak_demand_mw: number;
}

export interface NationalAnalytics {
  total_households: number;
  total_population: number;
  total_demand_mw: number;
  regions: RegionAnalytics[];
  ai_insights: string[];
}

export interface WeeklyForecast {
  day: string;
  date: string;
  avg_demand: number;
  peak_demand: number;
  min_demand: number;
  total_energy_mwh: number;
}

// ============ REALTIME TYPES ============
export interface RealtimeStatus {
  timestamp: string;
  grid_status: string;
  current_demand_mw: number;
  current_generation_mw: number;
  total_capacity_mw: number;
  operational_capacity_mw: number;
  reserve_margin_percent: number;
  frequency_hz: number;
  voltage_levels: {
    "230kV": number;
    "132kV": number;
    "66kV": number;
  };
  load_factor: number;
  peak_today_mw: number;
  min_today_mw: number;
}

export interface PowerPlant {
  name: string;
  type: string;
  capacity_mw: number;
  current_output_mw: number;
  utilization_percent: number;
  location: string;
  status: string;
}

export interface RegionalData {
  region: string;
  current_demand_mw: number;
  peak_demand_mw: number;
  population: number;
  households: number;
  per_capita_kw: number;
  substations: string[];
}

export interface UploadResponse {
  message: string;
  records_processed: number;
}

// ============ AUTH API ============
export const register = async (data: UserRegister): Promise<TokenResponse> => {
  const res = await api.post("/auth/register", data);
  return res.data;
};

export const login = async (data: UserLogin): Promise<TokenResponse> => {
  const res = await api.post("/auth/login", data);
  return res.data;
};

export const logout = async (token: string): Promise<void> => {
  await api.post(`/auth/logout?token=${token}`);
};

// ============ HOUSEHOLD API ============
export const createHousehold = async (data: HouseholdCreate): Promise<Household> => {
  const res = await api.post("/households/", data);
  return res.data;
};

export const getHouseholds = async (): Promise<Household[]> => {
  const res = await api.get("/households/");
  return res.data;
};

export const getHouseholdAnalytics = async (): Promise<HouseholdAnalytics> => {
  const res = await api.get("/households/analytics/summary");
  return res.data;
};

// ============ FORECAST API ============
export const getForecast = async (): Promise<ForecastResponse> => {
  const res = await api.get("/forecast");
  return res.data;
};

export const postForecast = async (params: {
  temperature: number;
  hour: number;
  day_of_week: number;
  month: number;
}): Promise<ForecastResponse> => {
  const res = await api.post("/forecast", params);
  return res.data;
};

export const get24hForecast = async (baseTemp: number = 25): Promise<Forecast24hResponse> => {
  const res = await api.get(`/forecast/24h?base_temperature=${baseTemp}`);
  return res.data;
};

export const getAnalytics = async (): Promise<AnalyticsResponse> => {
  const res = await api.get("/analytics");
  return res.data;
};

// ============ AI API ============
export const getAIInsights = async (): Promise<AIAnalysisResponse> => {
  const res = await api.get("/ai/insights");
  return res.data;
};

export const getNationalAnalytics = async (): Promise<NationalAnalytics> => {
  const res = await api.get("/ai/national");
  return res.data;
};

export const getWeeklyForecast = async (): Promise<{ forecasts: WeeklyForecast[]; total_weekly_mwh: number; avg_daily_peak: number }> => {
  const res = await api.get("/ai/predict/weekly");
  return res.data;
};

// ============ REALTIME API ============
export const getRealtimeStatus = async (): Promise<RealtimeStatus> => {
  const res = await api.get("/realtime/status");
  return res.data;
};

export const getRealtimeSummary = async () => {
  const res = await api.get("/realtime/summary");
  return res.data;
};

export const getPowerPlants = async (): Promise<{ plants: PowerPlant[]; total_output_mw: number }> => {
  const res = await api.get("/realtime/power-plants");
  return res.data;
};

export const getRegionalDemand = async (): Promise<{ regions: RegionalData[]; total_demand_mw: number }> => {
  const res = await api.get("/realtime/regional");
  return res.data;
};

export const getWeatherImpact = async () => {
  const res = await api.get("/realtime/weather");
  return res.data;
};

export const getCurrentAlerts = async () => {
  const res = await api.get("/realtime/alerts");
  return res.data;
};

// ============ UPLOAD API ============
export const uploadData = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

// ============ CHATBOT API ============
export interface ChatMessage {
  message: string;
  user_id?: number;
}

export interface ChatResponse {
  response: string;
  timestamp: string;
  suggestions: string[];
}

export const sendChatMessage = async (message: string): Promise<ChatResponse> => {
  const res = await api.post("/chat/message", { message });
  return res.data;
};

export const getChatSuggestions = async () => {
  const res = await api.get("/chat/suggestions");
  return res.data;
};

export default api;
