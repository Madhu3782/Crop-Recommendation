import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import Navbar from '../components/Navbar';
import './Dashboard.css'; // Reusing dashboard styles for consistency

const Analytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get('http://localhost:5000/analytics')
            .then(res => {
                if (res.data.error) {
                    console.error("Backend Error:", res.data.error);
                    setLoading(false);
                    return;
                }

                const avgPriceData = res.data.avg_price_by_crop ? Object.keys(res.data.avg_price_by_crop).map(key => ({
                    name: key,
                    price: Math.round(res.data.avg_price_by_crop[key])
                })) : [];

                const avgRegionData = res.data.avg_region_by_price ? Object.keys(res.data.avg_price_by_region).map(key => ({
                    name: key,
                    price: Math.round(res.data.avg_price_by_region[key])
                })) : (res.data.avg_price_by_region ? Object.keys(res.data.avg_price_by_region).map(key => ({
                    name: key,
                    price: Math.round(res.data.avg_price_by_region[key])
                })) : []);

                setData({
                    avgPriceData,
                    avgRegionData,
                    trendData: res.data.trend_data || []
                });
                setLoading(false);
            })
            .catch(err => {
                console.error("Network/Parse Error:", err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="dashboard-container">
            <Navbar />
            <div className="content-wrapper">
                <div style={{ width: '100%', marginBottom: '20px' }}>
                    <h2>📊 Market Analytics</h2>
                </div>

                {loading ? (
                    <p>Loading analytics data...</p>
                ) : data ? (
                    <>
                        <div className="chart-card" style={{ flex: '1 1 45%' }}>
                            <h3>Average Price by Crop</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={data.avgPriceData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="price" fill="#8884d8" name="Avg Price (₹)" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="chart-card" style={{ flex: '1 1 45%' }}>
                            <h3>Average Price by Region</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={data.avgRegionData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="price" fill="#82ca9d" name="Avg Price (₹)" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="chart-card" style={{ flex: '1 1 100%', marginTop: '30px' }}>
                            <h3>Recent Price Trends (Market Sample)</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={data.trendData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="Date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="Price" stroke="#ff7300" dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </>
                ) : (
                    <p>Failed to load data.</p>
                )}
            </div>
        </div>
    );
};

export default Analytics;
