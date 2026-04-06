import type { Store } from "./constants";
import { STORE_CHANNEL_ID } from "./constants";
//  ————————── set ali url ──────────────────────────────
export const setAliAIIMUrl=(channelId: string):string=>{
  return `https://csp.aliexpress.com/m_apps/ai-im/im?channelId=${channelId}#/window`
}
// ————————── 处理driver建立 ─────────────────────────────
  
 export const handleSetupDriver = async (store: Store) => {
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
  export const handleScrape = async (
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
  
  // ──—————————— 处理所有订单Export ──────────────────────────────
  
 export const handleExportOrders = async (addLog: (msg: string) => void) => {
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

   // ──—————————————————————————————— 处理客服输入 ──────────────────────────────
  export const handleOpenChat = async (
    url: string, 
    channelId: string, 
    setError: React.Dispatch<React.SetStateAction<string | null>>,
    setLoading: React.Dispatch<React.SetStateAction<boolean>>,
    addLog: (msg: string) => void, 
    message: string
  ) => {

    addLog(`Opening chat window for channel ${channelId}`)
    setLoading(true)

    try {

      const openChatResponse = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/chat/open`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            url: url,
            channelId: channelId,
            message: message
          })
        }
      )

      if (!openChatResponse.ok) {
        throw new Error("Failed to open chat")
      }

      addLog(`Chat opened for channel ${channelId}`)

      // 启动 listener
      const listenerResponse=await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/chat/start-listener`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            channelId: channelId
          })
        }
      )
      const listenerData=await listenerResponse.json()
      if (!listenerResponse.ok) {
        throw new Error(listenerData.error || "Listener failed")
      }

      addLog(`Chat listener started for ${channelId}`)

    } catch (err: any) {

      setError(err.message || "Chat open failed")
      addLog(`Chat open failed: ${err.message}`)

    } finally {

      setLoading(false)

    }
  }

  // ──—————————— 处理沙特订单导出 ──────────────────────────────
  export const handleDownloadSA = async ( setLoading: React.Dispatch<React.SetStateAction<boolean>>) => {
    setLoading(true)
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
    finally{
      setLoading(false)
    }
    
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
   // ──———————————————————— Handle Fetching Users ──————————————————————
  export const handleFetchingUsers = async (
    channelId: string, 
    url:string,
    // setUsers: React.Dispatch<React.SetStateAction<any[]>>,
    setError: React.Dispatch<React.SetStateAction<string | null>>,
    setLoading: React.Dispatch<React.SetStateAction<boolean>>,
    addLog: (msg: string) => void, 
) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `${import.meta.env.VITE_LOCALHOST_API_URL}/api/chat/users`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            channelId: channelId,
            url:url
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch users");
      }

      // setUsers(data.users);

    } catch (err: any) {
      setError(err.message || "User fetching failed")
      addLog(`User fetching failed: ${err.message}`)
    }
    finally{
        setLoading(false)
    }
  };