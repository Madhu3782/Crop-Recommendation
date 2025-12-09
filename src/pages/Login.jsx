import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css'; // We will create this

const Login = () => {
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setCredentials({ ...credentials, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Mock login
        if (credentials.username && credentials.password) {
            localStorage.setItem('user', credentials.username);
            navigate('/dashboard');
        } else {
            alert('Please enter username and password');
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Welcome Back</h2>
                <form onSubmit={handleSubmit}>
                    <div className="input-group">
                        <label>Username</label>
                        <input
                            type="text"
                            name="username"
                            value={credentials.username}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <div className="input-group">
                        <label>Password</label>
                        <input
                            type="password"
                            name="password"
                            value={credentials.password}
                            onChange={handleChange}
                            required
                        />
                    </div>
                    <button type="submit" className="login-btn">Login</button>
                    <p className="register-link">
                        New here? <a href="/register">Create an account</a>
                    </p>
                </form>
            </div>
        </div>
    );
};

export default Login;
