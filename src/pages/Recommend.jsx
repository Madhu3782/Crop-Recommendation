import React, { useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const Recommend = () => {

    const [formData, setFormData] = useState({
        state: 'Karnataka',
        district: 'Davanagere',
        N: 90,
        P: 42,
        K: 43,
        pH: 6.5,
        temperature: '',
        humidity: '',
        rainfall: '',
        crop: ''
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [weatherLoading, setWeatherLoading] = useState(false);
    const [error, setError] = useState('');

    const states = ['Karnataka', 'Punjab', 'Maharashtra', 'Madhya Pradesh', 'Uttar Pradesh'];

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // Fetch Live Weather
    const fetchWeather = async () => {
        if (!formData.district) {
            alert("Please enter a district");
            return;
        }

        setWeatherLoading(true);
        try {
            const res = await axios.get(`http://localhost:5000/fetch_weather?state=${formData.state}&district=${formData.district}`);
            const data = res.data;

            setFormData(prev => ({
                ...prev,
                temperature: data.temperature,
                humidity: data.humidity,
                rainfall: data.rainfall
            }));

            alert(`Weather fetched!\nTemp: ${data.temperature}°C`);
        } catch (err) {
            alert("Failed to fetch weather");
        } finally {
            setWeatherLoading(false);
        }
    };

    // Backend ML Predict
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult('');
        setError('');

        if (!formData.temperature || !formData.rainfall || !formData.humidity) {
            setError("Please enter or fetch weather values");
            setLoading(false);
            return;
        }

        try {
            const payload = {
                region: formData.district,
                N: formData.N,
                P: formData.P,
                K: formData.K,
                pH: formData.pH,
                temperature: formData.temperature,
                humidity: formData.humidity,
                rainfall: formData.rainfall,
                ...(formData.crop && { crop: formData.crop })
            };

            const res = await axios.post('http://localhost:5000/predict', payload);
            setResult(res.data.result || "No response from backend");

        } catch (err) {
            setError("Prediction failed, check backend");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />

            <div className="content-wrapper" style={{ maxWidth: '1000px', margin: '0 auto' }}>

                <div className="form-section">
                    <h2 style={{ color: '#2c3e50' }}>🌾 Dynamic Crop Recommendation</h2>
                    <p className="subtitle">Get best crop advice based on live weather + soil.</p>

                    <form onSubmit={handleSubmit}>

                        {/* LOCATION */}
                        <div className="section-header">📍 Location & Weather</div>
                        <div className="form-grid">
                            <div className="form-group">
                                <label>State</label>
                                <select name="state" value={formData.state} onChange={handleChange}>
                                    {states.map(s => <option key={s}>{s}</option>)}
                                </select>
                            </div>

                            <div className="form-group">
                                <label>District / City</label>
                                <input type="text" name="district" value={formData.district} onChange={handleChange} />
                            </div>

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
                                <input type="number" name="temperature"
                                    value={formData.temperature} onChange={handleChange} step="0.1" />
                            </div>
                            <div className="form-group">
                                <label>Humidity (%)</label>
                                <input type="number" name="humidity"
                                    value={formData.humidity} onChange={handleChange} step="0.1" />
                            </div>
                            <div className="form-group">
                                <label>Rainfall (mm)</label>
                                <input type="number" name="rainfall"
                                    value={formData.rainfall} onChange={handleChange} step="0.1" />
                            </div>
                        </div>

                        {/* SOIL NUTRIENTS */}
                        <div className="section-header" style={{ marginTop: '20px' }}>🧪 Soil Details</div>
                        <div className="form-grid">
                            <div className="form-group"><label>Nitrogen (N)</label>
                                <input type="number" name="N" value={formData.N} onChange={handleChange} />
                            </div>
                            <div className="form-group"><label>Phosphorus (P)</label>
                                <input type="number" name="P" value={formData.P} onChange={handleChange} />
                            </div>
                            <div className="form-group"><label>Potassium (K)</label>
                                <input type="number" name="K" value={formData.K} onChange={handleChange} />
                            </div>
                            <div className="form-group"><label>pH Level</label>
                                <input type="number" name="pH" value={formData.pH} onChange={handleChange} />
                            </div>
                            <div className="form-group"><label>Crop (optional)</label>
                                <input type="text" name="crop" value={formData.crop} onChange={handleChange} placeholder="e.g. Rice" />
                            </div>
                        </div>

                        <div className="form-actions" style={{ marginTop: '25px' }}>
                            <button className="primary-btn" disabled={loading}>
                                {loading ? 'Analyzing...' : '🔍 Predict Best Crop'}
                            </button>
                        </div>
                    </form>

                    {error && <div className="error-msg">{error}</div>}
                </div>


                {/* RESULT DISPLAY */}
                {result && (
                    <div className="results-section"
                        style={{ marginTop: '30px', padding: '20px',
                            borderRadius: '8px', background: '#e8f5e9',
                            border: '1px solid #c8e6c9' }}>

                        <h3 style={{ color: '#2e7d32' }}>📋 Crop Suitability Result</h3>

                        <pre style={{ whiteSpace: 'pre-line',
                            marginTop: '15px',
                            fontSize: '1.15em',
                            color: '#333' }}>
{result}
                        </pre>
                    </div>
                )}

            </div>
        </div>
    );
};

export default Recommend;
