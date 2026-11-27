import os
import sys
import time
import json
import base64
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from pathlib import Path

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
ANIM_DIR = BASE_DIR / "data" / "media" / "animations" / "swiss-air-grounding-prod"
ANIM_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR = BASE_DIR / "data" / "media" / "d3_wheel_frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

OUT_VIDEO = ANIM_DIR / "anim_07_hunter_wheel.mp4"

# Clean old frames
for f in FRAMES_DIR.glob("*.png"):
    try:
        f.unlink()
    except Exception:
        pass

PORT = 8993
total_frames = 110 # ~3.66s at 30fps
received_count = 0
done_event = threading.Event()

class FrameHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global received_count
        content_len = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_len)
        data = json.loads(post_data.decode('utf-8'))
        
        idx = data['frame']
        b64 = data['image'].split(',', 1)[1]
        img_bytes = base64.b64decode(b64)
        
        frame_file = FRAMES_DIR / f"frame_{idx:04d}.png"
        with open(frame_file, "wb") as f:
            f.write(img_bytes)
            
        received_count += 1
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
        
        if received_count >= total_frames:
            done_event.set()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open(BASE_DIR / 'd3_wheel.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/d3.min.js':
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            with open(BASE_DIR / 'd3.min.js', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        return

def run_server():
    server = HTTPServer(('127.0.0.1', PORT), FrameHandler)
    while not done_event.is_set():
        server.handle_request()
    server.server_close()

d3_wheel_html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="/d3.min.js"></script>
  <style>
    body {
      margin: 0;
      background: #080B11;
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      font-family: 'Segoe UI', -apple-system, sans-serif;
    }
  </style>
</head>
<body>
<canvas id="wheelCanvas" width="1920" height="1080"></canvas>

<script>
const TOTAL_FRAMES = 110;
const canvas = document.getElementById('wheelCanvas');
const ctx = canvas.getContext('2d');

const center = { x: 960, y: 560 };
const radius = 340;

const targets = [
  { name: "SABENA", country: "BELGIUM", stake: "49.5% STAKE", note: "CRITICAL 2.5B CHF LOSS", color: "#FF3355" },
  { name: "LTU INTERNATIONAL", country: "GERMANY", stake: "49.9% STAKE", note: "CASH BLEED DEFICIT", color: "#FF3355" },
  { name: "TAP AIR", country: "PORTUGAL", stake: "34.0% STAKE", note: "UNPROFITABLE REGIONAL", color: "#FFAA33" },
  { name: "LOT POLISH", country: "POLAND", stake: "37.6% STAKE", note: "HEAVY EXPANSION COST", color: "#FFAA33" },
  { name: "VOLARE AIRLINES", country: "ITALY", stake: "49.8% STAKE", note: "COLLATERAL LOSS", color: "#FF3355" },
  { name: "AIR LITTORAL", country: "FRANCE", stake: "49.0% STAKE", note: "INSOLVENT REGIONAL", color: "#FF3355" }
];

function renderFrame(frameIdx) {
  const t = Math.min(1.0, frameIdx / (TOTAL_FRAMES * 0.7));
  const eased = d3.easeCubicOut(t);
  const rotAngle = (frameIdx / TOTAL_FRAMES) * 0.25; // subtle organic rotation
  
  ctx.clearRect(0, 0, 1920, 1080);
  
  // Background radial
  const bgGrad = ctx.createRadialGradient(960, 560, 50, 960, 560, 900);
  bgGrad.addColorStop(0, "#151B28");
  bgGrad.addColorStop(1, "#080B11");
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, 1920, 1080);
  
  // Subtle concentric orbits
  ctx.save();
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;
  [radius * 0.5, radius, radius * 1.3].forEach(r => {
    ctx.beginPath();
    ctx.arc(center.x, center.y, r, 0, Math.PI * 2);
    ctx.stroke();
  });
  ctx.restore();
  
  // Header
  ctx.save();
  ctx.fillStyle = "#FFD700";
  ctx.fillRect(140, 50, 6, 44);
  
  ctx.fillStyle = "#FFFFFF";
  ctx.font = "900 28px 'Segoe UI', sans-serif";
  ctx.fillText("THE HUNTER STRATEGY: MINORITY ACQUISITION NETWORK", 160, 80);
  
  ctx.fillStyle = "rgba(180, 195, 220, 0.7)";
  ctx.font = "bold 16px 'Segoe UI', sans-serif";
  ctx.fillText("AGGRESSIVE BUYOUT OF CHRONICALLY UNPROFITABLE CARRIERS (1998 - 2001)", 160, 104);
  
  // Status Box
  ctx.fillStyle = "rgba(15, 20, 32, 0.85)";
  ctx.strokeStyle = "#FF3355";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(1920 - 140 - 380, 45, 380, 85, 8);
  ctx.fill();
  ctx.stroke();
  
  ctx.fillStyle = "#FF3355";
  ctx.font = "900 24px 'Segoe UI', sans-serif";
  ctx.textAlign = "right";
  ctx.fillText("LETHAL CAPITAL DRAIN", 1920 - 140 - 25, 82);
  
  ctx.fillStyle = "rgba(255, 215, 0, 0.85)";
  ctx.font = "bold 14px 'Segoe UI', monospace";
  ctx.fillText("OFF-BALANCE GUARANTEES COLLAPSING", 1920 - 140 - 25, 108);
  ctx.restore();
  
  // Render Beams & Satellite Nodes
  const numTargets = targets.length;
  targets.forEach((tg, i) => {
    const baseAngle = (i / numTargets) * Math.PI * 2 + rotAngle;
    const currentDist = radius * eased;
    const x = center.x + Math.cos(baseAngle) * currentDist;
    const y = center.y + Math.sin(baseAngle) * currentDist;
    
    // Animated Beam from Swissair to Target
    ctx.save();
    ctx.strokeStyle = `rgba(255, 51, 85, ${0.4 * eased})`;
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 8]);
    ctx.lineDashOffset = -(frameIdx * 2);
    ctx.beginPath();
    ctx.moveTo(center.x, center.y);
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.restore();
    
    // Satellite Node Card
    if (eased > 0.3) {
      const nodeAlpha = Math.min(1.0, (eased - 0.3) / 0.7);
      ctx.save();
      ctx.globalAlpha = nodeAlpha;
      
      // Node Card Box
      const cardW = 210;
      const cardH = 75;
      const cardX = x - cardW / 2;
      const cardY = y - cardH / 2;
      
      ctx.fillStyle = "rgba(12, 16, 26, 0.92)";
      ctx.strokeStyle = tg.color;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(cardX, cardY, cardW, cardH, 6);
      ctx.fill();
      ctx.stroke();
      
      // Node Name & Details
      ctx.fillStyle = "#FFFFFF";
      ctx.font = "900 16px 'Segoe UI', sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(tg.name, x, cardY + 24);
      
      ctx.fillStyle = "#FFD700";
      ctx.font = "bold 13px 'Segoe UI', sans-serif";
      ctx.fillText(`${tg.country} • ${tg.stake}`, x, cardY + 44);
      
      ctx.fillStyle = "#FF7788";
      ctx.font = "bold 11px 'Segoe UI', monospace";
      ctx.fillText(tg.note, x, cardY + 62);
      ctx.restore();
    }
  });
  
  // Center Node: Swissair (SAirGroup)
  ctx.save();
  const cPulse = (frameIdx % 25) / 25;
  ctx.strokeStyle = `rgba(255, 215, 0, ${1.0 - cPulse})`;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(center.x, center.y, 85 + cPulse * 30, 0, Math.PI * 2);
  ctx.stroke();
  
  // Core circle
  ctx.fillStyle = "#0A0D14";
  ctx.strokeStyle = "#FFD700";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.arc(center.x, center.y, 85, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  
  // Swiss Red Cross badge inside core
  ctx.fillStyle = "#D52B1E";
  ctx.beginPath();
  ctx.roundRect(center.x - 22, center.y - 45, 44, 44, 4);
  ctx.fill();
  
  // White Cross
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(center.x - 14, center.y - 28, 28, 10);
  ctx.fillRect(center.x - 5, center.y - 37, 10, 28);
  
  // Title
  ctx.fillStyle = "#FFFFFF";
  ctx.font = "900 18px 'Segoe UI', sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("SWISSAIR", center.x, center.y + 20);
  
  ctx.fillStyle = "#FFD700";
  ctx.font = "bold 13px 'Segoe UI', sans-serif";
  ctx.fillText("SAirGroup HUB", center.x, center.y + 38);
  ctx.restore();
}

