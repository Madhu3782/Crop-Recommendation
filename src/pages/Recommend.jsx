import React, { useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const Recommend = () => {
    // State for form fields
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
        crop: '' // optional crop for validation mode
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [weatherLoading, setWeatherLoading] = useState(false);
    const [error, setError] = useState('');

    // Pre-defined lists (can be expanded)
    const states = ['Karnataka', 'Punjab', 'Maharashtra', 'Madhya Pradesh', 'Uttar Pradesh'];

    // Handle input changes
    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    // 1. Fetch Weather from Backend (OpenWeatherMap)
    const fetchWeather = async () => {
        if (!formData.district) {
            alert("Please enter a district name.");
            return;
        }

        setWeatherLoading(true);
        setError('');
        try {
            const response = await axios.get(`http://localhost:5000/fetch_weather?state=${formData.state}&district=${formData.district}`);
            const data = response.data;

            setFormData(prev => ({
                ...prev,
                temperature: data.temperature,
                humidity: data.humidity,
                rainfall: data.rainfall // Can be 0 if no rain, user can edit
            }));

            alert(`Weather fetched for ${formData.district}!\nTemp: ${data.temperature}°C, Rain: ${data.rainfall}mm`);
        } catch (err) {
            console.error(err);
            alert("Failed to fetch weather. Please check city name or backend.");
        } finally {
            setWeatherLoading(false);
        }
    };

    // 2. Get Recommendation (ML Prediction)
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        // Basic validation
        if (!formData.temperature || !formData.rainfall || !formData.humidity) {
            setError("Please fetch weather or enter values manually.");
            setLoading(false);
            return;
        }

        try {
            // Mapping frontend keys to backend expectations if needed
            // Backend expects: region, N, P, K, pH, temperature, humidity, rainfall
            const payload = {
                region: formData.district, // Using district as region
                N: formData.N,
                P: formData.P,
                K: formData.K,
                pH: formData.pH,
                temperature: formData.temperature,
                humidity: formData.humidity,
                rainfall: formData.rainfall,
                // Include crop only if user specified one
                ...(formData.crop && { crop: formData.crop })
            };

            const response = await axios.post('http://localhost:5000/predict', payload);
            setResult(response.data.result); // Text response
        } catch (err) {
            console.error(err);
            setError('Prediction failed. Ensure backend is running.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content-wrapper" style={{ maxWidth: '1000px', margin: '0 auto' }}>
                <div className="form-section">
                    <h2 style={{ color: '#2c3e50', marginBottom: '10px' }}>🌾 Dynamic Crop Recommendation</h2>
                    <p className="subtitle">Get the best crop advice based on live weather and soil nutrients.</p>

                    <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>

                        {/* Section 1: Location & Weather */}
                        <div className="section-header">📍 Location & Weather</div>
                        <div className="form-grid">
                            <div className="form-group">
                                <label>State</label>
                                <select name="state" value={formData.state} onChange={handleChange}>
                                    {states.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>District / City</label>
                                <input type="text" name="district" value={formData.district} onChange={handleChange} placeholder="e.g. Davanagere" />
                            </div>
                            <div className="form-group" style={{ display: 'flex', alignItems: 'flex-end' }}>
                                <button type="button" onClick={fetchWeather} className="secondary-btn" disabled={weatherLoading} style={{ width: '100%' }}>
                                    {weatherLoading ? 'Fetching...' : '☁️ Fetch Live Weather'}
                                </button>
                            </div>
                        </div>

                        <div className="form-grid">
                            <div className="form-group">
                                <label>Temperature (°C)</label>
                                <input type="number" name="temperature" value={formData.temperature} onChange={handleChange} placeholder="Auto-fetched" step="0.1" required />
                            </div>
                            <div className="form-group">
                                <label>Humidity (%)</label>
                                <input type="number" name="humidity" value={formData.humidity} onChange={handleChange} placeholder="Auto-fetched" step="0.1" required />
                            </div>
                            <div className="form-group">
                                <label>Rainfall (mm)</label>
                                <input type="number" name="rainfall" value={formData.rainfall} onChange={handleChange} placeholder="Auto-fetched" step="0.1" required />
                            </div>
                        </div>

                        {/* Section 2: Soil Nutrients */}
                        <div className="section-header" style={{ marginTop: '20px' }}>🧪 Soil Details</div>
                        <div className="form-grid">
                            <div className="form-group">
                                <label>Nitrogen (N)</label>
                                <input type="number" name="N" value={formData.N} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label>Phosphorus (P)</label>
                                <input type="number" name="P" value={formData.P} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label>Potassium (K)</label>
                                <input type="number" name="K" value={formData.K} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label>pH Level</label>
                                <input type="number" name="pH" value={formData.pH} onChange={handleChange} step="0.1" required />
                            </div>
                            <div className="form-group">
                                <label>Crop (optional)</label>
                                <input type="text" name="crop" value={formData.crop} onChange={handleChange} placeholder="e.g. Rice" />
                            </div>
                        </div>

                        <div className="form-actions" style={{ marginTop: '30px' }}>
                            <button type="submit" className="primary-btn" disabled={loading} style={{ fontSize: '1.2em', padding: '15px 30px' }}>
                                {loading ? 'Analyzing...' : '🔍 Predict Best Crop'}
                            </button>
                        </div>
                    </form>

                    {error && <div className="error-msg" style={{ marginTop: '20px' }}>{error}</div>}
                </div>

                {/* Results Section */}
                {result && (
                    <div className="results-section" style={{ marginTop: '30px', padding: '20px', borderRadius: '8px', background: '#e8f5e9', border: '1px solid #c8e6c9' }}>
                        <h3 style={{ color: '#2e7d32' }}>📋 Recommendation Result</h3>
                        <div style={{ whiteSpace: 'pre-line', lineHeight: '1.6', fontSize: '1.1em', color: '#333' }}>
                            {result}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Recommend;
