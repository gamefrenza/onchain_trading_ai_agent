# AI Trading Agent

An onchain AI trading agent that combines blockchain interaction with machine learning for automated trading.

## Features

- Real-time blockchain monitoring using Web3.py
- Async functionality for improved performance
- TensorFlow-based AI trading model
- FastAPI web interface
- Comprehensive logging and error handling
- Environment-based configuration

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

## API Endpoints

- GET `/api/v1/balance`: Get current ETH balance
- POST `/api/v1/trade`: Execute a trade

## Project Structure

- `src/`: Main source code
  - `api/`: FastAPI routes and endpoints
  - `blockchain/`: Web3 interaction logic
  - `models/`: AI model implementation
  - `config/`: Configuration management
  - `utils/`: Utility functions and logging
- `tests/`: Test files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 