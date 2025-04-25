import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      alert('Registration failed: ' + (err.detail || res.status));
      return;
    }
    alert('Registered successfully! Please log in.');
    navigate('/login');
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl mb-4">Register</h2>
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
        <button type="submit" className="w-full p-2 bg-green-500 text-white rounded">
          Register
        </button>
      </form>
      <p className="mt-4 text-sm">
        Already have an account? <Link to="/login" className="text-blue-500">Log in</Link>
      </p>
    </div>
  );
}
