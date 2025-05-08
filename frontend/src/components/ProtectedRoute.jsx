// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { token, user } = useAuth();

  if (!token) {
    // not logged in
    return <Navigate to="/login" replace />;
  }
  if (adminOnly && user?.role !== 'admin') {
    // logged in but not an admin
    return <Navigate to="/" replace />;
  }

  return children;
}
