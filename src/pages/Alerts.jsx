import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import './Alerts.css';

const Alerts = () => {
    const [marketStatus, setMarketStatus] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    // Form State
    const [formData, setFormData] = useState({
        crop: 'Wheat',
        target_price: '',
        condition: 'Above',
        contact: '' // In real app, could be pre-filled from user profile
    });

    const API_URL = 'http://localhost:5000';

    useEffect(() => {
        fetchMarketStatus();
        fetchAlerts();
    }, []);

    const fetchMarketStatus = async () => {
        try {
            const res = await fetch(`${API_URL}/market-status`);
            const data = await res.json();
            setMarketStatus(data);
        } catch (err) {
            console.error("Error fetching market status:", err);
        }
    };

    const fetchAlerts = async () => {
        try {
            const res = await fetch(`${API_URL}/alerts`);
            const data = await res.json();
            setAlerts(data);
            setLoading(false);
        } catch (err) {
            console.error("Error fetching alerts:", err);
            setLoading(false);
        }
    };

    const handleCreateAlert = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch(`${API_URL}/alerts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (res.ok) {
                alert('Alert created successfully!');
                fetchAlerts(); // Refresh list
                setFormData({ ...formData, target_price: '' }); // Clear price
            } else {
                alert('Failed to create alert');
            }
        } catch (err) {
            console.error("Error creating alert:", err);
        }
    };

    const handleDeleteAlert = async (id) => {
        if (!window.confirm("Are you sure you want to delete this alert?")) return;
        try {
            await fetch(`${API_URL}/alerts/${id}`, { method: 'DELETE' });
            fetchAlerts();
        } catch (err) {
            console.error("Error deleting alert:", err);
        }
    };

    const getTrendIcon = (trend) => {
        if (trend === 'Up') return <span className="trend-arrow">⬆️</span>;
        if (trend === 'Down') return <span className="trend-arrow">⬇️</span>;
        return <span className="trend-arrow">➡️</span>;
    };

    return (
        <div className="alerts-container">
            <Navbar />
            <header className="alerts-header">
                <h1>📡 Market Monitor & Alerts</h1>
                <p>Track live prices and set automated notifications.</p>
            </header>

            {/* Market Trends Section */}
            <section className="market-trends-section">
                <h2>📈 Live Market Trends</h2>
                <div className="market-trends-grid">
                    {marketStatus.map((item, index) => (
                        <div key={index} className="trend-card">
                            <h3>{item.crop}</h3>
                            <div className="price-display">₹{item.price}</div>
                            <div className={`trend-indicator trend-${item.trend.toLowerCase()}`}>
                                {getTrendIcon(item.trend)}
                                <span>{item.change}%</span>
                            </div>
                        </div>
                    ))}
                    {marketStatus.length === 0 && <p>Loading trends...</p>}
                </div>
            </section>

            {/* Alert Management Section */}
            <section className="alerts-management">
                {/* Create Alert Form */}
                <div className="create-alert-form">
                    <h2>🔔 Set New Alert</h2>
                    <form onSubmit={handleCreateAlert}>
                        <div className="form-group">
                            <label>Crop</label>
                            <select
                                value={formData.crop}
                                onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
                            >
                                {marketStatus.length > 0 ?
                                    marketStatus.map(m => <option key={m.crop} value={m.crop}>{m.crop}</option>)
                                    : <option>Wheat</option>
                                }
                                <option>Sugarcane</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Target Price (₹)</label>
                            <input
                                type="number"
                                required
                                value={formData.target_price}
                                onChange={(e) => setFormData({ ...formData, target_price: e.target.value })}
                                placeholder="e.g. 2000"
                            />
                        </div>
                        <div className="form-group">
                            <label>Condition</label>
                            <select
                                value={formData.condition}
                                onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                            >
                                <option value="Above">Price Goes Above</option>
                                <option value="Below">Price Drops Below</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label>Notify Email/Phone</label>
                            <input
                                type="text"
                                required
                                value={formData.contact}
                                onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
                                placeholder="me@example.com"
                            />
                        </div>
                        <button type="submit" className="submit-btn" disabled={loading}>
                            Create Alert
                        </button>
                    </form>
                </div>

                {/* Active Alerts List */}
                <div className="active-alerts">
                    <h2>📋 Active Alerts</h2>
                    {alerts.length === 0 ? (
                        <p style={{ color: '#888' }}>No alerts active.</p>
                    ) : (
                        <div className="alerts-list">
                            {alerts.map(alert => (
                                <div key={alert.id} className="alert-item">
                                    <div className="alert-info">
                                        <p><strong>{alert.crop}</strong></p>
                                        <p>{alert.condition} <span>₹{alert.target_price}</span></p>
                                        <small style={{ color: '#666' }}>{alert.contact}</small>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteAlert(alert.id)}
                                        className="delete-btn"
                                    >
                                        Delete
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
};

export default Alerts;
