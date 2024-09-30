import subprocess
from decimal import Decimal

def getPriceImpact(*args):
    try:
        #call JavaScript code from Python
        result = subprocess.check_output(["node", 'getPriceImpact.js', 'getPI', *args], universal_newlines=True)
        #result will be fetched from the variables that were console.log'ed. Format the result to get price
        # impact and output
        js_output = result.split(',')

        output_amount = js_output[0]
        price_impact = js_output[1]
        
        output_amount.replace('\n', '')
        price_impact.replace('\n', '')

        #return the price impact and output of token1
        return float(price_impact), float(output_amount)
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.strip()}"

def emulate_transaction(*args):
    #call JavaScript code from Python
    result = subprocess.check_output(["node", 'emulateTransaction.js', 'emulateTransaction', *args], universal_newlines=True)
    #return the result
    return result

def convertToWei(ammount, decimal):
    #wei == (amount)/(10^decimal)
    wei_amount = Decimal(ammount) * (Decimal(10) ** Decimal(decimal))
    return wei_amount