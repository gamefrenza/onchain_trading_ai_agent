Onchain AI Trading Agent (TypeScript)

An AI-assisted on-chain trading agent with a Node.js/TypeScript backend (blockchain listeners, AI service integration, strategies, risk controls) and a React + MUI frontend dashboard.

---

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Blockchain RPC and WebSocket endpoints (e.g., Infura/Alchemy) and a funded private key for a test network

### Install dependencies
```bash
# from repo root
npm install

# frontend
cd web/trading-platform && npm install
```

### Environment
Create a `.env` file in the repo root (used by backend `src/utils/config.ts`):
```bash
# Blockchain
RPC_URL=your_https_rpc_url
WS_URL=your_wss_ws_url
PRIVATE_KEY=your_hex_private_key
CHAIN_ID=1

# AI service (optional)
AI_MODEL_ENDPOINT=https://your.ai.endpoint/predict
AI_API_KEY=your_api_key

# Trading
MIN_TRADE_AMOUNT=0.1
MAX_TRADE_AMOUNT=1.0
TRADING_PAIRS=ETH-USDT

# Logging
LOG_LEVEL=info
```

DEX pair contract addresses live in `src/utils/config.ts` under `CONFIG.DEX.PAIRS`.

### Run
```bash
# backend (development)
npm run dev

# backend (build + run)
npm run build && node dist/index.js

# frontend
cd web/trading-platform && npm start
```

If you do not yet have `src/index.ts`, see Backend Entrypoint below.

---

## Repository Structure
- `src/`
  - `ai/`: AI service client and TensorFlow.js LSTM model utilities
  - `blockchain/`: Ethers-based JSON-RPC and WebSocket listeners, contract ABIs
  - `trading/`: `AITrendStrategy`, risk management, trading engine
  - `utils/`: config, logger, retry helper
- `web/trading-platform/`: React dashboard (CRA)

---

## Backend Overview

### Config
`src/utils/config.ts` loads environment variables and exposes `CONFIG`.

### Blockchain
- `src/blockchain/web3Client.ts`: JSON-RPC provider + wallet for balance and transactions
- `src/blockchain/eventListener.ts`: WebSocket provider and DEX event subscriptions

### AI
- `src/ai/aiService.ts`: HTTP client to external AI inference service
- `src/ai/models/deepLearningModel.ts`: TensorFlow.js LSTM model (build/train/predict)

### Strategy & Risk
- `src/trading/strategies/aiTrendStrategy.ts`: combines AI prediction with RSI/MACD to produce trade signals
- `src/trading/risk/riskManager.ts`: position sizing, SL/TP calculation, risk constraints

### Trading Engine
`src/trading/tradingEngine.ts` coordinates blockchain listeners, AI predictions, and monitoring loop.

---

## Backend Entrypoint
Root `package.json` specifies `start: ts-node src/index.ts`, but `src/index.ts` is not present. Create it like:

```typescript
import { TradingEngine } from './trading/tradingEngine';
import { logger } from './utils/logger';

async function main() {
  try {
    const engine = new TradingEngine();
    await engine.startTrading();
  } catch (err) {
    logger.error('Fatal error starting engine', err);
    process.exit(1);
  }
}

main();
```

Then run:
```bash
npm run dev
```

---

## Frontend Overview
- Location: `web/trading-platform`
- Tech: React 18, React Router, MUI
- Start dev server:
```bash
cd web/trading-platform && npm start
```

Key files:
- `src/App.tsx`: routes and providers (auth, websocket)
- `src/pages/Dashboard.tsx`: dashboard view
- `src/components/trading/*`: chart and controls

---

## Testing
- Backend: Jest at root (`npm test`). Add test files under `src/**/__tests__` or `*.test.ts`.
- Frontend: CRA testing via `react-scripts test` in `web/trading-platform`.

---

## Notes & Caveats
- Ethers v6 vs v5 API: code uses `ethers.providers.*` (v5-style) while `package.json` pins `ethers@^6`. Align the code to v6 (e.g., `new ethers.JsonRpcProvider`, `new WebSocketProvider`) or pin ethers v5.
- Keep private keys secure; prefer environment variables and test networks.
- Replace example contract addresses in `CONFIG.DEX.PAIRS` with correct ones for your network.
- Long-running loops and WebSocket listeners should include robust reconnect/shutdown logic.

---

## License
MIT (or your preferred license)
