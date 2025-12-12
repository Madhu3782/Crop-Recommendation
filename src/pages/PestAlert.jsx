import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './PestAlert.css';

const PestAlert = () => {
    const [formData, setFormData] = useState({
        crop: 'Wheat',
        region: 'Punjab',
        temperature: '',
        humidity: '',
        rainfall: ''
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [weatherLoading, setWeatherLoading] = useState(false);

    // Lists
    const crops = ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Tomato', 'Potato'];
    const regions = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka'];

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const fetchWeather = async () => {
        if (!formData.region) return alert("Select a region first (using region as district proxy)");
        setWeatherLoading(true);
        try {
            // In a real app, map region to district properly. Using region name directly.
            const res = await axios.get(`http://localhost:5000/fetch_weather?district=${formData.region}`);
            setFormData({
                ...formData,
                temperature: res.data.temperature,
                humidity: res.data.humidity,
                rainfall: res.data.rainfall
            });
        } catch (err) {
            alert("Could not fetch weather. Please enter manually.");
        } finally {
            setWeatherLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await axios.post('http://localhost:5000/predict_pest_risk', formData);
            setResult(res.data);
        } catch (err) {
            alert("Prediction failed. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    // Prepare chart data
    const chartData = result ? result.next_7_days.map((val, idx) => ({
        day: `Day ${idx + 1}`,
        risk: val
    })) : [];

    return (
        <div className="pest-alert-container">
            <div className="pest-alert-header">
                <h1>🚨 Pest Attack Early Warning System</h1>
                <p>AI-powered risk assessment for the next 7 days.</p>
            </div>

            <div className="pest-content">
                {/* FORM CARD */}
                <div className="form-card">
                    <form onSubmit={handleSubmit}>
                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Crop</label>
                            <select
                                name="crop"
                                value={formData.crop}
                                onChange={handleChange}
                                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
                            >
                                {crops.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Region</label>
                            <select
                                name="region"
                                value={formData.region}
                                onChange={handleChange}
                                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
                            >
                                {regions.map(r => <option key={r} value={r}>{r}</option>)}
                            </select>
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Temperature (°C)</label>
                            <input
                                type="number"
                                name="temperature"
                                value={formData.temperature}
                                onChange={handleChange}
                                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
                                required
                            />
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Humidity (%)</label>
                            <input
                                type="number"
                                name="humidity"
                                value={formData.humidity}
                                onChange={handleChange}
                                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
                                required
                            />
                        </div>

                        <div style={{ marginBottom: '15px' }}>
                            <label style={{ display: 'block', marginBottom: '5px' }}>Rainfall (mm)</label>
                            <input
                                type="number"
                                name="rainfall"
                                value={formData.rainfall}
                                onChange={handleChange}
                                style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd' }}
                                required
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button
                                type="button"
                                onClick={fetchWeather}
                                style={{ flex: 1, padding: '10px', border: '1px solid #4CAF50', color: '#4CAF50', background: 'white', borderRadius: '6px', cursor: 'pointer' }}
                            >
                                {weatherLoading ? 'Fetching...' : 'Fetch Weather'}
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                style={{ flex: 1, padding: '10px', border: 'none', color: 'white', background: '#e74c3c', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
                            >
                                {loading ? 'Analyzing...' : 'Predict Risk'}
                            </button>
                        </div>
                    </form>
                </div>

                {/* RESULT CARD */}
                {result && (
                    <div className="result-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <span className={`risk-badge risk-${result.risk_level.toLowerCase()}`}>
                                    {result.risk_level} Risk ({result.risk_score}%)
                                </span>
                                <h2 className="pest-name">🐛 Likely Pest: {result.pest_name}</h2>
                            </div>
                        </div>

                        <div className="recommendation-box">
                            <h3>🛡️ Preventive Action</h3>
                            <p>Recommended to spray pesticides/neem oil on <strong>Day {result.recommended_spray_day}</strong> (Predicted Peak Risk).</p>
                        </div>

                        <div className="chart-section">
                            <h3>📅 7-Day Risk Forecast</h3>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="day" />
                                    <YAxis domain={[0, 100]} />
                                    <Tooltip />
                                    <Line type="monotone" dataKey="risk" stroke="#e74c3c" strokeWidth={3} dot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PestAlert;
