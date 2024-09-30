from web3 import Web3, HTTPProvider, contract, eth
import subprocess
from decimal import Decimal
import asyncio
import numpy
import time
from utils import getPriceImpact, convertToWei

infura_url = ""
w3 = Web3(Web3.HTTPProvider(infura_url))

def gather_token_details(token_address):

    #create ABI to interact with contracts on Ethereum Blockchain
    abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        }
    ]

    #get token information from Ethereum blockchain
    token = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=abi)
    name = token.functions.name().call()
    symbol = token.functions.symbol().call()
    decimals = token.functions.decimals().call()
    #return name, symbol and decimals for the token
    return {"name": name, "symbol": symbol, "decimals": decimals}


def getPoolInfo(tokenA, tokenB, fee):
    #create ABI to interact with Ethereum blockchain
    abi = [
        {
            "constant": False,
            "inputs": [
                {"name": "tokenA", "type": "address"},
                {"name": "tokenB", "type": "address"},
                {"name": "fee", "type": "uint24"}
            ],
            "name": "getPool",
            "outputs": [
                {"name": "", "type": "address"}
            ],
            "type": "function"
        }
    ]
    #use Uniswap V3 factory contract to query token0-token1 pool for a specific fee tier
    factory_address = "0x1f98431c8ad98523631ae4a59f267346ea31f984"
    factory = w3.eth.contract(address=w3.to_checksum_address(factory_address), abi=abi)

    #use try expect in case token0-token1 pair does not have a pool for a fee tier
    #if there isn't a pool for specific fee tier for token0-token1 pair, return null address
    try:
        pair_address = factory.functions.getPool(w3.to_checksum_address(tokenA), w3.to_checksum_address(tokenB), fee).call()
    except:
        pair_address = "0x0000000000000000000000000000000000000000"

    return pair_address

def get_max_input_and_output_on_a_pool(token0, token1, fee, pool, decimal0, decimal1, granular_amount, remaining):

    #initialise weiAmt - this should be sent to the getPI method as Quoter V2 uses weiAmt to emulate the swap
    weiAmt = 0

    #check if the remaining amout is less than granular_amount - in this case, send remaining to getPI
    if int(remaining) < int(granular_amount):
        #convert the amount to wei
        if decimal0 != 18:
            weiAmt = convertToWei(remaining, decimal0)
        else:
            weiAmt = w3.to_wei(remaining, 'ether')
        
        weiAmt = int(weiAmt)
        #call getPI using getPriceImpact
        PI_and_output = getPriceImpact(token0, token1, str(fee), str(weiAmt), pool, decimal0, decimal1)
        PI = PI_and_output[0]
        output = PI_and_output[1]
        #return price impact, output, remaining and weiAmt (input of token0) to splitOrder
        return PI, output, 0, weiAmt

    #convert amount of token0 into wei
    if decimal0 != 18:
        weiAmt = convertToWei(granular_amount, decimal0)
    elif decimal0 == 18:
        weiAmt = w3.to_wei(granular_amount, 'ether')
    
    weiAmt = int(weiAmt)
    #call getPI via getPriceImpact
    PI_and_output = getPriceImpact(token0, token1, str(fee), str(weiAmt), pool, decimal0, decimal1)
    PI = float(PI_and_output[0])
    output = float(PI_and_output[1])
    
    #run checks for Price impact, it should be in 4.5-5% range
    if PI < 5:
        if PI > 4:
            #this result should be returned, reduce granular from remaining
            remaining -= granular_amount
            #return price impact, output, remaining and weiAmt (input of token0) to splitOrder
            return PI, output, remaining, weiAmt
        else:
            #pool has high liquidity, so increase granular_amount
            #ensure PI != 0 - can't divide a number by 0
            if PI == 0.000000000000:
                granular_amount = float(4.5)*float(granular_amount)
            else:
                granular_amount = (float(4.5)/float(PI))*float(granular_amount)
            
            #call get_max_input_and_output_on_a_pool recursively with updated granular_amount
            return get_max_input_and_output_on_a_pool(token0, token1, fee, pool, decimal0, decimal1, int(granular_amount), remaining)
    elif PI < 10:
        #pool has medium liquidity, reduce the granular amount
        #check price impact != 0
        if PI == 0.000000000000:
            granular_amount = float(4.5)*float(granular_amount)
        else:
            granular_amount = (float(4.5)/float(PI))*float(granular_amount)
        #call get_max_input_and_output_on_a_pool recursively with updated granular_amount
        return get_max_input_and_output_on_a_pool(token0, token1, fee, pool, decimal0, decimal1, int(granular_amount), remaining)
    else:
       #this pool is ignored, illiquid pool
       return -1, 0, remaining, 0
    
