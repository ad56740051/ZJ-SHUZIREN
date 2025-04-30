var pc = null;

function negotiate() {
    console.log("client.js: negotiate() called");
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    console.log("client.js: Transceivers added");
    return pc.createOffer().then((offer) => {
        console.log("client.js: Offer created:", offer.sdp);
        return pc.setLocalDescription(offer);
    }).then(() => {
        console.log("client.js: Local description set. Waiting for ICE gathering...");
        // wait for ICE gathering to complete
        return new Promise((resolve) => {
            if (pc.iceGatheringState === 'complete') {
                console.log("client.js: ICE gathering already complete.");
                resolve();
            } else {
                const checkState = () => {
                    console.log("client.js: ICE gathering state changed:", pc.iceGatheringState);
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        console.log("client.js: ICE gathering complete.");
                        resolve();
                    }
                };
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(() => {
        var offer = pc.localDescription;
        console.log("client.js: ICE complete. Sending offer to server:", offer.sdp);
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then((response) => {
        console.log("client.js: Received response from /offer");
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    }).then((answer) => {
        console.log("client.js: Received answer from server:", answer.sdp);
        document.getElementById('sessionid').value = answer.sessionid;
        return pc.setRemoteDescription(answer);
    }).then(() => {
        console.log("client.js: Remote description set successfully!"); // Success log
    }).catch((e) => {
        console.error("client.js: Error in negotiate():", e);
        alert(e);
        // Propagate the error to the start function's catch block
        throw e; 
    });
}

function start() {
    console.log("client.js: start() called");
    var config = {
        sdpSemantics: 'unified-plan'
    };

    if (document.getElementById('use-stun').checked) {
        console.log("client.js: Using STUN");
        config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
    } else {
        console.log("client.js: Not using STUN");
    }

    // Close existing connection if any
    if (pc) {
        console.log("client.js: Closing existing PeerConnection before starting new one.");
        try { pc.close(); } catch(e) { console.error("Error closing previous PC:", e); }
        pc = null;
    }

    pc = new RTCPeerConnection(config);
    console.log("client.js: PeerConnection created");

    // connect audio / video
    pc.addEventListener('track', (evt) => {
        console.log("client.js: !!! Track event received !!! - kind:", evt.track.kind);
        const stream = evt.streams[0];
        if (!stream) {
             console.error("client.js: Track event received but no stream associated?");
             return;
        }
        if (evt.track.kind == 'video') {
            const videoElement = document.getElementById('video');
            if (videoElement) {
                console.log("client.js: Attaching video track to video element.");
                videoElement.srcObject = stream;
            } else {
                 console.error("client.js: Video element not found!");
            }
        } else if (evt.track.kind == 'audio') {
            const audioElement = document.getElementById('audio');
            if (audioElement) {
                console.log("client.js: Attaching audio track to audio element.");
                audioElement.srcObject = stream;
            } else {
                 console.warn("client.js: Audio element not found (might be intended if d-none).");
            }
        }
    });

    pc.addEventListener('connectionstatechange', event => {
        console.log("client.js: PeerConnection state changed:", pc.connectionState);
        if (pc.connectionState === 'failed') {
            console.error("client.js: PeerConnection failed!");
            stop(); // Attempt to cleanup
            alert("WebRTC 连接失败。");
        } else if (pc.connectionState === 'connected') {
             console.log("client.js: PeerConnection connected successfully.");
        }
    });

    // Toggle button visibility
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    if(startButton) startButton.style.display = 'none';
    if(stopButton) stopButton.style.display = 'inline-block';
    console.log("client.js: Start/Stop buttons toggled in UI");

    // Perform negotiation
    console.log("client.js: Calling negotiate()...");
    negotiate().then(() => {
        console.log("client.js: Negotiation promise resolved successfully in start()");
    }).catch((e) => {
        console.error("client.js: Negotiation failed in start():", e);
        // Revert button visibility on failure
        if(startButton) startButton.style.display = 'inline-block';
        if(stopButton) stopButton.style.display = 'none';
        // Alert is likely already shown in negotiate's catch block
    });
}

function stop() {
    console.log("client.js: stop() called");
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    if(stopButton) stopButton.style.display = 'none';
    if(startButton) startButton.style.display = 'inline-block';

    // close peer connection
    if (pc) {
        console.log("client.js: Closing PeerConnection");
        // Use a short timeout to allow signaling messages to potentially complete
        setTimeout(() => {
             try {
                 pc.close();
                 console.log("client.js: PeerConnection closed");
                 pc = null; // Reset pc variable
             } catch (e) {
                 console.error('Error closing PeerConnection in stop():', e);
             }
        }, 100); // Reduced timeout
    } else {
        console.log("client.js: PeerConnection already null in stop()");
    }
}

// Replace deprecated unload listeners with pagehide
window.addEventListener('pagehide', (event) => {
    // The event.persisted property is true if the page is cached by the browser
    if (event.persisted === false) {
        console.log('Closing PeerConnection due to pagehide event.');
        if (pc) {
             try {
                 pc.close();
                 console.log('PeerConnection closed on pagehide.');
             } catch (e) {
                 console.error('Error closing PeerConnection on pagehide:', e);
             }
        }
    }
});

// Keep beforeunload for the prompt, but remove pc.close() from it
window.onbeforeunload = function (e) {
    // Don't close pc here, rely on pagehide
    e = e || window.event;
    // Compatible Browsers prompt
    if (e) {
      e.returnValue = '确定离开此页面吗？连接将会断开。'; // Prompt message
    }
    // For older browsers
    return '确定离开此页面吗？连接将会断开。'; // Prompt message
};