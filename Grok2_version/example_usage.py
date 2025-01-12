import asyncio
from blockchain_data import BlockchainDataFetcher

async def example_callback(tx):
    """Example callback for mempool monitoring"""
    print(f"New pending transaction: {tx}")

async def main():
    fetcher = BlockchainDataFetcher()
    
    # Fetch latest Ethereum transactions
    transactions = await fetcher.get_latest_eth_transactions(num_blocks=2)
    print("\nLatest Ethereum transactions:")
    for tx in transactions[:5]:  # Show first 5 transactions
        print(f"Hash: {tx['hash']}, Value: {tx['value']} ETH")

    # Fetch USDT transfers (USDT contract address on Ethereum)
    usdt_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
    token_transfers = await fetcher.get_token_transfers(usdt_address)
    print("\nRecent USDT transfers:")
    for transfer in token_transfers[:5]:  # Show first 5 transfers
        print(f"From: {transfer['from']}, To: {transfer['to']}, Value: {transfer['value']}")

    # Fetch DEX trades
    dex_trades = await fetcher.get_dex_trades()
    print("\nRecent DEX trades:")
    for trade in dex_trades[:5]:  # Show first 5 trades
        print(f"Symbol: {trade['symbol']}, Price: {trade['price']}, Amount: {trade['amount']}")

    # Monitor mempool (runs indefinitely)
    print("\nStarting mempool monitoring...")
    await fetcher.monitor_mempool(example_callback)

if __name__ == "__main__":
    asyncio.run(main()) 