async function generateAllFrames() {
  for (let f = 0; f < TOTAL_FRAMES; f++) {
    renderFrame(f);
    const dataUrl = canvas.toDataURL('image/png');
    await fetch('/save_frame', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ frame: f, image: dataUrl })
    });
  }
}

window.addEventListener('load', () => {
  setTimeout(generateAllFrames, 500);
});
</script>
</body>
</html>
"""

Path(BASE_DIR / 'd3_wheel.html').write_text(d3_wheel_html, encoding='utf-8')

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print(f"HTTP Server listening on port {PORT} for Hunter Wheel D3 frame dispatch...")

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
chrome_cmd = [
    chrome_path,
    '--headless=new',
    '--disable-gpu',
    '--window-size=1920,1080',
    f'http://127.0.0.1:{PORT}/index.html'
]
print("Launching Chrome headless to generate Hunter Wheel D3.js frames...")
chrome_proc = subprocess.Popen(chrome_cmd)

timeout = 60
start_w = time.time()
while not done_event.is_set() and (time.time() - start_w) < timeout:
    time.sleep(0.5)

chrome_proc.terminate()
print(f"Captured {received_count} Hunter Wheel D3 frames in {time.time() - start_w:.2f}s!")

print(f"Encoding D3 frames to {OUT_VIDEO}...")
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-framerate", "30",
    "-i", str(FRAMES_DIR / "frame_%04d.png"),
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    str(OUT_VIDEO)
]
subprocess.run(ffmpeg_cmd, check=True)
print(f"SUCCESS: D3.js Hunter Wheel rendered to {OUT_VIDEO} ({OUT_VIDEO.stat().st_size / (1024*1024):.2f} MB)")
