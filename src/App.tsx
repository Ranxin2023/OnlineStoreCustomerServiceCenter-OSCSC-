import { useState, useEffect} from "react";
import "./App.css";
import { io } from "socket.io-client";

const socket = io(`${import.meta.env.VITE_LOCALHOST_API_URL}`);
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
  // const helloMessage="Hello!"
  const [scrapeUrl, setScrapeUrl] = useState("https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196");
  const [loading1, setLoading1] = useState(false);
  const [loading2, setLoading2] = useState(false);
  const [loading3, setLoading3] = useState(false);
  const [scrapyError1, setScrapyError1] = useState<string | null>(null);
  const [scrapyError2, setScrapyError2] = useState<string | null>(null);
  const [scrapyError3, setScrapyError3] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("Hello");
  const [messageError1, setMessageError1] = useState<string | null>(null);
  const [messageError2, setMessageError2] = useState<string | null>(null);
  const [messageError3, setMessageError3] = useState<string | null>(null);

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
  // console.log(`Socket url is:${import.meta.env.VITE_LOCALHOST_API_URL}`)
  // console.log(`Public url is:${import.meta.env.VITE_API_URL}`)
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
  // ————————── 处理driver建立 ──────────────────────────────
  
  const handleSetupDriver = async (store: Store) => {
    try {

      const response = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/web-scrapy/setup-driver`,
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

   // ──—————————— 处理订单爬取 ──────────────────────────────
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
      const response = await fetch(`${import.meta.env.VITE_LOCALHOST_API_URL}/api/web-scrapy/scrape`, {
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
  // ──—————————— 处理订单爬取一店 ──────────────────────────────
  const handleScrapeStore1 = async () => {
    addLog("Start scraping Store1");
    const url=STORE_URLS.store1
    handleScrape(url, setScrapyError1, setLoading1)
    addLog("Finished scraping Store1");
  };
  // ──—————————— 处理订单爬取二店 ──────────────────────────────
  const handleScrapeStore2 = async () => {
    const url=STORE_URLS.store2
    handleScrape(url, setScrapyError2, setLoading2)
    
  };
  // ──—————————— 处理订单爬取三店 ──────────────────────────────
  const handleScrapeStore3 = async () => {
    const url=STORE_URLS.store3
    handleScrape(url, setScrapyError3, setLoading3)
  };

  // ──—————————— 处理订单详情爬取 ──────────────────────────────
  const handleScrapeDetail = async () => {
    if (!detailUrl.startsWith("http")) {
      setDetailError("Please enter a valid URL");
      return;
    }
    setDetailLoading(true);
    setDetailError(null);
    setDetailResult(null);
    try {
      const response = await fetch(`${import.meta.env.LOCALHOST_URL}/api/web-scrapy/scrape-detail`, {
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

  // ──—————————— 处理所有订单爬取 ──────────────────────────────
  
  const handleExportOrders = async () => {
    try {
      addLog("Exporting orders from database...");
      
      const response = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/orders/export`,
        { method: "GET" }
      );

      if (!response.ok) {
        throw new Error("Failed to export orders");
      }

      const blob = await response.blob();
      
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");

      a.href = downloadUrl;
      a.download = "orders.xlsx";
      
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(downloadUrl);

      addLog("Orders exported to Excel");
    } catch (err) {
      console.error(err);
      addLog("Export failed");
    }
  };
  // ──—————————— 处理沙特订单导出 ──────────────────────────────
  const handleDownloadSA = async () => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/orders/sa`
      );
      
      if (!response.ok) {
        throw new Error("Failed to download Saudi orders");
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "SA_orders.xlsx";
      a.click();
      
      window.URL.revokeObjectURL(url);
    } 
    catch (err) {
      alert("Download failed");
    }
    
  };
  // ──—————————————————————————————— 处理客服输入 ──────────────────────────────
  const handleOpenChat = async (
    url: string, 
    channelId: string, 
    setError: React.Dispatch<React.SetStateAction<string | null>>,
    setLoading: React.Dispatch<React.SetStateAction<boolean>>
  ) => {
    
    addLog(`Opening chat window for channel ${channelId}`)
    setLoading(true)
    try {
      
      const response = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/chat/open`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            url: url,
            channelId: channelId,
            message:message
          })
        }
      )
      
      if (!response.ok) {
        throw new Error("Failed to open chat")
      }
      
      addLog(`Chat opened for channel ${channelId}`)
      
    } catch (err: any) {
      setError(err.message || "Chat open failed")
      addLog(`Chat open failed: ${err.message}`)
      
    }
    finally{
      setLoading(false)
    }
    
  }
  // ──———————————————————— 处理客服一店输入 ──────────────────────────────
  const handleOpenChat1 = async () => {

  const channelId = STORE_CHANNEL_ID.store1

    const url =
      `https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`

    await handleOpenChat(
      url,
      channelId,
      setMessageError1,
      setLoading1
    )

  }

  // ──———————————————————— 处理客服二店输入 ──────────────────────────────
  const handleOpenChat2 = async () => {

  const channelId = STORE_CHANNEL_ID.store2

    const url =
      `https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`

    await handleOpenChat(
      url,
      channelId,
      setMessageError2, 
      setLoading2
    )

  }

  // ──———————————————————— 处理客服三店输入 ──────────────────────────────
  const handleOpenChat3 = async () => {

  const channelId = STORE_CHANNEL_ID.store3

    const url =
      `https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`

    await handleOpenChat(
      url,
      channelId,
      setMessageError3,
      setLoading3
    )

  }
 
  return (
    <div className="app-layout">
      {/* Left sidebar */}
      <aside className="sidebar">
        <h2>Hwatel</h2>
        {/*
        <button className="sidebar-btn">Check Prices</button>
        <button className="sidebar-btn">📞 Contact Support</button>
        <button className="sidebar-btn">🧾 My Reservations</button>
        <button className="sidebar-btn">❓ FAQs</button>
        <hr style={{ width: "100%", borderColor: "#444", margin: "12px 0" }} />
        */}
        {/* ── 订单列表爬取 ── */}
        <h3>Scrape the Page</h3>
        <input
          className="sidebar-input"
          type="text"
          placeholder="Order list URL"
          value={scrapeUrl}
          onChange={(e) => setScrapeUrl(e.target.value)}
        />
        
        <button
          className="sidebar-btn"
          onClick={handleExportOrders}
          >
          📥 Export Orders (DB → Excel)
        </button>
        
        {/* ──———————— driver部分 ─——————————─ */}
        <div className="store-grid">
          {/* ──———————— 登录一店 ─——————————─ */}
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
          {scrapyError1 && <p className="error-text">{scrapyError1}</p>}
        </div>
        {/* ──———————— 登录二店 ─——————————─ */}
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
          {scrapyError2 && <p className="error-text">{scrapyError2}</p>}
        </div>

        {/* ──———————— 登录三店 ─——————————─ */}
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
          {scrapyError3 && <p className="error-text">{scrapyError3}</p>}
        </div>
        <div className="store-grid">
          <button
            className="sidebar-btn"
            onClick={handleDownloadSA}
            >
            🇸🇦 Download Saudi Orders
          </button>
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
        <hr style={{ width: "100%", borderColor: "#444", margin: "12px 0" }} />

        {/* ── chat page部分 ── */}
        <h3>Open Chat Page</h3>
         <input
          className="sidebar-input"
          type="text"
          placeholder="Order list URL"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button
          className="sidebar-btn"
          onClick={handleOpenChat1}
          disabled={loading1}
          >
          {loading1?"💬Open Chatting": "💬 Open Chat Page Store1"}
        </button>
        {messageError1 && <p className="error-text">{messageError1}</p>}
        <button
          className="sidebar-btn"
          onClick={handleOpenChat2}
          disabled={loading2}
          >
          
            {loading2?"💬Open Chatting": "💬 Open Chat Page Store2"}
        </button>
        {messageError2 && <p className="error-text">{messageError2}</p>}
        <button
          className="sidebar-btn"
          onClick={handleOpenChat3}
          disabled={loading3}
          >
            {loading3?"💬Open Chatting": "💬 Open Chat Page Store3"}
          
        </button>
        {messageError3 && <p className="error-text">{messageError3}</p>}
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
      
      {/* ---------Main log area--------------- */}
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

      {/*------------ Main chatbot area -----------------*/}
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
