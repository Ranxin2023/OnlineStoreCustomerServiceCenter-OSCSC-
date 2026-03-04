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

const STORE_URLS = {
  store1: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=98158",
  store2: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1471480",
  store3: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196",
  
};

function App() {
  // ── 订单列表爬取 ──────────────────────────────────
  const [scrapeUrl, setScrapeUrl] = useState("https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196");
  const [loading1, setLoading1] = useState(false);
  const [loading2, setLoading2] = useState(false);
  const [loading3, setLoading3] = useState(false);
  const [error1, setError1] = useState<string | null>(null);
  const [error2, setError2] = useState<string | null>(null);
  const [error3, setError3] = useState<string | null>(null);

  // ── 订单详情爬取 ──────────────────────────────────
  const [detailUrl, setDetailUrl] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detailResult, setDetailResult] = useState<DetailResult | null>(null);

  // ── 处理订单列表爬取 ──────────────────────────────
  const handleScrapeStore1 = async () => {
    const url=STORE_URLS.store1
    if (!url.startsWith("http")) {
      setError1("Please enter a valid URL");
      return;
    }
    
    setLoading1(true);
    setError1(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/web-scrapy/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url }),
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
      setError1(err.message || "Something went wrong");
    } finally {
      setLoading1(false);
    }
  };
  const handleScrapeStore2 = async () => {
    const url=STORE_URLS.store2
    if (!url.startsWith("http")) {
      setError2("Please enter a valid URL");
      return;
    }
    setLoading2(true);
    setError2(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/web-scrapy/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url }),
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
      setError2(err.message || "Something went wrong");
    } finally {
      setLoading2(false);
    }
  };
  const handleScrapeStore3 = async () => {
    const url=STORE_URLS.store2
    if (!url.startsWith("http")) {
      setError3("Please enter a valid URL");
      return;
    }
    setLoading3(true);
    setError3(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/web-scrapy/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url }),
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
      setError3(err.message || "Something went wrong");
    } finally {
      setLoading3(false);
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
          onClick={handleScrapeStore1}
          disabled={loading1}
        >
          {loading1 ? "Scraping..." : "🔍 Scrape Store1"}
        </button>
        {error1 && <p className="error-text">{error1}</p>}
        <button
          className="sidebar-btn"
          onClick={handleScrapeStore2}
          disabled={loading2}
        >
          {loading2 ? "Scraping..." : "🔍 Scrape Store2"}
        </button>
        {error2 && <p className="error-text">{error2}</p>}
        <button
          className="sidebar-btn"
          onClick={handleScrapeStore3}
          disabled={loading3}
        >
          {loading3 ? "Scraping..." : "🔍 Scrape Store3"}
        </button>
        {error3 && <p className="error-text">{error3}</p>}

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
          <div className="detail-result-box">
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
              <div key={label} className="detail-row">
                <span className="detail-label">{label}: </span>
                <span>{value || "—"}</span>
              </div>
            ))}
            {detailResult.clicked_by && (
              <p className="detail-clicked-by">
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
