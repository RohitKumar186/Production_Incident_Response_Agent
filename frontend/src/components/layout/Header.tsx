import {
  Bell,
  Search,
} from 'lucide-react'

function Header() {
  return (
    <header className="header">
      <div className="header-search">
        <Search />

        <input
          type="text"
          placeholder="Search incidents..."
          aria-label="Search incidents"
        />
      </div>

      <div className="header-actions">
        <button
          type="button"
          className="header-icon-button"
          aria-label="Notifications"
        >
          <Bell size={17} />
        </button>

        <div className="header-user">
          <div className="header-avatar">
            YO
          </div>

          <div className="header-user-info">
            <div className="header-user-name">
              Incident Operator
            </div>

            <div className="header-user-role">
              Administrator
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header