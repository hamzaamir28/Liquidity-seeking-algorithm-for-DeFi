from flask import Flask, request, jsonify, copy_current_request_context, Response
import json
from quoter import gather_token_details, getPoolInfo, splitOrder
from utils import emulate_transaction
from flask_cors import CORS, cross_origin
import time
from datetime import datetime

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

sum_in = 0
new_pool_inputs = [[],[],[],[]]
pool_list = []
corresponding_fee_tier = []
token0 = ''
token1 = ''
inpAmt = 0
tokenA_details = ''
tokenB_details = ''
sum_out = 0


@app.route('/getInput', methods = ['POST'])
@cross_origin()
def request_quote():
    #declearing global variables
    global sum_in
    global new_pool_inputs
    global token0
    global token1
    global inpAmt
    global tokenA_details
    global tokenB_details
    global sum_out
    #initialising variables
    sum_in = 0
    new_pool_inputs = [[],[],[],[]]
    token1 = ''
    inpAmt = 0
    tokenA_details = ''
    tokenB_details = ''
    sum_out = 0

    #get result from frontend
    result = request.get_json()
    #stroing results into variables
    token0 = result['token0']
    token1 = result['token1']
    inpAmt = result['amtIn']

    #get information on each token
    tokenA_details = gather_token_details(token0)
    tokenB_details = gather_token_details(token1)
    fee_list = [10000, 500, 3000, 100]
    
    global pool_list
    global corresponding_fee_tier
    pool_list = []
    corresponding_fee_tier = []

    #iterate through the frr_list and find all available pools for the pair
    for fee in fee_list:
        pair = getPoolInfo(token0, token1, fee)
        if pair != "0x0000000000000000000000000000000000000000":
            pool_list.append(pair)
            corresponding_fee_tier.append(fee)

    #call splitOrder
    sum_out, max_PI, new_pool_inputs, sum_in = splitOrder(int(inpAmt), pool_list, token0, token1, corresponding_fee_tier, str(tokenA_details['decimals']), str(tokenB_details['decimals']))
    
    print()
    print('sum_out: ', sum_out)
    print('max_PI: ', max_PI)
    print('new_pool_inputs: ', new_pool_inputs)
    
    return jsonify({'sum_out': "{:.3f}".format(sum_out), 'max_PI': "{:.3f}".format(max_PI) + "%"})

@app.route('/initSwap', methods = ['POST'])
@cross_origin()
def init_swap():
    trigger = request.get_json()

    if trigger:
        global sum_in
        global sum_out
        i = 0
        
        print('TRIGGER RECEIVED')
        try:
            while i < len(new_pool_inputs[0]):
                print('i: ', i)
                for pool in pool_list:
                    idx = pool_list.index(pool)
                    if pool != "0x0000000000000000000000000000000000000000" or new_pool_inputs[idx] != []:
                        
                        fee = corresponding_fee_tier[idx]

                        if new_pool_inputs[idx][i] != 0:
                            output = emulate_transaction(token0, token1, str(fee), str(new_pool_inputs[idx][i]))
                            inp = float(new_pool_inputs[idx][i])/float(10**(float(tokenA_details['decimals'])))
                            out = "{:.3f}".format(float(output))
                            
                            print()
                            msg="Swap completed " + str(inp) + " " + str(tokenA_details['symbol']) + " yielded " + out + " " + str(tokenB_details['symbol'])
                            print('msg: ', msg)
                
                print('sleeping for 5s')      
                time.sleep(5) 
        
                i+=1
        
        except IndexError:
            print('ALL SWAPS COMPLETED')
    return jsonify({'msg': "Swap completed " + str(float(sum_in)/float(10**(float(tokenA_details['decimals'])))) + " " + str(tokenA_details['symbol']) + " yielded " + str("{:.3f}".format(float(sum_out))) + " " + str(tokenB_details['symbol'])})


if __name__ == '__main__':
    app.run(debug = True)
