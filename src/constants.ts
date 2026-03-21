export type Store = "store1" | "store2" | "store3";
export const STORE_URLS: Record<Store, string>= {
  store1: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=98158",
  store2: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1471480",
  store3: "https://csp.aliexpress.com/m_apps/order-manage/orderList?channelId=1579196",
  
};
export const STORE_CHANNEL_ID: Record<Store, string>= {
  store1: "98158",
  store2: "1471480",
  store3: "1579196",
  
};