// 
//

var ws;

function WebSocketTest() {
    var messageContainer = document.getElementById("messages");
    if ("WebSocket" in window) {
        messageContainer.innerHTML = "WebSocket is supported by your Browser!";
        ws = new WebSocket("ws://127.0.0.1:8888/ws?Id=123456789");

        ws.onopen = function() {
            ws.send("Message to send");
        };

        ws.onmessage = actOnData;

        ws.onclose = function() { 
            messageContainer.innerHTML = "Connection is closed...";
        };

    } else {
        messageContainer.innerHTML = "WebSocket NOT supported by your Browser!";
    }
}

function actOnData(evt) {
    var received_msg = evt.data;
    var messageContainer = document.getElementById("messages");
    var world = JSON.parse(received_msg); 

    messageContainer.innerHTML = received_msg;

    var sonarWidth = document.getElementById("sonars").style.width 
    document.getElementById("sonar1").style.width = (100*(world.sonar[0]/300)).toString()+"%";
    document.getElementById("sonar2").style.width = (100*(world.sonar[1]/300)).toString()+"%";
    document.getElementById("sonar3").style.width = (100*(world.sonar[2]/300)).toString()+"%";
    document.getElementById("sonar4").style.width = (100*(world.sonar[3]/300)).toString()+"%";

    if (world.bump[0])  { document.getElementById("lbump").style.backgroundColor = "red"; }
                  else  { document.getElementById("lbump").style.backgroundColor = "green"; }
    if (world.bump[1])  { document.getElementById("rbump").style.backgroundColor = "red"; }
                   else { document.getElementById("rbump").style.backgroundColor = "green"; }
    if (world.cliff[0]) { document.getElementById("lcliff").style.backgroundColor = "red"; }
                   else { document.getElementById("lcliff").style.backgroundColor = "green"; }
    if (world.cliff[1]) { document.getElementById("rcliff").style.backgroundColor = "red"; }
                   else { document.getElementById("rcliff").style.backgroundColor = "green"; }
    
    irCamera(document.getElementById("ircamera"), world);
    mapDraw2(document.getElementById("map"), world);

};

function irCamera(canvas, world) { // ir = [ [x,y,w],null,null,null ] 
    var width = canvas.width;
    var height = canvas.height;
    var ir = world.ir
    var context = canvas.getContext("2d");

    context.strokeStyle = "white";
    context.fillStyle = "red";
    
    context.clearRect(0, 0, width, height);
    context.beginPath();
    for (var i=0; i<4; i++) {
        if (ir[i]) {
            var x = (ir[i][0]/1024)*width;
            var y = (ir[i][1]/768)*height;
            var w = ir[i][2];
            context.strokeRect(x-2*w,y-2*w, 2*2*w,2*2*w);
            }
        }
    };

function getMousePos(canvas, e) {
    var rect = canvas.getBoundingClientRect();
    return { x: e.clientX-rect.left, y: e.clientY-rect.top};
    }

function joyDraw(Canvas) {
    var x = Canvas.width;
    var y = Canvas.height;
    var w = 40;
    var joyContext = Canvas.getContext("2d");

    joyContext.strokeStyle = "white";
    joyContext.fillStyle = "blue";
    joyContext.beginPath();
//    joyContext.moveTo(x/2, y/2);    
    joyContext.arc(x/2, y/2, 100, 0.0, Math.PI*2);
    joyContext.stroke();
//    joyContext.strokeRect(x/2-2*w,y/2-2*w, 2*2*w,2*2*w);
    }


function robotDraw(canvas, x, y, th, world, zoom) {     // zoom=1 equates to 1cm = 1px.
    var context = canvas.getContext("2d");
    var w = canvas.width;
    var h = canvas.height;

    var size = 22/2; // cm
    var origin_x = (w/2)-(y*zoom);
    var origin_y = (h/2)-(x*zoom);

    context.strokeStyle = "white";
    context.fillStyle = "green";
    context.save();
    context.translate(origin_x,origin_y);
    context.rotate(Math.PI/2.0-th);
    context.strokeRect(-size*zoom, -size*zoom, 2*size*zoom, 2*size*zoom);
    context.beginPath();
    context.arc(-size*zoom*0.8, -size*zoom*0.8, size*zoom*0.08, 0.0, Math.PI*2);
    context.arc(-size*zoom*0.8,  size*zoom*0.8, size*zoom*0.08, 0.0, Math.PI*2);
    context.arc(-size*zoom*0.8, -size*zoom*0.6, size*zoom*0.08, 0.0, Math.PI*2);
    context.arc(-size*zoom*0.8,  size*zoom*0.6, size*zoom*0.08, 0.0, Math.PI*2);
    context.fill();
    context.restore();
    }

function mapDraw2(canvas, world) {
    var w = canvas.width;
    var h = canvas.height;
    var context = canvas.getContext("2d");
    var x = world.pose[0];
    var y = world.pose[1];
    var th = world.pose[2];
    var zoom = 2;// pixels per cm

    context.clearRect(0, 0, w, h);
    robotDraw(canvas, x, y, th, world, zoom);
    }

function joyMouseDown(e) {
    var pos = getMousePos(joyCanvas, e);

    joyDraw(joyCanvas);
    joyContext.strokeStyle = "white";
    joyContext.fillStyle = "red";
    joyContext.beginPath();
    joyContext.arc(pos.x, pos.y, 10, 0.0, Math.PI*2);
    joyContext.fill();
    console.log('you clicked');
    }

function docKeyDown(event) {
    if(event.keyCode == 37) {
        ws.send("left");
        }
    else if(event.keyCode == 39) {
        ws.send("right");
        }
    else if(event.keyCode == 38) {
        ws.send("forward");
        }
    else if(event.keyCode == 40) {
        ws.send("backward");
        }
    else if(event.keyCode == 32) {
        ws.send("stop");
        }
    }

var joyCanvas = document.getElementById("joystick");

joyCanvas.addEventListener('mousedown', joyMouseDown);
document.addEventListener('keydown', docKeyDown);