def splitOrder(amtIn, pools, token0, token1, fee_pool, decimal0, decimal1):
    #initialise variables
    granularity = 0.01
    input_amount = amtIn
    granular_amount = input_amount * granularity
    remaining = input_amount
    new_outputs = [[],[],[],[]]
    new_price_impact = [[],[],[],[]]
    new_pool_inputs = [[],[],[],[]]

    count = 0

    #run a loop that'll run until remaining > 0
    while remaining > 0:
        #run a loop of pools
        for pool in pools:
            idx = pools.index(pool)
            
            #get initial inputs of token0 on each available pool
            if count < 4:
                #call get_max_input_and_output_on_a_pool
                func_output = get_max_input_and_output_on_a_pool(token0, token1, str(fee_pool[idx]), pool, decimal0, decimal1, granular_amount, remaining)
                    
                price_impact = func_output[0]
                output_amt = func_output[1]
                    
                remaining = func_output[2]
                input_amt = func_output[3]

                #store output, remaining, input amount and price impact into relevant variables
                last_idx = len(new_outputs[idx])
                new_outputs[idx].insert(last_idx, output_amt)
                new_price_impact[idx].insert(last_idx, price_impact)
                new_pool_inputs[idx].insert(last_idx, input_amt)

            elif count >= 4:
                #after initial inputs on the pool, copy-paste previous values in new index in each sub-array of each 2D array
                last_idx = len(new_outputs[idx])
                price_impact = new_price_impact[idx]
                
                output_amt = new_outputs[idx]
                
                input_amt = new_pool_inputs[idx]
                #update remaining and add value of index into index+1
                if (int(remaining) - int(int(input_amt[0])/int(10**int(decimal0)))) > 0:
                    remaining -= int(input_amt[0])/int(10**int(decimal0))
                    new_outputs[idx].insert(last_idx, output_amt[0])
                    new_price_impact[idx].insert(last_idx, price_impact[0])
                    new_pool_inputs[idx].insert(last_idx, input_amt[0])

                else:
                    #remaining < granular_amount, means get_max_input_and_output_on_a_pool has to be called to get price impact
                    # and output as these values will not be similar to previous ones
                    func_output = get_max_input_and_output_on_a_pool(token0, token1, str(fee_pool[idx]), pool, decimal0, decimal1, granular_amount, remaining)
                    price_impact = func_output[0]
                    output_amt = func_output[1]
                    remaining = func_output[2]
                    input_amt = func_output[3]
                    
                    last_idx = len(new_outputs[idx])
                    new_outputs[idx].insert(last_idx, output_amt)
                    new_price_impact[idx].insert(last_idx, price_impact)
                    new_pool_inputs[idx].insert(last_idx, input_amt)
                    
                    if remaining == 0:
                        break

            if remaining == 0:
                break
            
            count += 1

    #calculate sum of output and input and get maximum value of price impact
    output = 0.0
    for arr in new_outputs:
        for elem in arr:
            output += elem
    
    input = 0.0
    for arr in new_pool_inputs:
        for elem in arr:
            input+= elem
    
    pi = 0.0
    for arr in new_price_impact:
        for elem in arr:
            if elem > pi:
                pi = elem
                
    return output, pi, new_pool_inputs, input
    