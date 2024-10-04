This project focuses on optimising price impacts for large cryptocurrency trades on
Decentralised Exchanges (DEXs). It is evident that crypto traders want to swap
cryptocurrencies in large quantities, however, this leads to greater transaction costs, with
price impact being a significant one. The project covers a strategy that was created and
implemented to reduce the price impacts for crypto traders. This is helpful when traders are
swapping large quantities of tokens (cryptocurrency assets). The Liquidity Seeking algorithm
for DeFi employs two major algorithms, a splitting algorithm, and a Time Weighted Average
Price (TWAP) algorithm. The splitting algorithm splits the amount of token0 (cryptocurrency
a user has) into chunks and iteratively swaps it into token1 (the cryptocurrency the user
wants), and the TWAP algorithm spans out the swaps to ensure liquidity pools are not
overwhelmed by the inflow of tokens in evaluations. The Liquidity Seeking Algorithm has
shown success on liquid pools and can be seen as a competitor to existing DEXs such as
Uniswap.


Python dependencies:
- pip install web3
- pip install requests
- pip install js2py
- pip install flask

npm dependencies
"@uniswap/sdk": "^3.0.3",
"@uniswap/sdk-core": "^3.2.2",
"@uniswap/v3-core": "^1.0.1",
"@uniswap/v3-periphery": "^1.4.3",
"@uniswap/v3-sdk": "^3.9.0",
"dotenv": "^16.0.3",
"ethers": "^5.7.2"

**A guide to running the application**
Open Terminal -> spit terminal
1. Open server:
    in the first terminal do the following:
    cd Backend -> cd LSA -> cd server -> python server.py
2. Open client:
    in the second terminal do the following:
    cd Frontend -> cd dexStarter -> cd dex -> npm start
