import { ethers } from 'ethers';

export const DEX_ABI = [
  'event Trade(address indexed maker, address indexed taker, address indexed pair, uint256 amount, uint256 price, uint256 timestamp)',
  'event Swap(address indexed sender, uint256 amount0In, uint256 amount1In, uint256 amount0Out, uint256 amount1Out, address indexed to)',
];

export interface TradeEvent {
  maker: string;
  taker: string;
  pair: string;
  amount: string;
  price: string;
  timestamp: number;
  transactionHash: string;
  blockNumber: number;
}

export interface SwapEvent {
  sender: string;
  amount0In: string;
  amount1In: string;
  amount0Out: string;
  amount1Out: string;
  to: string;
  transactionHash: string;
  blockNumber: number;
} 