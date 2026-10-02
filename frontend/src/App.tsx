import {
  BrowserRouter,
  Routes,
  Route,
} from 'react-router-dom'

import AppShell from './components/layout/AppShell'

import Dashboard from './pages/Dashboard'
import Incidents from './pages/Incidents'
import IncidentDetails from './pages/IncidentDetails'
import History from './pages/History'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<Dashboard />} />

          <Route
            path="/incidents"
            element={<Incidents />}
          />

          <Route
            path="/incidents/:incidentId"
            element={<IncidentDetails />}
          />

          <Route
            path="/history"
            element={<History />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App