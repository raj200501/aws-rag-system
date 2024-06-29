import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Search from './pages/Search';
import Generate from './pages/Generate';

function App() {
  return (
    <Router>
      <div className="App">
        <Switch>
          <Route path="/" exact component={Home} />
          <Route path="/upload" component={Upload} />
          <Route path="/search" component={Search} />
          <Route path="/generate" component={Generate} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
