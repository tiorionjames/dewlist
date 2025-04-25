import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { setToken } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password }),
    });
    if (!res.ok) {
      alert('Login failed');
      return;
    }
    const data = await res.json();
    setToken(data.access_token);
    navigate('/');
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl mb-4">Sign In</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>
        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>
        <button type="submit" className="w-full p-2 bg-blue-500 text-white rounded">
          Log In
        </button>
      </form>
      <p className="mt-2 text-sm">
        Don’t have an account? <Link to="/register" className="text-blue-500">Register</Link>
      </p>
      <p className="mt-1 text-sm">
        <Link to="/forgot-password" className="text-red-500">Forgot your password?</Link>
      </p>
    </div>
  );
}
