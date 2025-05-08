import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function ManagerDashboard() {
  const navigate = useNavigate();

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Admin Dashboard</h1>
      <nav className="mb-6">
        <ul className="space-y-2">

          {/* Future links to /admin/users, /admin/settings, etc */}
        </ul>
      </nav>
      <button
        onClick={() => navigate('/')}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Go to Main Page
      </button>
    </div>
  );
}
