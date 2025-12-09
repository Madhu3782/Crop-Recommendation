import React, { useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import './Dashboard.css'; // Reuse dashboard styles

const Recommend = () => {
    const [formData, setFormData] = useState({
        region: 'Punjab',
        season: 'Rabi',
        soil_type: 'Loamy',
        temperature: '',
        rainfall: '',
        humidity: ''
    });

    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const regions = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Maharashtra', 'Karnataka', 'Madhya Pradesh'];
    const seasons = ['Rabi', 'Kharif', 'Zaid'];
    const soilTypes = ['Clayey', 'Loamy', 'Sandy', 'Black', 'Red'];

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const fetchWeather = () => {
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
        // DEBUG: Check what is being sent
        alert(`Sending Data:\nRegion: ${formData.region}\nSoil: ${formData.soil_type}\nRainfall: ${formData.rainfall}`);

        setLoading(true);
        setError('');
        setRecommendations(null);

        try {
            const response = await axios.post('http://localhost:5000/recommend', formData);
            // Attach debug info to the recommendations object for easy access (hacky but works for debug)
            const recs = response.data.recommendations;
            recs.debug_soil = response.data.debug_received_soil;
            recs.debug_rain = response.data.debug_rainfall;
            setRecommendations(recs);
        } catch (err) {
            setError('Failed to fetch recommendations. Ensure backend is running.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content-wrapper">
                <div className="form-section">
                    <h2>🌱 Best Crop Recommendation</h2>
                    <p className="subtitle">Find the most profitable crop for your soil and weather condition.</p>
                    <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
                        <div className="form-grid">
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
                                <label>Soil Type</label>
                                <select name="soil_type" value={formData.soil_type} onChange={handleChange}>
                                    {soilTypes.map(s => <option key={s} value={s}>{s}</option>)}
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
                                {loading ? 'Analyzing...' : 'Get Recommendation'}
                            </button>
                        </div>
                    </form>
                    {error && <div className="error-msg">{error}</div>}
                </div>

                {recommendations && (
                    <div className="results-section">
                        <h3>🏆 Top Recommended Crops</h3>
                        {/* DEBUG INFO DISPLAY */}
                        <div style={{ background: '#eee', padding: '10px', fontSize: '0.8em', marginBottom: '10px' }}>
                            Debug: Backend received Soil="{recommendations.debug_soil}" Rain="{recommendations.debug_rain}"
                        </div>
                        <div className="recommendation-list">
                            {recommendations.map((rec, index) => (
                                <div key={index} className={`rec-card ${index === 0 ? 'top-rec' : ''}`}>
                                    <div className="rank">#{index + 1}</div>
                                    <div className="crop-info">
                                        <h4>{rec.crop}</h4>
                                        <div className="rec-price">Predicted: ₹ {rec.predicted_price}</div>
                                    </div>
                                    {index === 0 && <div className="badge">Best Choice</div>}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Recommend;
