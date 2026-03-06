import { useState, useEffect} from "react";
import "./App.css";
import { io } from "socket.io-client";

const socket = io(`${import.meta.env.VITE_API_URL}`);
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
type Store = "store1" | "store2" | "store3";
const STORE_URLS = {
  store1: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=98158",
  store2: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1471480",
  store3: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196",
  
};
const STORE_CHANNEL_ID: Record<Store, string>= {
  store1: "98158",
  store2: "1471480",
  store3: "1579196",
  
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
  
  // ── 日志获取 ──────────────────────────────────
  const [logs, setLogs] = useState<string[]>([]);
  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };
  useEffect(() => {
    socket.on("connect", () => {
      console.log("Socket connected");
      addLog("Socket connected");
    });

    // socket.on("scrape_log", (data: { msg: string }) => {
    //   setLogs(prev => [
    //     ...prev,
    //     `[${new Date().toLocaleTimeString()}] ${data.msg}`
    //   ]);
    // });
    socket.on("scrape_log", (data) => {
      console.log("SCRAPE LOG:", data);
      addLog(data.msg);
    });
    return () => {
      socket.off("scrape_log");
    };
  }, []);
  // ── 处理订单列表爬取 ──────────────────────────────
  
  const handleSetupDriver = async (store: Store) => {
    try {

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/web-scrapy/setup-driver`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ channelId: STORE_CHANNEL_ID[store]})
        }
      );

      if (!response.ok) {
        throw new Error("Failed to setup driver");
      }

      alert(`Driver for ${store} ready. Please login if needed.`);

    } catch (err: any) {
      alert(err.message || "Setup failed");
    }
  };
  const handleScrape = async (
    url: string,
    setError: React.Dispatch<React.SetStateAction<string | null>>,
    setLoading: React.Dispatch<React.SetStateAction<boolean>>
  )=>{
     if (!url.startsWith("http")) {
      setError("Please enter a valid URL");
      return;
    }
    setLoading(true);
    setError(null);
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
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }
  const handleScrapeStore1 = async () => {
    addLog("Start scraping Store1");
    const url=STORE_URLS.store1
    handleScrape(url, setError1, setLoading1)
    addLog("Finished scraping Store1");
  };
  const handleScrapeStore2 = async () => {
    const url=STORE_URLS.store2
    handleScrape(url, setError2, setLoading2)
    
  };
  const handleScrapeStore3 = async () => {
    const url=STORE_URLS.store3
    handleScrape(url, setError3, setLoading3)
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
        <hr style={{ width: "100%", borderColor: "#444", margin: "12px 0" }} />
        {/* ── 订单列表爬取 ── */}
        <input
          className="sidebar-input"
          type="text"
          placeholder="Order list URL"
          value={scrapeUrl}
          onChange={(e) => setScrapeUrl(e.target.value)}
        />
        <h3>Setup Driver</h3>
      <div className="store-grid">
        <button
          className="sidebar-btn"
          onClick={() => handleSetupDriver("store1")}
        >
           点我后登录一店
        </button>

        <button
          className="sidebar-btn"
          onClick={handleScrapeStore1}
          disabled={loading1}
          >
          {loading1 ? "Scraping..." : "🔍 Scrape Store1"}
        </button>
        {error1 && <p className="error-text">{error1}</p>}
      </div>
        <div className="store-grid">
        <button
          className="sidebar-btn"
          onClick={() => handleSetupDriver("store2")}
        >
          点我后登录二店
        </button>

      
        <button
          className="sidebar-btn"
          onClick={handleScrapeStore2}
          disabled={loading2}
        >
          {loading2 ? "Scraping..." : "🔍 Scrape Store2"}
        </button>
        {error2 && <p className="error-text">{error2}</p>}
        </div>

        <div className="store-grid">
        <button
          className="sidebar-btn"
          onClick={() => handleSetupDriver("store3")}
          >
          点我后登录三店
        </button>

        <button
          className="sidebar-btn"
          onClick={handleScrapeStore3}
          disabled={loading3}
          >
          {loading3 ? "Scraping..." : "🔍 Scrape Store3"}
        </button>
        {error3 && <p className="error-text">{error3}</p>}
        </div>

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
          {/* Main log area */}
        <main className="log-container">
        <div className="log-header">
          <h3>Scraper Logs</h3>
          <button
            onClick={() => setLogs([])}
            style={{ marginLeft: "auto" }}
          >
            Clear
          </button>
        </div>

        <div className="log-messages">
          {logs.length === 0 ? (
            <div className="log-empty">No logs yet...</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="log-line">
                {log}
              </div>
            ))
          )}
        </div>
      </main>
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
