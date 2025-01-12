from web3 import Web3
import pandas as pd
import logging
from datetime import datetime
import json
import os
from dotenv import load_load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='uniswap_trading.log'
)

# Load environment variables
load_dotenv()

# Uniswap V2 WETH/USDC pair contract address on mainnet
UNISWAP_V2_PAIR = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'

# Token addresses
WETH_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
USDC_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'

# ABI for Uniswap V2 Pair contract - minimum required for swap events
UNISWAP_V2_PAIR_ABI = json.loads('''[
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "sender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "amount0In",
                "type": "uint256"
            },
            {
                "indexed": false,
                "name": "amount1In",
                "type": "uint256"
            },
            {
                "indexed": false,
                "name": "amount0Out",
                "type": "uint256"
            },
            {
                "indexed": false,
                "name": "amount1Out",
                "type": "uint256"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            }
        ],
        "name": "Swap",
        "type": "event"
    }
]''')

class UniswapDataFetcher:
    def __init__(self):
        try:
            # Initialize Web3 with your Ethereum node
            self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_NODE_URL')))
            
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Ethereum node")
            
            self.pair_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(UNISWAP_V2_PAIR),
                abi=UNISWAP_V2_PAIR_ABI
            )
            logging.info("Successfully initialized UniswapDataFetcher")
            
        except Exception as e:
            logging.error(f"Initialization error: {str(e)}")
            raise

    def fetch_swap_events(self, from_block, to_block=None):
        """
        Fetch Swap events from the Uniswap V2 WETH/USDC pair
        """
        try:
            if to_block is None:
                to_block = self.w3.eth.block_number

            logging.info(f"Fetching swap events from block {from_block} to {to_block}")
            
            # Get swap events
            swap_events = self.pair_contract.events.Swap.get_logs(
                fromBlock=from_block,
                toBlock=to_block
            )
            
            # Process events into a list of dictionaries
            processed_events = []
            for event in swap_events:
                # Calculate price and volume
                if event.args.amount1In > 0:
                    price = event.args.amount1In / (10**6) / (event.args.amount0Out / (10**18))
                    volume_usdc = event.args.amount1In / (10**6)
                elif event.args.amount1Out > 0:
                    price = event.args.amount1Out / (10**6) / (event.args.amount0In / (10**18))
                    volume_usdc = event.args.amount1Out / (10**6)
                else:
                    continue

                # Get block timestamp
                block = self.w3.eth.get_block(event.blockNumber)
                
                processed_events.append({
                    'timestamp': datetime.fromtimestamp(block.timestamp),
                    'block_number': event.blockNumber,
                    'transaction_hash': event.transactionHash.hex(),
                    'price_usdc_per_eth': price,
                    'volume_usdc': volume_usdc,
                    'sender': event.args.sender,
                    'receiver': event.args.to
                })
            
            # Create DataFrame
            df = pd.DataFrame(processed_events)
            logging.info(f"Successfully processed {len(processed_events)} swap events")
            return df
            
        except Exception as e:
            logging.error(f"Error fetching swap events: {str(e)}")
            raise

def main():
    try:
        fetcher = UniswapDataFetcher()
        
        # Fetch last 100 blocks of swap data
        current_block = fetcher.w3.eth.block_number
        from_block = current_block - 100
        
        df = fetcher.fetch_swap_events(from_block)
        
        # Save to CSV
        output_file = 'uniswap_swaps.csv'
        df.to_csv(output_file, index=False)
        logging.info(f"Data saved to {output_file}")
        
        # Display summary
        print("\nData Summary:")
        print(f"Number of swaps: {len(df)}")
        print(f"Average USDC/ETH price: {df['price_usdc_per_eth'].mean():.2f}")
        print(f"Total USDC volume: {df['volume_usdc'].sum():,.2f}")
        
    except Exception as e:
        logging.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 