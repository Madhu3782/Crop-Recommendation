import React from 'react';
import Sidebar from './Sidebar';
import './MainLayout.css';

const MainLayout = ({ children }) => {
    return (
        <div className="main-layout">
            <Sidebar />
            <div className="main-content">
                {children}
            </div>
        </div>
    );
};

export default MainLayout;
