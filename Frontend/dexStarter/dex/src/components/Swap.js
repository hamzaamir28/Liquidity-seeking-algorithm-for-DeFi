import React, { useState, useEffect} from 'react'
import { Input, Popover, Radio, Modal, Card ,message, Row} from "antd"
import {
  ArrowDownOutlined,
  DownOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import tokenList from '../tokenList.json'
import axios from 'axios'
import {ToastContainer, toast} from "react-toastify"
import "react-toastify/dist/ReactToastify.css"

function Swap() {

  const [tokenOneAmount, setTokenOneAmount] = useState(null)
  const [tokenTwoAmount, setTokenTwoAmount] = useState(null)
  const [tokenOne, setTokenOne] = useState(tokenList[0])
  const [tokenTwo, setTokenTwo] = useState(tokenList[1])
  const [isOpen, setIsOpen] = useState(false)
  const [changeToken, setChangeToken] = useState(1)
  const [prices, setPrices] = useState(null)
  const [swapVar, setSwap] = useState("Swap")
  const [messageApi, contextHolder] = message.useMessage();
  const [swapping, setSwapping] = useState(false)
  const [isModalVisable, setIsModalVisable] = useState(false)
  const [price_impact, setPriceImpact] = useState('-%')
  const { Meta } = Card
  const [data, setData] = useState('')
  function changeAmount(e){
    setTokenOneAmount(e.target.value)
  }

  function switchTokens(){
    setPrices(null)
    setTokenOneAmount(null)
    setTokenTwoAmount(null)
    const one = tokenOne
    const two = tokenTwo
    setTokenOne(two)
    setTokenTwo(one)
  }

  function openModal(asset){
    setChangeToken(asset)
    setIsOpen(true)
  }

  function modifyToken(i){
    if(changeToken === 1){
      setTokenOne(tokenList[i])
    }else{
      setTokenTwo(tokenList[i])
    }
    setIsOpen(false)
  }

  function sendDataToPy(e){
    const inpAmt = e.target.value
    setTokenTwoAmount('Fetching prices...')
    axios.post('http://127.0.0.1:5000/getInput', {
      token0: tokenOne.address,
      token1: tokenTwo.address,
      amtIn: inpAmt
    }).then(res => {
      console.log(res.data)
      const PI = res.data.max_PI
      const sum_out = res.data.sum_out
      console.log('PI ' + PI)
      setTokenTwoAmount(sum_out)
      setPriceImpact(PI)
      
    }).catch(e => {
      console.log('error happened, line 60')
      setTokenOneAmount(null)
      setTokenTwoAmount(null)
    })
  }

  const triggerSwap = async() => {
    setSwap("Swapping")
    await axios.post('http://127.0.0.1:5000/initSwap', {
      trigger: 'trigger'
    })
    .then( res => {
      console.log(res.data.msg)
      setSwapping(true)
      setTokenOneAmount(null)
      setTokenTwoAmount(null)
      setSwap("Swap")

      toast.success(res.data.msg, {
            position: "bottom-right",
            autoClose: 3000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
            draggable: true,
            progress: undefined,
            theme: "dark",
          });
    }).catch(e => {
      console.log('error happened, line 222')
      //setTokenOneAmount(null)
      //setTokenTwoAmount(null)
    })
  }

  return (
    <>
    {contextHolder}
    <Modal
    open={isOpen}
    footer={null}
    onCancel={() => setIsOpen(false)}
    title='Select a token'
    >
      <div className='modalContent'>
        {tokenList?.map((e, i) => {
          return(
            <div 
            className='tokenChoice'
            key={i}
            onClick={() => modifyToken(i)}
            >

              <img src={e.img} alt={e.ticker} className='tokenLogo' />
              <div className='tokenChoiceNames'>
                <div className='tokenName'>{e.name}</div>
                <div className='tokenTicker'>{e.ticker}</div>
              </div>

            </div>
          )
        })}
      </div>
    </Modal>
    <div className='tradeBox'>

      <div className='tradeBoxHeader'>

        <h4>Swap</h4>

      </div>

      <div className='inputs'>

        <Input placeholder='0'value={tokenOneAmount} onChange={changeAmount} onBlur={sendDataToPy}/>
        <Input placeholder='0'value={tokenTwoAmount} disabled={true} />
        <div className='switchButton' onClick={switchTokens}>
          <ArrowDownOutlined className='switchArrow' />
        </div>
        
        <div className='assetOne' onClick={() => openModal(1)}>
          <img src = {tokenOne.img} alt='assetOneLogo' className='assetLogo' />
          {tokenOne.ticker}
          <DownOutlined />
        </div>
        <div className='assetTwo' onClick={() => openModal(2)}>
          <img src = {tokenTwo.img} alt='assetOneLogo' className='assetLogo' />
          {tokenTwo.ticker}
          <DownOutlined />
        </div>
      </div>
      
      <div className='swapButton' disabled={!tokenOneAmount || swapVar === "Swapping"} onClick={triggerSwap}>{swapVar}</div>
      
      <Card 
      style={{ width: 400 }}
      bodyStyle={{backgroundColor: '#3a4157', border: 0 , textAlign:'left'}}
      bordered={false}>
        <Meta 
        description={'Price Impact: ' + price_impact}/>
      </Card>
    </div>
    
    <ToastContainer
      position="bottom-right"
      autoClose={3000}
      hideProgressBar={false}
      newestOnTop={false}
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="dark"
    />
    </>
  )
}

export default Swap
