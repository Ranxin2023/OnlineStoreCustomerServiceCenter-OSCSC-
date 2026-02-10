import { useState } from "react";
import "./App.css";

function App() {
  const [scrapeUrl, setScrapeUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // const isValidUrl = scrapeUrl.startsWith("http://") || scrapeUrl.startsWith("https://");
  const handleScrapeWebsite = async () => {
    if (!scrapeUrl.startsWith("http")) {
      setError("Please enter a valid URL");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:5000/api/web-scrapy/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: scrapeUrl }),
      });

      if (!response.ok) {
        throw new Error("Failed to scrape website");
      }

      // ✅ use blob,instead of json
      const blob = await response.blob();

      // create download link
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;

      // file name
      a.download = "orders.csv";

      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(downloadUrl);

      console.log("✅ CSV downloaded successfully");
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      {/* Left sidebar */}
      <aside className="sidebar">
        <h2>Hwatel</h2>

        <button className="sidebar-btn">Check Prices</button>

        <button className="sidebar-btn">📞 Contact Support</button>
        <button className="sidebar-btn">🧾 My Reservations</button>
        <button className="sidebar-btn">❓ FAQs</button>
        {/* Website URL input */}
        <input
          className="sidebar-input"
          type="text"
          placeholder="Enter website URL"
          value={scrapeUrl}
          onChange={(e) => setScrapeUrl(e.target.value)}
        />
        <button
          className="sidebar-btn"
          onClick={handleScrapeWebsite}
          disabled={loading}
        >
          {loading ? "Scraping..." : "🔍 Scrape Website"}
        </button>
        {error && <p style={{ color: "salmon", fontSize: "12px" }}>{error}</p>}
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
