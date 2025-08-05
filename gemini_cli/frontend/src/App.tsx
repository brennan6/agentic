import React, { useState } from 'react';
import './App.css';

function App() {
  const [picks, setPicks] = useState<string[]>([]);

  const fetchPicks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agent-picks');
      const data = await response.json();
      setPicks(data.picks);
    } catch (error) {
      console.error("Error fetching picks:", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Betting Agent</h1>
        <button onClick={fetchPicks}>Get Today's Picks</button>
        <ul>
          {picks.map((pick, index) => (
            <li key={index}>{pick}</li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
