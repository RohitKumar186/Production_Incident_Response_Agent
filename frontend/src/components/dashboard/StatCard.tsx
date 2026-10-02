import type { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: number
  description: string
  icon?: ReactNode
}

function StatCard({
  title,
  value,
  description,
  icon,
}: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>

        {icon && (
          <div className="stat-card-icon">
            {icon}
          </div>
        )}
      </div>

      <div className="stat-card-value">
        {value}
      </div>

      <div className="stat-card-description">
        {description}
      </div>
    </div>
  )
}

export default StatCard