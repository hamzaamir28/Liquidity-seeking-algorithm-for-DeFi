const {ethers, JsonRpcProvider, BigNumber} = require('ethers')

const { abi: QuoterV2ABI } = require('@uniswap/v3-periphery/artifacts/contracts/lens/QuoterV2.sol/QuoterV2.json')

const QUOTER2_ADDRESS = '0x61fFE014bA17989E743c5F6cB21bF9697530B21e'

INFURA_URL = ""

const provider = new ethers.providers.JsonRpcProvider(INFURA_URL)


async function emulateTransaction(tokenIn, tokenOut, fee, input){
    
    //Use Uniswap Quoter V2 to emulate swap
    const quoter = new ethers.Contract(
        QUOTER2_ADDRESS,
        QuoterV2ABI,
        provider
    )
    //initialise parameters for Quoter V2
    const params = {
        tokenIn: tokenIn,
        tokenOut: tokenOut,
        fee: fee,
        amountIn: input,
        sqrtPriceLimitX96: '0', 
    }
    //emulate the swap and console.log the output of token1 (tokenOut)
    const quote = await quoter.callStatic.quoteExactInputSingle(params)
    const output = ethers.utils.formatUnits(quote.amountOut.toString())
    console.log(output)
}

module.exports = {emulateTransaction};

const method = process.argv[2];
const args = process.argv.slice(3);
module.exports[method](...args);