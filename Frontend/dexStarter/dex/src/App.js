import "./App.css";
import Header from './components/Header'
import Tokens from './components/Tokens'
import Swap from './components/Swap'
import { Routes, Route } from 'react-router-dom'

function App() {
  return(
  <div className="App">

    <div className="mainWindow">
      <Routes>
        <Route path = "/" element={<Swap />} />
      </Routes>
      
    </div>
  </div>
  ) 
}

export default App;
