import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { SearchIcon, UserCircle2, Droplet } from 'lucide-react';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';

export default function Header() {
  const { token, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="flex items-center justify-between p-4 bg-surface dark:bg-neutral-dark">
      {/* Left section: Logo + Search */}
      <div className="flex items-center space-x-4">
        <Droplet className="w-10 h-10 text-primary fill-current" />
        <h1 className="text-2xl font-bold text-primary">DewList</h1>
        <button className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-600">
          <SearchIcon className="w-5 h-5 text-text-muted" />
        </button>
      </div>

      {/* Right section: Auth links + User menu */}
      <div className="flex items-center space-x-4">
        {!token ? (
          <Link to="/login">
            <button className="px-3 py-1 rounded bg-primary text-black hover:bg-primary-dark">
              Login
            </button>
          </Link>
        ) : (
          <>
            {user?.role === 'admin' && (
              <Link to="/admin">
                <button className="px-3 py-1 rounded bg-primary-dark text-white hover:bg-primary">
                  Admin Dashboard
                </button>
              </Link>
            )}

            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <button className="p-2 rounded-full bg-primary-dark hover:bg-primary">
                  <UserCircle2 className="w-6 h-6 text-white" />
                </button>
              </DropdownMenu.Trigger>

              <DropdownMenu.Content className="bg-surface dark:bg-neutral-dark rounded shadow p-2">
                <DropdownMenu.Item
                  className="px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                  onSelect={handleLogout}
                >
                  Logout
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Root>
          </>
        )}
      </div>
    </header>
  );
}
