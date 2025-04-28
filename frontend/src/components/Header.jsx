// src/components/Header.jsx

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Make sure this path is correct
import { toast } from 'react-toastify'; // We’ll install this in a second

export default function Header() {
  const { token, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();               // Clear the auth session
    navigate('/login');      // Redirect user to login page
    toast.success('Logged out successfully'); // 🎉 Show logout success
  };

  return (
    <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem' }}>
      <h1>DewList</h1>
      <div>
        {!token ? (
          <Link to="/login">
            <button>Login</button>
          </Link>
        ) : (
          <>
            {/* Only show Admin Dashboard if user is admin */}
            {user?.role === 'admin' && (
              <Link to="/admin">
                <button style={{ marginRight: '1rem' }}>Admin Dashboard</button>
              </Link>
            )}
            <button onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>
    </header>
  );
}
