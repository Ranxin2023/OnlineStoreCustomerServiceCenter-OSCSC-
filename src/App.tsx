// import { useState } from "react";
// import "./App.css";

// function App() {
//   const [scrapeUrl, setScrapeUrl] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState<string | null>(null);
//   // const isValidUrl = scrapeUrl.startsWith("http://") || scrapeUrl.startsWith("https://");
//   const handleScrapeWebsite = async () => {
//     if (!scrapeUrl.startsWith("http")) {
//       setError("Please enter a valid URL");
//       return;
//     }

//     setLoading(true);
//     setError(null);

//     try {
//       const response = await fetch("http://localhost:5000/api/web-scrapy/scrape", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ url: scrapeUrl }),
//       });

//       if (!response.ok) {
//         throw new Error("Failed to scrape website");
//       }

//       // ✅ use blob,instead of json
//       const blob = await response.blob();

//       // create download link
//       const downloadUrl = window.URL.createObjectURL(blob);
//       const a = document.createElement("a");
//       a.href = downloadUrl;

//       // file name
//       a.download = "orders.csv";

//       document.body.appendChild(a);
//       a.click();

//       a.remove();
//       window.URL.revokeObjectURL(downloadUrl);

//       console.log("✅ CSV downloaded successfully");
//     } catch (err: any) {
//       setError(err.message || "Something went wrong");
//     } finally {
//       setLoading(false);
//     }
//   };
  
//   return (
//     <div className="app-layout">
//       {/* Left sidebar */}
//       <aside className="sidebar">
//         <h2>Hwatel</h2>

//         <button className="sidebar-btn">Check Prices</button>

//         <button className="sidebar-btn">📞 Contact Support</button>
//         <button className="sidebar-btn">🧾 My Reservations</button>
//         <button className="sidebar-btn">❓ FAQs</button>
//         {/* Website URL input */}
//         <input
//           className="sidebar-input"
//           type="text"
//           placeholder="Enter website URL"
//           value={scrapeUrl}
//           onChange={(e) => setScrapeUrl(e.target.value)}
//         />
//         <button
//           className="sidebar-btn"
//           onClick={handleScrapeWebsite}
//           disabled={loading}
//         >
//           {loading ? "Scraping..." : "🔍 Scrape Website"}
//         </button>
//         {error && <p style={{ color: "salmon", fontSize: "12px" }}>{error}</p>}
//       </aside>

//       {/* Main chatbot area */}
//       <main className="chat-container">
//         <div className="chat-header">
//           <h3>Customer Service Chat</h3>
//         </div>

//         <div className="chat-messages">
//           <div className="message bot">
//             👋 Hi! How can I help you with your stay today?
//           </div>
//         </div>

//         <div className="chat-input">
//           <input
//             type="text"
//             placeholder="Type your message..."
//           />
//           <button>Send</button>
//         </div>
//       </main>
//     </div>
//   );
// }

// export default App;
import { useState } from "react";
import "./App.css";

interface OrderDetail {
  recipient: string;
  address: string;
  postal_code: string;
  email: string;
  phone: string;
  tax_number: string;
}

interface DetailResult {
  data: OrderDetail;
  unmasked: boolean;
  clicked_by: string | null;
  debug_elements: any[];
}

function App() {
  // ── 订单列表爬取 ──────────────────────────────────
  const [scrapeUrl, setScrapeUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── 订单详情爬取 ──────────────────────────────────
  const [detailUrl, setDetailUrl] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detailResult, setDetailResult] = useState<DetailResult | null>(null);

  // ── 处理订单列表爬取 ──────────────────────────────
  const handleScrapeWebsite = async () => {
    if (!scrapeUrl.startsWith("http")) {
      setError("Please enter a valid URL");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/web-scrapy/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: scrapeUrl }),
      });
      if (!response.ok) throw new Error("Failed to scrape website");

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = "orders.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  // ── 处理订单详情爬取 ──────────────────────────────
  const handleScrapeDetail = async () => {
    if (!detailUrl.startsWith("http")) {
      setDetailError("Please enter a valid URL");
      return;
    }
    setDetailLoading(true);
    setDetailError(null);
    setDetailResult(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/web-scrapy/scrape-detail`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: detailUrl }),
      });
      const json = await response.json();
      if (!response.ok) throw new Error(json.error || "Failed to scrape detail");
      setDetailResult(json);
    } catch (err: any) {
      setDetailError(err.message || "Something went wrong");
    } finally {
      setDetailLoading(false);
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

        {/* ── 订单列表爬取 ── */}
        <input
          className="sidebar-input"
          type="text"
          placeholder="Order list URL"
          value={scrapeUrl}
          onChange={(e) => setScrapeUrl(e.target.value)}
        />
        <button
          className="sidebar-btn"
          onClick={handleScrapeWebsite}
          disabled={loading}
        >
          {loading ? "Scraping..." : "🔍 Scrape Orders"}
        </button>
        {error && <p style={{ color: "salmon", fontSize: "12px" }}>{error}</p>}

        {/* ── 订单详情爬取 ── */}
        <hr style={{ width: "100%", borderColor: "#444", margin: "12px 0" }} />
        <input
          className="sidebar-input"
          type="text"
          placeholder="Order detail URL"
          value={detailUrl}
          onChange={(e) => setDetailUrl(e.target.value)}
        />
        <button
          className="sidebar-btn"
          onClick={handleScrapeDetail}
          disabled={detailLoading}
        >
          {detailLoading ? "Loading..." : "📦 Scrape Detail"}
        </button>
        {detailError && (
          <p style={{ color: "salmon", fontSize: "12px" }}>{detailError}</p>
        )}

        {/* 详情结果展示 */}
        {detailResult && (
          <div style={{
            marginTop: "10px",
            background: "#1e1e1e",
            border: "1px solid #444",
            borderRadius: "8px",
            padding: "10px",
            fontSize: "12px",
            color: "#eee",
            wordBreak: "break-all",
          }}>
            <p style={{ marginBottom: "6px", color: detailResult.unmasked ? "#4caf50" : "#ff9800", fontWeight: "bold" }}>
              {detailResult.unmasked ? "✅ Unmasked" : "⚠️ Still masked"}
            </p>
            {(
              [
                ["👤 Recipient",  detailResult.data.recipient],
                ["🏠 Address",    detailResult.data.address],
                ["📮 Postal",     detailResult.data.postal_code],
                ["📧 Email",      detailResult.data.email],
                ["📞 Phone",      detailResult.data.phone],
                ["🧾 Tax No.",    detailResult.data.tax_number],
              ] as [string, string][]
            ).map(([label, value]) => (
              <div key={label} style={{ marginBottom: "4px" }}>
                <span style={{ color: "#aaa" }}>{label}: </span>
                <span>{value || "—"}</span>
              </div>
            ))}
            {detailResult.clicked_by && (
              <p style={{ marginTop: "8px", color: "#888", fontSize: "11px" }}>
                clicked_by: {detailResult.clicked_by}
              </p>
            )}
          </div>
        )}
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
          <input type="text" placeholder="Type your message..." />
          <button>Send</button>
        </div>
      </main>
    </div>
  );
}

export default App;
