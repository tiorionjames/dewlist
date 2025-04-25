// frontend/src/pages/ResetPasswordPage.jsx
import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

export default function ResetPasswordPage() {
  const query    = useQuery();
  const token    = query.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm,  setConfirm]  = useState('');
  const [error,    setError]    = useState('');
  const [success,  setSuccess]  = useState(false);

  useEffect(() => {
    if (!token) {
      setError('No reset token provided.');
    }
  }, [token]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    try {
      const res = await fetch('http://localhost:8000/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });
      const body = await res.json();
      if (!res.ok) {
        setError(body.detail || 'Failed to reset password.');
      } else {
        setSuccess(true);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  }

  if (error && !success) {
    return (
      <div className="p-4 max-w-md mx-auto">
        <p className="text-red-500">{error}</p>
        <p className="mt-4">
          <Link to="/login" className="text-blue-500">Back to login</Link>
        </p>
      </div>
    );
  }

  if (success) {
    return (
      <div className="p-4 max-w-md mx-auto">
        <h2 className="text-xl mb-4">Password Reset!</h2>
        <p>Your password has been updated.</p>
        <p className="mt-4">
          <Link to="/login" className="text-blue-500">Log in with your new password</Link>
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl mb-4">Reset Password</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label>New Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>
        <div>
          <label>Confirm Password</label>
          <input
            type="password"
            value={confirm}
            onChange={e => setConfirm(e.target.value)}
            className="w-full border p-2 rounded"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full p-2 bg-green-500 text-white rounded"
        >
          Update Password
        </button>
      </form>
    </div>
  );
}
