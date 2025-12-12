import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Recommend from './pages/Recommend';
import Alerts from './pages/Alerts';
import PestAlert from './pages/PestAlert';
import Chatbot from './pages/Chatbot';
import MainLayout from './components/MainLayout';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<MainLayout><Dashboard /></MainLayout>} />
        <Route path="/analytics" element={<MainLayout><Analytics /></MainLayout>} />
        <Route path="/recommend" element={<MainLayout><Recommend /></MainLayout>} />
        <Route path="/alerts" element={<MainLayout><Alerts /></MainLayout>} />
        <Route path="/pest-alert" element={<MainLayout><PestAlert /></MainLayout>} />
        <Route path="/chatbot" element={<MainLayout><Chatbot /></MainLayout>} />
        {/* Default route */}
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;
