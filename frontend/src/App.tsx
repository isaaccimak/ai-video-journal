import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import RouterConfig from './RouterConfig';

const App: React.FC = () => {
  return (
    <Router>
      <RouterConfig />
    </Router>
  );
}

export default App;
