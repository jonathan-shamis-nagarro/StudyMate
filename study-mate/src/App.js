import Home from './pages/Home';
import Layout from './pages/Layout';
import './App.css';

import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

function App() {
  return (
    <Router>
      <div>
        <Layout />
        <main role="main" className="main-container">
        <Switch>
          <Route path="/">
            <Home />
          </Route>
        </Switch>
        </main>
      </div>
    </Router>
  )
}
export default App;
