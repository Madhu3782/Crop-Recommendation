import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { FaHome, FaChartBar, FaLeaf, FaBell, FaSignOutAlt, FaBug, FaRobot } from 'react-icons/fa';
import './Sidebar.css';

const Sidebar = () => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('user');
        navigate('/login');
    };

    const menuItems = [
        { path: '/dashboard', name: 'Dashboard', icon: <FaHome /> },
        { path: '/analytics', name: 'Analytics', icon: <FaChartBar /> },
        { path: '/recommend', name: 'Recommendation', icon: <FaLeaf /> },
        { path: '/alerts', name: 'Alerts', icon: <FaBell /> },
        { path: '/pest-alert', name: 'Pest Warning', icon: <FaBug /> },
        { path: '/chatbot', name: 'AI Assistant', icon: <FaRobot /> },
    ];

    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h2>🌾 CropPriceAI</h2>
            </div>
            <div className="sidebar-menu">
                {menuItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => isActive ? "menu-item active" : "menu-item"}
                    >
                        <span className="icon">{item.icon}</span>
                        <span className="label">{item.name}</span>
                    </NavLink>
                ))}
            </div>
            <div className="sidebar-footer">
                <button onClick={handleLogout} className="logout-btn">
                    <FaSignOutAlt className="icon" />
                    <span className="label">Logout</span>
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
