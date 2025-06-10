#include <Trade/Trade.mqh>

// Input Variables
input double lotSize = 0.01;
input int magicNumber = 24681012;
input int maxTrades = 2;
input string backendBaseURL = "http://127.0.0.1:8000";

// Global Variables
CTrade trade;
int totalTrades = 0;
datetime lastTradeTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization                                            |
//+------------------------------------------------------------------+
int OnInit() {
  // Perform backend connection check
  if (!pingBackend()) {
    Print("Backend connection failed.");
    return INIT_FAILED;
  }
  
  trade.SetExpertMagicNumber(magicNumber);
  trade.SetTypeFilling(ORDER_FILLING_IOC);
  
  Print("IBKR_Replicator initialized.");
  return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert tick                                                      |
//+------------------------------------------------------------------+
void OnTick() {
  datetime now = TimeCurrent();
  
  if (totalTrades >= maxTrades || now - lastTradeTime < 10) {
    return;
  }
  
  double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
  bool trade_result = trade.Buy(lotSize, _Symbol, price, 0, 0);
  
  if(trade_result) {
    Print("Trade #", totalTrades + 1, " executed successfully.");
    totalTrades++;
    lastTradeTime = now;
    
    // Send request to backend
    sendOrderToIBKR("BUY", _Symbol, lotSize);
  } else {
     Print("Trade failed. Error: ", GetLastError());
  }
}

//+------------------------------------------------------------------+
//| Ping FastAPI backend to check connection                         |
//+------------------------------------------------------------------+
bool pingBackend() {
  char resultData[];
  char emptyData[];
  string resultHeaders;
  ResetLastError();
  
  int response = WebRequest(
    "GET",
    backendBaseURL + "/ping",
    "", // No custom headers
    5000,
    emptyData,
    resultData,
    resultHeaders
  );
  
  if (response != 200) {
    Print("Ping to backend failed. HTTP Code: ", response, " Error: ", GetLastError());
    return false;
  }
  
  string reply = CharArrayToString(resultData);
  Print("Ping backend successful. Response: ", reply);
  return true;
}


//+------------------------------------------------------------------+
//| Send trade info to IBKR backend                                  |
//+------------------------------------------------------------------+
void sendOrderToIBKR(string direction, string symbol, double volume) {
  string json = StringFormat("{\"action\":\"NEW_ORDER\",\"symbol\":\"%s\",\"direction\":\"%s\",\"volume\":%.2f}",
                            symbol, direction, volume);
  
  char postData[];
  StringToCharArray(json, postData, 0, StringLen(json));
  
  char resultData[];
  string resultHeaders;
  
  ResetLastError();
  int response = WebRequest(
    "POST",
    backendBaseURL + "/order",
    "Content-Type: application/json\r\n",
    5000,
    postData,
    resultData,
    resultHeaders
  );
  
  if (response != 200) {
    Print("Backend request failed. HTTP Code: ", response, " Error: ", GetLastError());
  } else {
    string jsonResponse = CharArrayToString(resultData);
    Print("Backend response: ", jsonResponse);
  }
}
