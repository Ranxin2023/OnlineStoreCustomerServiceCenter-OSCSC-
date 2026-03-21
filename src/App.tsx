import { useState, useEffect} from "react";
import "./App.css";
import { io } from "socket.io-client";
import { handleSetupDriver, handleScrape, handleExportOrders, handleOpenChat, handleDownloadSA, handleFetchingUsers} from "./handleFunctions.ts"
import { STORE_CHANNEL_ID, STORE_URLS } from "./constants.ts";

// setup socket
const socket = io(`${import.meta.env.VITE_LOCALHOST_API_URL}`);
// interface OrderDetail {
//   recipient: string;
//   address: string;
//   postal_code: string;
//   email: string;
//   phone: string;
//   tax_number: string;
// }

// interface DetailResult {
//   data: OrderDetail;
//   unmasked: boolean;
//   clicked_by: string | null;
//   debug_elements: any[];
// }



function App() {
  // const helloMessage="Hello!"
  const [scrapeUrl, setScrapeUrl] = useState("https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196");
  const [users, setUsers]=useState<any[]>([])
  // ─——————————─ loading定义 ──────────────────────────────────
  const [scrapeLoading1, setScrapeLoading1] = useState<boolean>(false);
  const [scrapeLoading2, setScrapeLoading2] = useState<boolean>(false);
  const [scrapeLoading3, setScrapeLoading3] = useState<boolean>(false);
  const [openPageLoading1, setOpenPageLoading1] = useState<boolean>(false);
  const [openPageLoading2, setOpenPageLoading2] = useState<boolean>(false);
  const [openPageLoading3, setOpenPageLoading3] = useState<boolean>(false);
  const [fetchUserLoading1, setFetchUserLoading1]=useState<boolean>(false)
  const [fetchUserLoading2, setFetchUserLoading2]=useState<boolean>(false)
  const [fetchUserLoading3, setFetchUserLoading3]=useState<boolean>(false)
  // ─——————————─ error message定义 ──────────────────────────────────
  const [scrapyError1, setScrapyError1] = useState<string | null>(null);
  const [scrapyError2, setScrapyError2] = useState<string | null>(null);
  const [scrapyError3, setScrapyError3] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("Hello! Welcome to Huatong Signal Booster Store. How can I help you today? ");
  const [messageError1, setMessageError1] = useState<string | null>(null);
  const [messageError2, setMessageError2] = useState<string | null>(null);
  const [messageError3, setMessageError3] = useState<string | null>(null);
  const [fetchUserError1, setFetchUserError1]=useState<string | null>(null)
  const [fetchUserError2, setFetchUserError2]=useState<string | null>(null)
  const [fetchUserError3, setFetchUserError3]=useState<string | null>(null)
  
  // ─————————─ 订单详情爬取 ──────────────────────────────────
  // const [detailUrl, setDetailUrl] = useState("");
  // const [detailLoading, setDetailLoading] = useState(false);
  // const [detailError, setDetailError] = useState<string | null>(null);
  // const [detailResult, setDetailResult] = useState<DetailResult | null>(null);
  
  // ─————————─ 日志获取 ──────────────────────────────────
  const [logs, setLogs] = useState<string[]>([]);
  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };
  // ─————————─ socket建立 ──────────────────────────────────
  useEffect(() => {
    socket.on("connect", () => {
      console.log("Socket connected");
      addLog("Socket connected");
    });
    socket.on("scrape_log", (data) => {
      console.log("SCRAPE LOG:", data);
      addLog(data.msg);
    });
    return () => {
      socket.off("scrape_log");
    };
  }, []);
 
  

  // ──—————————— 处理订单爬取一店 ──────────────────────────────
  const handleScrapeStore1 = async () => {
    addLog("Start scraping Store1");
    const url=STORE_URLS.store1
    handleScrape(url, setScrapyError1, setScrapeLoading1)
    if(!openPageLoading1)
    addLog("Finished scraping Store1");
  };
  
  // ──—————————— 处理订单爬取二店 ──────────────────────────────
  const handleScrapeStore2 = async () => {
    addLog("Start scraping Store2");
    const url=STORE_URLS.store2
    handleScrape(url, setScrapyError2, setScrapeLoading2)
    if(!openPageLoading2)
    addLog("Finished scraping Store2");
    
  };
  
  // ──—————————— 处理订单爬取三店 ──────────────────────────────
  const handleScrapeStore3 = async () => {
    addLog("Start scraping Store3...");
    const url=STORE_URLS.store3
    handleScrape(url, setScrapyError3, setScrapeLoading3)
    if(!openPageLoading3)
    addLog("Finished scraping Store3...");
  };

  

  // ──—————————— 处理订单详情爬取 ──────────────────────────────
  // const handleScrapeDetail = async () => {
  //   if (!detailUrl.startsWith("http")) {
  //     setDetailError("Please enter a valid URL");
  //     return;
  //   }
  //   setDetailLoading(true);
  //   setDetailError(null);
  //   setDetailResult(null);
  //   try {
  //     const response = await fetch(`${import.meta.env.LOCALHOST_URL}/api/web-scrapy/scrape-detail`, {
  //       method: "POST",
  //       headers: { "Content-Type": "application/json" },
  //       body: JSON.stringify({ url: detailUrl }),
  //     });
  //     const json = await response.json();
  //     if (!response.ok) throw new Error(json.error || "Failed to scrape detail");
  //     setDetailResult(json);
  //   } catch (err: any) {
  //     setDetailError(err.message || "Something went wrong");
  //   } finally {
  //     setDetailLoading(false);
  //   }
  // };

  
 
  // ──———————————————————— 处理客服一店输入 ──────────────────────────────
  const handleOpenChat1 = async () => {

  const channelId = STORE_CHANNEL_ID.store1

    const url =
      `https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`

    await handleOpenChat(
      url,
      channelId,
      setMessageError1,
      setOpenPageLoading1, 
      addLog, 
      message
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
      setOpenPageLoading2, 
      addLog, 
      message
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
      setOpenPageLoading3, 
      addLog, 
      message
    )
    
  }
  
  // ──———————————————————— 处理客服一店用户获取 ──────────────────────────────
  const handleFetchingUsers1=async()=>{
    const channelId=STORE_CHANNEL_ID.store1
    const url =`https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`
    await handleFetchingUsers(
      channelId,
      url,
      setUsers,
      setFetchUserError1, 
      setFetchUserLoading1, 
      addLog
    )
  }
  // ──———————————————————— 处理客服二店用户获取 ──────────────────────────────
  const handleFetchingUsers2=async()=>{
    const channelId=STORE_CHANNEL_ID.store2
    const url =`https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`
    await handleFetchingUsers(
      channelId, url, setUsers,
      setFetchUserError2,
      setFetchUserLoading2,
      addLog
    )
  }
  // ──———————————————————— 处理客服三店用户获取 ──────────────────────────────
  const handleFetchingUsers3=async()=>{
    const channelId=STORE_CHANNEL_ID.store3
    const url =`https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`
    await handleFetchingUsers(channelId, url, setUsers,
      setFetchUserError3,
      setFetchUserLoading3,
      addLog
    )
  }
  // ──———————————————————— render page ──────────────────────────────
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
          onClick={()=>handleExportOrders(addLog)}
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
            disabled={scrapeLoading1}
            >
            {scrapeLoading1 ? "Scraping..." : "🔍 Scrape Store1"}
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
            disabled={scrapeLoading2}
            >
            {scrapeLoading2 ? "Scraping..." : "🔍 Scrape Store2"}
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
            disabled={scrapeLoading3}
            >
            {scrapeLoading3 ? "Scraping..." : "🔍 Scrape Store3"}
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
         {/*
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
          */}
        {/* ──—————— chat page部分 ————————── */}
        <h3>Open Chat Page</h3>
         <input
          className="sidebar-input"
          type="text"
          placeholder="Order list URL"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          />
        <div className="store-grid">

          <button
            className="sidebar-btn"
            onClick={handleOpenChat1}
            disabled={openPageLoading1}
            >
            {openPageLoading1?"💬Open Chatting": "💬 Open Chat Page Store1"}
          </button>
          <button
            className="sidebar-btn"
            onClick={handleFetchingUsers1}
            disabled={fetchUserLoading1}
            >
            {fetchUserLoading1?"💬Fetching User List": "💬 Open User List1"}
          </button>
        </div>
          {fetchUserError1 && <p className="error-text">{fetchUserError1}</p>}
        {messageError1 && <p className="error-text">{messageError1}</p>}
        <div className="store-grid">
          <button
            className="sidebar-btn"
            onClick={handleOpenChat2}
            disabled={openPageLoading2}
            >
            
              {openPageLoading2?"💬Open Chatting": "💬 Open Chat Page Store2"}
          </button>
          <button
            className="sidebar-btn"
            onClick={handleFetchingUsers2}
            disabled={fetchUserLoading2}
            >
            
            {fetchUserLoading2?"💬Fetching User List": "💬 Open User List2"}
          </button>
          {fetchUserError2 && <p className="error-text">{fetchUserError2}</p>}
          {messageError2 && <p className="error-text">{messageError2}</p>}
        </div>
        <div className="store-grid">

          <button
            className="sidebar-btn"
            onClick={handleOpenChat3}
            disabled={openPageLoading3}
            >
              {openPageLoading3?"💬Open Chatting": "💬 Open Chat Page Store3"}
            
          </button>
          <button
            className="sidebar-btn"
            onClick={handleFetchingUsers3}
            disabled={fetchUserLoading3}
            >
            {fetchUserLoading3?"💬Fetching User List": "💬 Open User List3"}
            
          </button>
            {fetchUserError3 && <p className="error-text">{fetchUserError3}</p>}
          {messageError3 && <p className="error-text">{messageError3}</p>}
        </div>
        <div className="user-list-panel">
          <h3>👥 Users</h3>

          {users.length === 0 ? (
            <p>No users yet</p>
          ) : (
            users.map((u, i) => (
              <div key={i} className="user-item">
                <p><b>{u.name}</b></p>
                <p>⭐ {u.star || "-"}</p>
                <p>🌍 {u.country || "-"}</p>
              </div>
            ))
          )}
        </div>
        {/* 详情结果展示 */}
        {
        /*
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
        */
      }
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
