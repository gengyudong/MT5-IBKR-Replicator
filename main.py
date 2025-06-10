from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from ib_insync import IB, Forex, MarketOrder, Contract
import asyncio
from contextlib import asynccontextmanager
from pydantic_models import NewOrderRequest
from symbols import get_ibkr_symbol, get_ibkr_conid, get_ibkr_currency

ib = IB()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to IBKR...")
    await ib.connectAsync("127.0.0.1", 7497, clientId=1)
    print("Connected to IBKR.")
    yield
    print("Disconnecting from IBKR...")
    ib.disconnect()
    print("Disconnected.")

app = FastAPI(lifespan=lifespan)

async def check_ib_connection():
    if not ib.isConnected():
        print("Connecting to IBKR...")
        try:
            await ib.connectAsync("127.0.0.1", 7497, clientId=1)
            print("Connected to IBKR.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to IBKR: {str(e)}")

@app.get("/ping")
async def ping():
    print("Received ping from MT5")
    try:
        await check_ib_connection()  # Ensure connection is active
        print("IBKR connection is active.")
        return JSONResponse(status_code=200, content={"status": "OK"})
    
    except Exception as e:
        print("Order placement failed:", e)
        raise HTTPException(status_code=500, detail=f"Backend ping failed: {str(e)}")


@app.post("/order")
async def handle_order(order: NewOrderRequest):
    action = order.action.upper()
    symbol = order.symbol
    direction = order.direction
    volume = order.volume * 100000  # In IBKR, order quantities are always in base currency units, not "lots"
    
    if action.upper() != "NEW_ORDER":
        return JSONResponse(status_code=400, content={
            "status": "ERROR",
            "message": "Invalid action"
        })

    try:
        await check_ib_connection()  # Ensure connection is active
        
        print(f"Received order: {direction} {volume} of {symbol}")
        
        contract_Id = get_ibkr_conid(symbol)
        contract_symbol = get_ibkr_symbol(symbol)
        contract_currency = get_ibkr_currency(symbol)
        
        contract = Contract()
        contract.conId = contract_Id
        contract.symbol = contract_symbol
        contract.secType = "CFD"
        contract.exchange = "SMART"
        contract.currency = contract_currency

        await ib.qualifyContractsAsync(contract)
        
        order = MarketOrder(direction, volume)
        trade = ib.placeOrder(contract, order)
        
        await asyncio.sleep(1)

        return {
            "Backend status": "OK",
            "orderStatus": trade.orderStatus.status,
            "orderId": trade.order.orderId
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "ERROR",
            "message": str(e),
            "error_type": type(e).__name__
        })
        