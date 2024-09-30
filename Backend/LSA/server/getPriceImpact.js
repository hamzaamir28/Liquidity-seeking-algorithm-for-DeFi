const {ethers, JsonRpcProvider, BigNumber} = require('ethers')

const { abi: QuoterV2ABI } = require('@uniswap/v3-periphery/artifacts/contracts/lens/QuoterV2.sol/QuoterV2.json')
const { abi: PoolABI } = require('@uniswap/v3-core/artifacts/contracts/UniswapV3Pool.sol/UniswapV3Pool.json')
const { abi: FactoryABI } = require("@uniswap/v3-core/artifacts/contracts/UniswapV3Factory.sol/UniswapV3Factory.json")

// npm dependencies
// "@uniswap/sdk": "^3.0.3",
// "@uniswap/sdk-core": "^3.2.2",
// "@uniswap/v3-core": "^1.0.1",
// "@uniswap/v3-periphery": "^1.4.3",
// "@uniswap/v3-sdk": "^3.9.0",
// "dotenv": "^16.0.3",
// "ethers": "^5.7.2"

const ECR20ABI = require('./erc20.json')
const WETHABI = require('./weth.json')

const QUOTER2_ADDRESS = '0x61fFE014bA17989E743c5F6cB21bF9697530B21e'
const FACTORY_ADDRESS = '0x1F98431c8aD98523631AE4a59f267346ea31F984'
const WETH_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
const USDC_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'

INFURA_URL = ""

const provider = new ethers.providers.JsonRpcProvider(INFURA_URL)

const getAbi = address => address === WETH_ADDRESS ? WETHABI : ECR20ABI

function sqrtToPrice(sqrt, decimal0, decimal1, token0IsInput=true){

    //price = (sqrtPriceX96^2)/(2^192)
    const numerator = sqrt ** 2
    const denominator = 2 ** 192
    let ratio = numerator / denominator

    //ratio (price) should be formatted to consider decimals of token0 and token1
    const shiftDecimals = Math.pow(10, decimal0 - decimal1)
    ratio = ratio * shiftDecimals
    
    //check if token0 inputted by user == token0 in the liquidity pool
    if(!token0IsInput){
        ratio = 1/ratio
    }
    
    return ratio
}

async function getPI(tokenIn, tokenOut, fee, amountIn, poolAdress, decimalsIn, decimalsOut){
    //amountIn is BigNumber, let code know that
    amountIn= BigNumber.from(amountIn)

    //use Uniswap liquidity pool contract to get sqrtPriceX96
    const poolContract = await new ethers.Contract(
        poolAdress,
        PoolABI,
        provider,
    )

    //use slot0 to get sqrtPriceX96
    const slot0 = await poolContract.slot0()
    const sqrtPriceX96 = slot0.sqrtPriceX96
    
    //get value of token0 and check if the token0 from user == token0 in pool - will be used in sqrtToPrice function
    const token0 = await poolContract.token0()
    const token1 = await poolContract.token1()
    
    const token0IsInput = tokenIn == token0
    
    //use Quoter V2 to get output amount of token1 and sqrtPriceX96 after emulated swap
    const quoter = new ethers.Contract(
        QUOTER2_ADDRESS,
        QuoterV2ABI,
        provider
    )
    //initialise the parameters for Quoter V2
    const params = {
        tokenIn: tokenIn,
        tokenOut: tokenOut,
        fee: fee,
        amountIn: amountIn,
        sqrtPriceLimitX96: '0', 
    }
    
    //query Quoter V2 code to get sqrtPriceX96After (sqrtPriceX96 when swap is emulated)
    const quote = await quoter.callStatic.quoteExactInputSingle(params)
    const sqrtPriceX96After = quote.sqrtPriceX96After
    //console.log the result 
    console.log(ethers.utils.formatUnits(quote.amountOut.toString(), decimalsOut))
    //convert sqrtPriceX96 to price and calculate price impact
    const price  = sqrtToPrice(sqrtPriceX96, decimalsIn, decimalsOut, token0IsInput)
    const priceAfter  = sqrtToPrice(sqrtPriceX96After, decimalsIn, decimalsOut, token0IsInput)
    
    const price_change = (priceAfter - price)/price
    let price_impact = (price_change * 100).toFixed(3)
    //console.log the price impact
    if(price_impact < 0){
        console.log(',',price_impact*-1)
    }else{
        console.log(',',price_impact)
    }
    return price_impact
}

module.exports = {getPI};

const method = process.argv[2];
const args = process.argv.slice(3);
module.exports[method](...args);
