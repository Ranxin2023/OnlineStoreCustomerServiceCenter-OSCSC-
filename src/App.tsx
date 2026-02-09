import "./App.css";

function App() {
  return (
    <div className="app-layout">
      {/* Left sidebar */}
      <aside className="sidebar">
        <h2>Hwatel</h2>

        <button className="sidebar-btn">Check Prices</button>
        <button className="sidebar-btn">📞 Contact Support</button>
        <button className="sidebar-btn">🧾 My Reservations</button>
        <button className="sidebar-btn">❓ FAQs</button>
      </aside>

      {/* Main chatbot area */}
      <main className="chat-container">
        <div className="chat-header">
          <h3>Customer Service Chat</h3>
        </div>

        <div className="chat-messages">
          <div className="message bot">
            👋 Hi! How can I help you with your stay today?
          </div>
        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
          />
          <button>Send</button>
        </div>
      </main>
    </div>
  );
}

export default App;
