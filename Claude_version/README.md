# AI Trading Agent

An onchain AI trading agent that combines blockchain interaction with machine learning for automated trading.

## Features

- Real-time blockchain monitoring using Web3.py
- Async functionality for improved performance
- TensorFlow-based AI trading model
- FastAPI web interface
- Comprehensive logging and error handling
- Environment-based configuration

## Core Components

### Trading Strategies (`src/trading/strategy.py`)
- Abstract base class for trading strategies
- MACD and RSI strategy implementations
- Strategy execution pipeline with confidence scoring
- Risk management integration

### Configuration (`src/config/settings.py`)
- Environment-based settings
- Blockchain configuration
- API settings
- Model parameters
- Trading pair definitions

### Data Processing (`src/data/data_processor.py`)
- Market data preprocessing
- Technical indicator calculation
- Feature engineering
- Data normalization
- Sequence preparation

### Application Core (`src/main.py`)
- FastAPI app and routing
- WebSocket endpoint `/ws/trades`
- Event service lifecycle hooks
- Centralized logging and error handling

### Models

#### Backtesting (`src/models/backtesting.py`)
- Historical performance simulation
- Performance metrics calculation
- Risk analysis
- Trade execution simulation
- Strategy validation

#### Technical Indicators (`src/models/indicators.py`)
- RSI calculation
- MACD implementation
- Bollinger Bands
- Momentum indicators
- Trend analysis

#### Risk Management (`src/models/risk_management.py`)
- Position sizing
- Stop-loss calculation
- Risk rule application
- Trade validation
- Portfolio exposure management

#### Trading Model (`src/models/trading_model.py`)
- Deep learning model architecture
- Training pipeline
- Prediction generation
- Model validation
- Performance metrics

### Services

#### Event Service (`src/services/event_service.py`)
- Blockchain event monitoring
- Trade event processing
- WebSocket broadcasting
- Event persistence
- Error handling

#### Trading Service (`src/services/trading_service.py`)
- Trade execution
- Strategy coordination
- Model prediction handling
- Transaction management
- Error recovery

### Testing

#### Unit Tests
- Risk management testing (`tests/unit/test_risk_management.py`)
- Trading model validation (`tests/unit/test_trading_model.py`)
- Component isolation testing
- Error handling verification

#### Integration Tests
- Trading service testing (`tests/integration/test_trading_service.py`)
- End-to-end workflow validation
- System integration verification
- Performance testing

#### UI Testing
- Component rendering (`tests/ui/test_components.tsx`)
- User interaction testing
- WebSocket functionality
- Error state handling

#### Test Configuration
- Test fixtures (`tests/conftest.py`)
- Mock data generation
- Test environment setup
- Dependency injection

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your configuration
5. Run the application:
   ```bash
   python src/main.py
   ```

## Development

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/ui/

# Run with coverage
pytest --cov=src tests/
```

### Local Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Watch for changes
docker-compose -f docker-compose.dev.yml logs -f
```

### Production Deployment
```bash
# Deploy to production
./deployment/scripts/deploy.sh
```

## API Endpoints

- POST `/api/v1/token`: Obtain access token (OAuth2 password flow)
- GET `/api/v1/user/me`: Get current user
- POST `/api/v1/trade`: Execute a trade
- GET `/api/v1/predictions`: Get model predictions
- GET `/api/v1/performance`: Get trading performance
- GET `/api/v1/strategies`: List available strategies
- POST `/api/v1/strategies/configure`: Configure strategy
- GET `/api/v1/health`: Service health status

## WebSocket Endpoints

- `/ws/trades`: Real-time trade updates
## Environment Variables

Create a `.env` file based on `.env.example`:

```env
WEB3_PROVIDER_URI=
WS_PROVIDER_URI=
WALLET_ADDRESS=
PRIVATE_KEY=
SECRET_KEY=
API_HOST=0.0.0.0
API_PORT=8000
MODEL_PATH=models/trained_model
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trading_db
REDIS_URL=redis://localhost:6379/0
```

## Docker

- Development: `docker-compose -f docker-compose.dev.yml up`
- Production: `docker-compose -f docker-compose.prod.yml up -d`

Notes:
- Production compose uses `redis:6-alpine` and initializes Postgres with `deployment/db/init.sql`.
- Nginx serves the built frontend and proxies `/api` and `/ws` to the backend.
- `/ws/predictions`: Live model predictions
- `/ws/performance`: Performance metric updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 