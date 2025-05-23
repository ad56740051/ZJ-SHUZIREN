
// 切换到表演视频（状态2）  
function switchToPerformanceVideo() {  
  const sessionId = document.getElementById('sessionid').value;  
  if (!sessionId) return;  
      
  fetch('/set_audiotype', {  
    method: 'POST',  
    headers: {'Content-Type': 'application/json'},  
    body: JSON.stringify({  
      sessionid: parseInt(sessionId),  
      audiotype: 2,  // 设置为状态2，表示表演状态  
      reinit: true  
    })  
  })  
  .then(() => {  
    currentState = 2;  
    console.log('已切换到表演视频');  
  })  
  .catch(err => console.error('切换视频失败:', err));  
}




// 定期检查数字人说话状态    
function checkSpeakingStatus() {      
  const sessionId = document.getElementById('sessionid').value;      
  if (!sessionId) return;      
        
  fetch('/is_speaking', {      
    method: 'POST',      
    headers: {'Content-Type': 'application/json'},      
    body: JSON.stringify({sessionid: parseInt(sessionId)})      
  })      
  .then(response => response.json())      
  .then(data => {      
    // 当前状态是2（表演状态）时，保持在表演视频状态  
    if (!data.data && currentState !== 1 && currentState !== 2) { // 不在说话且状态不是1和2      
      switchToStaticVideo();      
    }      
  })      
  .catch(err => console.error('检查说话状态失败:', err));      
}
    
  // 切换到静态视频  
  function switchToStaticVideo() {  
    const sessionId = document.getElementById('sessionid').value;  
    if (!sessionId) return;  
      
    fetch('/set_audiotype', {  
      method: 'POST',  
      headers: {'Content-Type': 'application/json'},  
      body: JSON.stringify({  
        sessionid: parseInt(sessionId),  
        audiotype: 1,  // 设置为状态1，对应custom_video.json中的设置  
        reinit: true  
      })  
    })  
    .then(() => {  
      currentState = 1;  
      console.log('已切换到静态视频');  
    })  
    .catch(err => console.error('切换视频失败:', err));  
  }  
    
  // 全局变量跟踪当前状态  
  let currentState = 0;  
    
  // 文本发送前，确保切换到动态视频  
  document.getElementById('send-text-btn').addEventListener('click', function() {  
    const sessionId = document.getElementById('sessionid').value;  
    if (!sessionId) return;  
      
    fetch('/set_audiotype', {  
      method: 'POST',  
      headers: {'Content-Type': 'application/json'},  
      body: JSON.stringify({  
        sessionid: parseInt(sessionId),  
        audiotype: 0,  // 设置为状态0，使用动态视频  
        reinit: true  
      })  
    })  
    .then(() => {  
      currentState = 0;  
      console.log('已切换到动态视频');  
    })  
    .catch(err => console.error('切换视频失败:', err));  
  });  
    
  // 启动状态检查  
  setInterval(checkSpeakingStatus, 1000);

  // 添加表演按钮的事件监听  
document.getElementById('performance-btn').addEventListener('click', function() {  
  switchToPerformanceVideo();  
});