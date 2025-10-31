import HotTakeGenerator from './components/HotTakeGenerator'
import './App.css'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🔥 Hot Take Generator 🔥</h1>
        <p>Generate spicy opinions on any topic with AI agents</p>
      </header>
      <main>
        <HotTakeGenerator />
      </main>
    </div>
  )
}

export default App
