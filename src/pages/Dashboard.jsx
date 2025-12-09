import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const Dashboard = () => {
    const [formData, setFormData] = useState({
        crop: 'Wheat',
        region: 'Punjab',
        season: 'Rabi',
        temperature: '',
        rainfall: '',
        humidity: ''
    });

    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const crops = ['Wheat', 'Rice', 'Maize', 'Sugarcane', 'Cotton', 'Onion', 'Tomato', 'Potato'];
    const regions = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Madhya Pradesh'];
    const seasons = ['Rabi', 'Kharif', 'Zaid'];

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const fetchWeather = () => {
        // Simulate fetching weather
        setFormData({
            ...formData,
            temperature: (25 + Math.random() * 10).toFixed(1),
            rainfall: (50 + Math.random() * 100).toFixed(1),
            humidity: (40 + Math.random() * 30).toFixed(1)
        });
        alert("Simulated weather data fetched!");
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setPrediction(null);

        try {
            const response = await axios.post('http://localhost:5000/predict', formData);
            setPrediction(response.data);
        } catch (err) {
            setError('Failed to fetch prediction. Ensure backend is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Dummy data for graph
    const trendData = [
        { name: 'Jan', price: prediction ? prediction.predicted_price * 0.9 : 0 },
        { name: 'Feb', price: prediction ? prediction.predicted_price * 0.95 : 0 },
        { name: 'Mar', price: prediction ? prediction.predicted_price : 0 },
        { name: 'Apr', price: prediction ? prediction.predicted_price * 1.05 : 0 },
        { name: 'May', price: prediction ? prediction.predicted_price * 1.02 : 0 },
    ];

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content-wrapper">
                <div className="form-section">
                    <h2>🌾 Get Crop Price Prediction</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="form-grid">
                            <div className="form-group">
                                <label>Crop</label>
                                <select name="crop" value={formData.crop} onChange={handleChange}>
                                    {crops.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Region</label>
                                <select name="region" value={formData.region} onChange={handleChange}>
                                    {regions.map(r => <option key={r} value={r}>{r}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Season</label>
                                <select name="season" value={formData.season} onChange={handleChange}>
                                    {seasons.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Temperature (°C)</label>
                                <input type="number" step="0.1" name="temperature" value={formData.temperature} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label>Rainfall (mm)</label>
                                <input type="number" step="0.1" name="rainfall" value={formData.rainfall} onChange={handleChange} required />
                            </div>
                            <div className="form-group">
                                <label>Humidity (%)</label>
                                <input type="number" step="0.1" name="humidity" value={formData.humidity} onChange={handleChange} required />
                            </div>
                        </div>
                        <div className="form-actions">
                            <button type="button" onClick={fetchWeather} className="secondary-btn">Fetch Weather (Sim)</button>
                            <button type="submit" className="primary-btn" disabled={loading}>
                                {loading ? 'Predicting...' : 'Get Prediction'}
                            </button>
                        </div>
                    </form>
                    {error && <div className="error-msg">{error}</div>}
                </div>

                {prediction && (
                    <div className="results-section">
                        <div className="prediction-card">
                            <h3>Predicted Price</h3>
                            <div className="price">₹ {prediction.predicted_price} / Quintal</div>
                            <div className="suggestion">💡 {prediction.suggestion}</div>
                        </div>
                        <div className="chart-card">
                            <h3>Price Trend Forecast</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={trendData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 8 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
