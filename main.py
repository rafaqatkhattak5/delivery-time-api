from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="Delivery Time Prediction API")

MODEL_PATH = "delivery_time_model.pkl"
model = joblib.load(MODEL_PATH)


class DeliveryInput(BaseModel):
    Order_Hour: int
    Day_of_Week: str
    Is_Weekend: int
    Is_Festival: int
    Weather: str
    Pickup_Zone: str
    Dropoff_Zone: str
    Vehicle_Type: str
    Rider_Experience_Years: float
    Rider_Rating: float
    Restaurant_Rating: float
    Cuisine_Type: str
    Order_Items: int
    Restaurant_Load: str
    Preparation_Time_Min: float
    Road_Distance_km: float
    Delivery_Distance_Category: str
    Traffic_Level: str
    Number_of_Signals: int
    Average_Speed_kmph: float
    Delivery_Priority: str


@app.get("/", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Delivery Time Predictor</title>
<style>
  body { font-family: sans-serif; max-width: 480px; margin: 20px auto; padding: 0 12px; }
  h2 { text-align: center; }
  label { display: block; margin-top: 10px; font-size: 14px; color: #333; }
  input, select { width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; font-size: 14px; }
  button { width: 100%; padding: 12px; margin-top: 18px; background: #ff4b4b; color: white; border: none; border-radius: 6px; font-size: 16px; }
  #result { margin-top: 18px; padding: 14px; background: #f0f2f6; border-radius: 6px; text-align: center; font-size: 18px; font-weight: bold; display: none; }
</style>
</head>
<body>
<h2>🛵 Delivery Time Predictor</h2>
<form id="f">
  <label>Order Hour (0-23)</label><input type="number" name="Order_Hour" value="14" min="0" max="23">
  <label>Day of Week</label>
  <select name="Day_of_Week">
    <option>Monday</option><option>Tuesday</option><option>Wednesday</option>
    <option selected>Thursday</option><option>Friday</option><option>Saturday</option><option>Sunday</option>
  </select>
  <label>Is Weekend?</label>
  <select name="Is_Weekend"><option value="0" selected>No</option><option value="1">Yes</option></select>
  <label>Is Festival?</label>
  <select name="Is_Festival"><option value="0" selected>No</option><option value="1">Yes</option></select>
  <label>Weather</label>
  <select name="Weather"><option>Clear</option><option>Cloudy</option><option>Fog</option><option>Rain</option><option>Storm</option></select>
  <label>Pickup Zone</label>
  <select name="Pickup_Zone"><option>CBD</option><option>Commercial</option><option>Industrial</option><option selected>Residential</option><option>Suburban</option></select>
  <label>Dropoff Zone</label>
  <select name="Dropoff_Zone"><option>CBD</option><option selected>Commercial</option><option>Industrial</option><option>Residential</option><option>Suburban</option></select>
  <label>Vehicle Type</label>
  <select name="Vehicle_Type"><option>Bicycle</option><option selected>Bike</option><option>Electric Scooter</option><option>Scooter</option></select>
  <label>Rider Experience (Years)</label><input type="number" step="0.1" name="Rider_Experience_Years" value="2.5">
  <label>Rider Rating (1-5)</label><input type="number" step="0.1" name="Rider_Rating" value="4.7">
  <label>Restaurant Rating (1-5)</label><input type="number" step="0.1" name="Restaurant_Rating" value="4.3">
  <label>Cuisine Type</label>
  <select name="Cuisine_Type"><option>Bakery</option><option selected>Biryani</option><option>Burger</option><option>Cafe</option><option>Chinese</option><option>Desserts</option><option>North Indian</option><option>Pizza</option><option>South Indian</option></select>
  <label>Order Items</label><input type="number" name="Order_Items" value="3">
  <label>Restaurant Load</label>
  <select name="Restaurant_Load"><option>High</option><option>Low</option><option selected>Medium</option></select>
  <label>Preparation Time (min)</label><input type="number" step="0.1" name="Preparation_Time_Min" value="15">
  <label>Road Distance (km)</label><input type="number" step="0.1" name="Road_Distance_km" value="4.2">
  <label>Delivery Distance Category</label>
  <select name="Delivery_Distance_Category"><option>Long</option><option selected>Medium</option><option>Short</option></select>
  <label>Traffic Level</label>
  <select name="Traffic_Level"><option selected>High</option><option>Low</option><option>Moderate</option><option>Severe</option></select>
  <label>Number of Signals</label><input type="number" name="Number_of_Signals" value="5">
  <label>Average Speed (km/h)</label><input type="number" step="0.1" name="Average_Speed_kmph" value="22">
  <label>Delivery Priority</label>
  <select name="Delivery_Priority"><option selected>Normal</option><option>Priority</option><option>VIP</option></select>

  <button type="submit">Predict Delivery Time</button>
</form>
<div id="result"></div>

<script>
document.getElementById('f').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = new FormData(e.target);
  const data = {};
  for (const [key, value] of form.entries()) {
    const numericFields = ["Order_Hour","Is_Weekend","Is_Festival","Rider_Experience_Years",
      "Rider_Rating","Restaurant_Rating","Order_Items","Preparation_Time_Min",
      "Road_Distance_km","Number_of_Signals","Average_Speed_kmph"];
    data[key] = numericFields.includes(key) ? Number(value) : value;
  }
  const resultBox = document.getElementById('result');
  resultBox.style.display = 'block';
  resultBox.textContent = 'Calculating...';
  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data)
    });
    const json = await res.json();
    if (res.ok) {
      resultBox.textContent = 'Estimated Delivery Time: ' + json.predicted_delivery_time_min + ' minutes';
    } else {
      resultBox.textContent = 'Error: ' + json.detail;
    }
  } catch (err) {
    resultBox.textContent = 'Error: ' + err;
  }
});
</script>
</body>
</html>
"""


@app.post("/predict")
def predict(data: DeliveryInput):
    try:
        input_df = pd.DataFrame([data.dict()])
        prediction = model.predict(input_df)[0]
        return {"predicted_delivery_time_min": round(float(prediction), 2)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
