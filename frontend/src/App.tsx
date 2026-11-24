import { Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Discipline from './pages/Discipline'
import Login from './pages/Login'
import Orders from './pages/Orders'
import Portfolio from './pages/Portfolio'
import StockDetail from './pages/StockDetail'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Dashboard />} />
      <Route path="/stocks/:symbol" element={<StockDetail />} />
      <Route path="/portfolio" element={<Portfolio />} />
      <Route path="/orders" element={<Orders />} />
      <Route path="/discipline" element={<Discipline />} />
    </Routes>
  )
}
