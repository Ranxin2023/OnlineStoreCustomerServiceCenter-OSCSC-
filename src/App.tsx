import { useState, useEffect, useRef} from "react";
import "./App.css";
import { io } from "socket.io-client";
import { setAliAIIMUrl, handleSetupDriver, handleScrape, 
  handleExportOrders, handleOpenChat, handleDownloadSA, handleFetchingUsers} from "./handleFunctions.ts"
import { STORE_CHANNEL_ID, STORE_URLS } from "./constants.ts";

// setup socket
const socket = io(`${import.meta.env.VITE_LOCALHOST_API_URL}`);
function App() {
  const chatRef=useRef<HTMLDivElement | null>(null);
  // ─——————————─chat input 定义 ──────────────────────────────────
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  // const helloMessage="Hello!"
  const [scrapeUrl, setScrapeUrl] = useState("https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196");
  // const [users, setUsers]=useState<any[]>([])
  // ─——————————─ loading定义 ──────────────────────────────────
  const [fetchYanwenLoading, setFetchUYanwenLoading] = useState<boolean>(false)
  const [fetchUserLoading1, setFetchUserLoading1] = useState<boolean>(false)
  const [fetchUserLoading2, setFetchUserLoading2] = useState<boolean>(false)
  const [fetchUserLoading3, setFetchUserLoading3] = useState<boolean>(false)
  const [scrapeLoading1, setScrapeLoading1] = useState<boolean>(false);
  const [scrapeLoading2, setScrapeLoading2] = useState<boolean>(false);
  const [scrapeLoading3, setScrapeLoading3] = useState<boolean>(false);
  const [scrapeSALoading, setScrapeSALoading] = useState<boolean>(false);
  const [openPageLoading1, setOpenPageLoading1] = useState<boolean>(false);
  const [openPageLoading2, setOpenPageLoading2] = useState<boolean>(false);
  const [openPageLoading3, setOpenPageLoading3] = useState<boolean>(false);
  // ─——————————─ error message定义 ──────────────────────────────────
  const [fetchYanwenError, setFetchYanwenError]=useState<string | null>(null);
  const [scrapyError1, setScrapyError1] = useState<string | null>(null);
  const [scrapyError2, setScrapyError2] = useState<string | null>(null);
  const [scrapyError3, setScrapyError3] = useState<string | null>(null);
  const [message, setMessage] = useState<string>("Hello! Welcome to Huatong Signal Booster Store. How can I help you today? ");
  const [messageError1, setMessageError1] = useState<string | null>(null);
  const [messageError2, setMessageError2] = useState<string | null>(null);
  const [messageError3, setMessageError3] = useState<string | null>(null);
  const [fetchUserError1, setFetchUserError1] = useState<string | null>(null)
  const [fetchUserError2, setFetchUserError2] = useState<string | null>(null)
  const [fetchUserError3, setFetchUserError3] = useState<string | null>(null)
  
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
  
  // ─————————─ scroll view ──────────────────────────────────
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [chatMessages]);
    

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
 
  // ──———————————————————— 处理客服一店输入 ──────────────────────────────
  const handleOpenChat1 = async (channelId:string) => {

    const url =setAliAIIMUrl(channelId)

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
  const handleOpenChat2 = async (channelId:string) => {
    const url =setAliAIIMUrl(channelId)
      

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
  const handleOpenChat3 = async (channelId: string) => {
    const url =setAliAIIMUrl(channelId)
    
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
    const url = setAliAIIMUrl(channelId)
    await handleFetchingUsers(
      channelId, url,
      // setUsers,
      setFetchUserError1, 
      setFetchUserLoading1, 
      addLog
    )
  }
  // ──———————————————————— 处理客服二店用户获取 ──────────────────────────────
  const handleFetchingUsers2=async()=>{
    const channelId=STORE_CHANNEL_ID.store2
    const url = setAliAIIMUrl(channelId)
    await handleFetchingUsers(
      channelId, url, 
      // setUsers,
      setFetchUserError2,
      setFetchUserLoading2,
      addLog
    )
  }
  // ──———————————————————— 处理客服三店用户获取 ──────────────────────────────
  const handleFetchingUsers3=async()=>{
    const channelId=STORE_CHANNEL_ID.store3
    const url = setAliAIIMUrl(channelId)
    await handleFetchingUsers(
      channelId, url, 
      // setUsers,
      setFetchUserError3,
      setFetchUserLoading3,
      addLog
    )
  }
  // ──———————————————————— 处理发消息程序 ──────────────────────────────
  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    const userMsg = { role: "user", text: chatInput };

    setChatMessages(prev => [...prev, userMsg]);

    try {
      const res = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/chat/rag`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: chatInput
          })
        }
      );

      const data = await res.json();
      
      const botMsg = {
        role: "bot",
        text: data.answer
      };
      
      setChatMessages(prev => [...prev, botMsg]);
      
    } catch (err) {
      console.error(err);
      
      setChatMessages(prev => [
        ...prev,
        { role: "bot", text: "Error connecting to server." }
      ]);
    }
    
    setChatInput("");
  };
  // ──———————————————————— 处理获取燕文信息 ──────────────────────────────
  const fetchingYanwenOrders = async () => {
  setFetchUYanwenLoading(true);

  try {
    const res = await fetch(`${import.meta.env.VITE_LOCALHOST_API_URL}/api/yanwen/fetch-all`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        tracking_number: "YOUR_TRACKING_NUMBER", // 👈 这里你可以传订单号
      }),
    });

    const data = await res.json();

    if (!res.ok){
      setFetchYanwenError(data.error || "Failed to fetch Yanwen orders");
      return;
    }

    console.log("Yanwen result:", data);
  } catch (err: any) {
    setFetchYanwenError(err.message||"Network Error")
    console.error(err.message);
  } finally {
    setFetchUYanwenLoading(false);
  }
};
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
            onClick={()=>handleDownloadSA(setScrapeSALoading)}
            >
            {scrapeSALoading? "Downloading":"🇸🇦 Download Saudi Orders"}
          </button>
        </div>

        {/* ── 订单详情爬取 ── */}
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
        <hr style={{ width: "100%", borderColor: "#444", margin: "12px 0" }} />
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
            onClick={()=>handleOpenChat1(STORE_CHANNEL_ID.store1)}
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
            onClick={()=>handleOpenChat2(STORE_CHANNEL_ID.store2)}
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
            onClick={()=>handleOpenChat3(STORE_CHANNEL_ID.store3)}
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
        {/* <div className="user-list-panel">
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
        </div> */}
        <hr style={{ width: "100%", borderColor: "#444", margin: "12px 0" }} />
        <h3>Open Chat Page</h3>
        <div className="store-grid">
              <button
            className="sidebar-btn"
            onClick={()=>fetchingYanwenOrders()}
            disabled={openPageLoading3}
            >
              {fetchYanwenLoading?"💬Fetching Yanwen": "💬 Fetch Yanwen Orders"}
            
          </button>
          {fetchYanwenError && <p className="error-text">{fetchYanwenError}</p>}
        </div>
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
        <div className="log-header">
          <h3 style={{color: "white"}}>Customer Service Chat</h3>
          <button
            onClick={() => setChatMessages([])}
            style={{ marginLeft: "auto"}}
          >
            Clear
          </button>
        </div>
        <div className="chat-messages" ref={chatRef}>
           {chatMessages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSendMessage();
            }}
          />

          <button onClick={handleSendMessage}>Send</button>
        </div>
      </main>
      
    </div>
  );
}

export default App;
