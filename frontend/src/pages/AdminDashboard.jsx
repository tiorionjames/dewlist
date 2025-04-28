import React from 'react';
import { Link } from 'react-router-dom';

export default function AdminDashboard() {
  return (
    <div>
      <h1>Admin Dashboard</h1>
      <nav>
        <ul>
          <li><Link to="/admin/logs">View Audit Logs</Link></li>
          {/* Future links to /admin/users, /admin/settings, etc */}
        </ul>
      </nav>
    </div>
  );
}
