import Chat from "./components/Chat";

function App() {
  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Fintech Knowledge Assistant</h1>
          <p>RAG over SOPs, policies, FAQs, and test cases</p>
        </div>
      </header>
      <main className="content">
        <Chat />
      </main>
    </div>
  );
}

export default App;

