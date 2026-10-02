import {
  Activity,
  LayoutDashboard,
  History,
  ShieldAlert,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <ShieldAlert size={20} />
        </div>

        <div className="sidebar-brand-text">
          <h1>PIRA</h1>
          <span>Production Incident Response</span>
        </div>
      </div>

      <div className="sidebar-section-title">Operations</div>

      <nav className="sidebar-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `sidebar-link ${isActive ? 'active' : ''}`
          }
        >
          <LayoutDashboard />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/incidents"
          className={({ isActive }) =>
            `sidebar-link ${isActive ? 'active' : ''}`
          }
        >
          <Activity />
          <span>Incidents</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `sidebar-link ${isActive ? 'active' : ''}`
          }
        >
          <History />
          <span>History</span>
        </NavLink>
      </nav>

      <div className="sidebar-bottom">
        <div className="engine-status">
          <div className="engine-status-header">
            <span className="status-dot" />
            <span>System Online</span>
          </div>

          <div className="engine-status-text">
            PIRA Engine operational
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar