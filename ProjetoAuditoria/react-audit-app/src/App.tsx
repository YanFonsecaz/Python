import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { ErrorPage } from './pages/ErrorPage';

/**
 * Componente principal da aplicação
 * Configura o roteamento entre as páginas
 */
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/error" element={<ErrorPage />} />
          {/* Rota catch-all para páginas não encontradas */}
          <Route path="*" element={<ErrorPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
