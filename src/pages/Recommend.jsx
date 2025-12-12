import React, { useState, useEffect } from 'react';
import axios from 'axios';

import './Dashboard.css';
import Select from "react-select";

const Recommend = () => {

  const [formData, setFormData] = useState({
    state: '',
    district: '',
    N: 90,
    P: 42,
    K: 43,
    pH: 6.5,
    temperature: '',
    humidity: '',
    rainfall: '',
    crop: ''
  });
  const altitudeMap = {
    "Karnataka": 700,
    "Kerala": 1000,
    "Tamil Nadu": 600,
    "Himachal Pradesh": 1800,
    "Jammu and Kashmir": 1600,
    "Maharashtra": 650,
    "Assam": 150,
    "Meghalaya": 1300,
    "Goa": 30
  };

  const terrainMap = {
    "Karnataka": "Plain",
    "Kerala": "Mountain",
    "Himachal Pradesh": "Hilly",
    "Jammu and Kashmir": "Mountain",
    "Assam": "Hilly",
    "Meghalaya": "Hilly",
    "Goa": "Coastal"
  };

  const [statesList, setStatesList] = useState([]);
  const [districtsList, setDistrictsList] = useState([]);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [error, setError] = useState('');

  // 🔹 FETCH STATES (INDIA ONLY)
  useEffect(() => {
    fetch("https://countriesnow.space/api/v0.1/countries/states")
      .then(res => res.json())
      .then(data => {
        const india = data.data.find(c => c.name === "India");

        const formatted = india.states.map(s => ({
          label: s.name,
          value: s.name
        }));

        setStatesList(formatted);
      });
  }, []);



  // 🔹 FETCH DISTRICTS WHEN STATE SELECTED
  const handleStateChange = (selectedState) => {
    setFormData({ ...formData, state: selectedState.label, district: "" });

    fetch("https://countriesnow.space/api/v0.1/countries/state/cities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        country: "India",
        state: selectedState.label
      })
    })
      .then(res => res.json())
      .then(data => {
        const formatted = data.data.map(d => ({
          label: d,
          value: d
        }));

        setDistrictsList(formatted);
      });
  };



  // 🔹 DISTRICT CHANGE
  const handleDistrictChange = (selectedDistrict) => {
    setFormData({ ...formData, district: selectedDistrict.value });
  };



  // 🔹 FETCH WEATHER
  const fetchWeather = async () => {
    if (!formData.district) {
      alert("Please select a district");
      return;
    }

    setWeatherLoading(true);

    try {
      const res = await axios.get(`http://localhost:5000/fetch_weather?district=${formData.district}`);
      const data = res.data;

      setFormData(prev => ({
        ...prev,
        temperature: data.temperature,
        humidity: data.humidity,
        rainfall: data.rainfall
      }));

      alert("Weather fetched successfully!");

    } catch (err) {
      alert("Failed to fetch weather");
    } finally {
      setWeatherLoading(false);
    }
  };


  // 🔹 ML PREDICTION
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult('');
    setError('');

    try {
      const payload = {
        region: formData.state,       // Use STATE, not district
        N: Number(formData.N),
        P: Number(formData.P),
        K: Number(formData.K),
        pH: Number(formData.pH),
        temperature: Number(formData.temperature),
        humidity: Number(formData.humidity),
        rainfall: Number(formData.rainfall),

        altitude: altitudeMap[formData.state] ?? 600,
        terrain: terrainMap[formData.state] ?? "Plain",

        ...(formData.crop && { crop: formData.crop })
      };


      const res = await axios.post("http://localhost:5000/predict", payload);
      setResult(res.data.result);

    } catch {
      setError("Prediction failed. Check backend.");
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="dashboard-container">


      <div className="content-wrapper" style={{ maxWidth: '1000px', margin: '0 auto' }}>

        <div className="form-section">
          <h2 style={{ color: '#2c3e50' }}>🌾 Dynamic Crop Recommendation</h2>
          <p className="subtitle">Get best crop advice based on live weather + soil.</p>

          <form onSubmit={handleSubmit}>

            {/* LOCATION */}
            <div className="section-header">📍 Location & Weather</div>
            <div className="form-grid">

              {/* STATE */}
              <div className="form-group">
                <label>State</label>
                <Select
                  options={statesList}
                  value={statesList.find(s => s.label === formData.state)}
                  onChange={handleStateChange}
                  placeholder="Search or Select State"
                  isSearchable
                />
              </div>

              {/* DISTRICT */}
              <div className="form-group">
                <label>District</label>
                <Select
                  options={districtsList}
                  value={districtsList.find(d => d.label === formData.district)}
                  onChange={handleDistrictChange}
                  placeholder={formData.state ? "Search or Select District" : "Select State first"}
                  isSearchable
                  isDisabled={!formData.state}
                />
              </div>

              {/* Weather Button */}
              <div className="form-group">
                <button type="button"
                  onClick={fetchWeather}
                  className="secondary-btn"
                  disabled={weatherLoading}>
                  {weatherLoading ? 'Fetching...' : '☁️ Fetch Live Weather'}
                </button>
              </div>
            </div>

            {/* Weather Inputs */}
            <div className="form-grid">
              <div className="form-group">
                <label>Temperature (°C)</label>
                <input type="number" value={formData.temperature}
                  onChange={(e) => setFormData({ ...formData, temperature: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Humidity (%)</label>
                <input type="number" value={formData.humidity}
                  onChange={(e) => setFormData({ ...formData, humidity: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Rainfall (mm)</label>
                <input type="number" value={formData.rainfall}
                  onChange={(e) => setFormData({ ...formData, rainfall: e.target.value })} />
              </div>
              <div className="form-group">
                <label>Crop (Optional)</label>
                <input type="text" value={formData.crop}
                  onChange={(e) => setFormData({ ...formData, crop: e.target.value })} />
              </div>
            </div>

            {/* SOIL DETAILS */}
            <div className="section-header">🧪 Soil Details</div>
            <div className="form-grid">
              <div className="form-group"><label>Nitrogen (N)</label>
                <input type="number" value={formData.N}
                  onChange={(e) => setFormData({ ...formData, N: e.target.value })} />
              </div>
              <div className="form-group"><label>Phosphorus (P)</label>
                <input type="number" value={formData.P}
                  onChange={(e) => setFormData({ ...formData, P: e.target.value })} />
              </div>
              <div className="form-group"><label>Potassium (K)</label>
                <input type="number" value={formData.K}
                  onChange={(e) => setFormData({ ...formData, K: e.target.value })} />
              </div>
              <div className="form-group"><label>pH Level</label>
                <input type="number" value={formData.pH}
                  onChange={(e) => setFormData({ ...formData, pH: e.target.value })} />
              </div>
            </div>

            <div className="form-actions">
              <button className="primary-btn" disabled={loading}>
                {loading ? 'Analyzing...' : '🔍 Predict Best Crop'}
              </button>
            </div>
          </form>

          {error && <div className="error-msg">{error}</div>}
        </div>


        {/* RESULT */}
        {result && (
          <div className="result-container">

            <h3 className="result-title">📊 Crop Suitability Result</h3>

            {/* STATUS */}
            <p className="result-line">
              {result.includes("NOT") ? (
                <span className="status-bad">❌ Not suitable here</span>
              ) : (
                <span className="status-good">✔️ Suitable crop</span>
              )}
            </p>

            {/* Extract values from result */}
            {(() => {
              const lines = result.split("\n");
              let mlConf = 0;
              let agro = 0;

              lines.forEach(line => {
                if (line.includes("ML confidence")) {
                  mlConf = Number(line.replace(/[^0-9.]/g, ""));
                }
                if (line.includes("Agro suitability")) {
                  agro = Number(line.replace(/[^0-9.]/g, ""));
                }
              });

              return (
                <>
                  {/* ML SCORE BAR */}
                  <div className="score-wrapper">
                    <div className="score-label">🧠 ML Confidence ({mlConf}%)</div>
                    <div className="score-bar">
                      <div className="score-fill"
                        style={{
                          width: `${mlConf}%`,
                          background: mlConf > 60 ? "#3cb371" : mlConf > 35 ? "#e5c100" : "#de4b4b"
                        }}>
                      </div>
                    </div>
                  </div>

                  {/* AGRO SCORE BAR */}
                  <div className="score-wrapper">
                    <div className="score-label">🌾 Agro Suitability ({agro}%)</div>
                    <div className="score-bar">
                      <div className="score-fill"
                        style={{
                          width: `${agro}%`,
                          background: agro > 60 ? "#3cb371" : agro > 35 ? "#e5c100" : "#de4b4b"
                        }}>
                      </div>
                    </div>
                  </div>
                </>
              );
            })()}

            {/* OTHER RAW TEXT LINES */}
            {result.split("\n").map((line, idx) =>
              (line.includes("confidence") || line.includes("suitability")) ? null : (
                <p key={idx} className="result-line">{line}</p>
              ))}

            {/* ALTERNATIVES */}

            {result.includes("Suggested Alternatives:") && (
              <div className="alt-container">
                <h4 className="alt-title">🌱 Suggested Alternatives</h4>

                {result
                  .split("Suggested Alternatives:")[1]
                  .replace(".", "")
                  .split(",")
                  .map((alt, i) => (
                    <div key={i} className="alt-item">
                      ✔️ {alt.trim()}
                    </div>
                  ))
                }
              </div>
            )}


          </div>
        )}

      </div>
    </div>
  );
};

export default Recommend;
