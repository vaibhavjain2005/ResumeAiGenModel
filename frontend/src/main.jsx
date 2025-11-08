import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { createRoot } from 'react-dom/client'
import './index.css'
import { HeroUIProvider } from "@heroui/react";
import App from './App.jsx'
import DataFormPage from './components/DataFormPage.jsx';
import MainLayout from './layouts/MainLayout.jsx';




createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route element={<MainLayout />}><Route path="/" element={<HeroUIProvider><App /></HeroUIProvider>} />
        <Route path="/get-started" element={<DataFormPage />} /></Route>

    </Routes>
  </BrowserRouter>

)
