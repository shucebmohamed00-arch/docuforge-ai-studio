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
FRAMES_DIR = BASE_DIR / "data" / "media" / "d3_chart_frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

OUT_VIDEO = ANIM_DIR / "anim_02_chart.mp4"

# Clean old frames
for f in FRAMES_DIR.glob("*.png"):
    try:
        f.unlink()
    except Exception:
        pass

PORT = 8992
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
        # Serve local files (like d3.min.js and index.html)
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open(BASE_DIR / 'd3_chart.html', 'rb') as f:
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
        return # suppress verbose logs

def run_server():
    server = HTTPServer(('127.0.0.1', PORT), FrameHandler)
    while not done_event.is_set():
        server.handle_request()
    server.server_close()

# Generate the D3 HTML Template
d3_html_content = """<!DOCTYPE html>
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
    #stage {
      position: relative;
      width: 1920px;
      height: 1080px;
      background: radial-gradient(circle at 60% 40%, #151b28 0%, #080B11 85%);
    }
  </style>
</head>
<body>
<div id="stage">
  <canvas id="chartCanvas" width="1920" height="1080"></canvas>
</div>

<script>
const TOTAL_FRAMES = 110;
const canvas = document.getElementById('chartCanvas');
const ctx = canvas.getContext('2d');

// Historical Swissair Data Points (1995 to Oct 2001)
const data = [
  { year: 1995, debt: 1.2, label: "AAA Rating // Conservative Reserves", note: "The Flying Bank" },
  { year: 1996, debt: 1.8, label: "EEA Rejection // Skies Deregulate", note: "" },
  { year: 1997, debt: 2.5, label: "Alliance Isolation", note: "" },
  { year: 1998, debt: 4.8, label: "Hunter Strategy Launches (Sabena 49.5%)", note: "Aggressive Buyout" },
  { year: 1999, debt: 9.2, label: "LTU, TAP, LOT, Volare Acquisitions", note: "Cash Drain Begins" },
  { year: 2000, debt: 13.8, label: "Hidden Off-Balance Liabilities", note: "Losses Snowball" },
  { year: 2001, debt: 17.2, label: "OCTOBER 2, 2001: SYSTEMIC GROUNDING", note: "17 BILLION CHF COLLAPSE" }
];

// D3 Scales
const margin = { top: 160, right: 120, bottom: 140, left: 160 };
const width = 1920 - margin.left - margin.right;
const height = 1080 - margin.top - margin.bottom;

const xScale = d3.scaleLinear()
  .domain([1995, 2001])
  .range([margin.left, margin.left + width]);

const yScale = d3.scaleLinear()
  .domain([0, 20.0])
  .range([margin.top + height, margin.top]);

// D3 Line Generator
const lineGen = d3.line()
  .x(d => xScale(d.year))
  .y(d => yScale(d.debt))
  .curve(d3.curveMonotoneX)
  .context(ctx);

// D3 Area Generator
const areaGen = d3.area()
  .x(d => xScale(d.year))
  .y0(margin.top + height)
  .y1(d => yScale(d.debt))
  .curve(d3.curveMonotoneX)
  .context(ctx);

function renderFrame(frameIdx) {
  const t = Math.min(1.0, frameIdx / (TOTAL_FRAMES * 0.75)); // animation settles in last 25%
  const eased = d3.easeCubicOut(t);
  
  // Clear
  ctx.clearRect(0, 0, 1920, 1080);
  
  // 1. Grid & Blueprint Lines
  ctx.save();
  ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
  ctx.lineWidth = 1;
  
  // Horizontal grid lines
  for (let b = 0; b <= 20; b += 5) {
    const y = yScale(b);
    ctx.beginPath();
    ctx.moveTo(margin.left, y);
    ctx.lineTo(margin.left + width, y);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = "rgba(160, 175, 200, 0.5)";
    ctx.font = "bold 18px 'Segoe UI', sans-serif";
    ctx.textAlign = "right";
    ctx.fillText(`${b}B CHF`, margin.left - 20, y + 6);
  }
  
  // Vertical grid lines
  for (let yr = 1995; yr <= 2001; yr++) {
    const x = xScale(yr);
    ctx.beginPath();
    ctx.moveTo(x, margin.top);
    ctx.lineTo(x, margin.top + height);
    ctx.stroke();
    
    // Label
    ctx.fillStyle = "rgba(160, 175, 200, 0.6)";
    ctx.font = "bold 20px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(yr === 2001 ? "OCT 2001" : yr, x, margin.top + height + 36);
  }
  ctx.restore();
  
  // 2. Animated Curve & Area Fill
  const currentYear = 1995 + (2001 - 1995) * eased;
  const currentData = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i].year <= currentYear) {
      currentData.push(data[i]);
    } else {
      const prev = data[i - 1];
      const frac = (currentYear - prev.year) / (data[i].year - prev.year);
      const interpDebt = prev.debt + frac * (data[i].debt - prev.debt);
      currentData.push({ year: currentYear, debt: interpDebt, label: "", note: "" });
      break;
    }
  }
  
  // Area Gradient
  if (currentData.length > 1) {
    ctx.save();
    const grad = ctx.createLinearGradient(0, margin.top, 0, margin.top + height);
    grad.addColorStop(0, "rgba(255, 51, 85, 0.35)");
    grad.addColorStop(0.6, "rgba(255, 51, 85, 0.12)");
    grad.addColorStop(1, "rgba(255, 51, 85, 0.0)");
    
    ctx.beginPath();
    areaGen(currentData);
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();
    
    // Stroke with Neon Glow
    ctx.save();
    ctx.shadowColor = "#FF3355";
    ctx.shadowBlur = 18;
    ctx.strokeStyle = "#FF3355";
    ctx.lineWidth = 5;
    ctx.beginPath();
    lineGen(currentData);
    ctx.stroke();
    ctx.restore();
  }
  
  // 3. Milestone Markers along path
  currentData.forEach((d, idx) => {
    if (idx < currentData.length - 1 || t >= 0.98) {
      const px = xScale(d.year);
      const py = yScale(d.debt);
      
      ctx.save();
      ctx.fillStyle = d.year === 2001 ? "#FF3355" : "#FFD700";
      ctx.beginPath();
      ctx.arc(px, py, d.year === 2001 ? 8 : 5, 0, Math.PI * 2);
      ctx.fill();
      
      // Halo ring
      ctx.strokeStyle = d.year === 2001 ? "rgba(255, 51, 85, 0.6)" : "rgba(255, 215, 0, 0.5)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(px, py, d.year === 2001 ? 14 : 9, 0, Math.PI * 2);
      ctx.stroke();
      
      // Milestone Callout Badges
      if (d.year === 1995) {
        drawPill(ctx, px - 10, py - 35, "1995: AAA Rating (1.2B)", "#FFD700", "left");
      } else if (d.year === 1998) {
        drawPill(ctx, px, py - 40, "1998: Hunter Strategy (4.8B)", "#FFD700", "center");
      } else if (d.year === 2000) {
        drawPill(ctx, px, py - 40, "2000: Losses Mounting (13.8B)", "#FFAA33", "center");
      }
      ctx.restore();
    }
  });
  
  // Current Head Point & Radar Ping
  const head = currentData[currentData.length - 1];
  const hx = xScale(head.year);
  const hy = yScale(head.debt);
  
  ctx.save();
  ctx.fillStyle = "#FFFFFF";
  ctx.beginPath();
  ctx.arc(hx, hy, 6, 0, Math.PI * 2);
  ctx.fill();
  
  // Pulse
  const pulsePhase = (frameIdx % 20) / 20;
  ctx.strokeStyle = `rgba(255, 51, 85, ${1.0 - pulsePhase})`;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(hx, hy, 8 + pulsePhase * 25, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
  
  // 4. Tactical Headers & Dynamic Counter
  ctx.save();
  // Header bar
  ctx.fillStyle = "#FFD700";
  ctx.fillRect(margin.left, 50, 6, 44);
  
  ctx.fillStyle = "#FFFFFF";
  ctx.font = "900 28px 'Segoe UI', sans-serif";
  ctx.textAlign = "left";
  ctx.fillText("FORENSIC AUDIT: THE CATASTROPHIC DEBT EXPLOSION", margin.left + 20, 80);
  
  ctx.fillStyle = "rgba(180, 195, 220, 0.7)";
  ctx.font = "bold 16px 'Segoe UI', sans-serif";
  ctx.fillText("SWISSAIR GROUP (SAIRGROUP) TOTAL ACCUMULATED DEBT & LIQUIDITY CRATER", margin.left + 20, 104);
  
  // Ticking Ticker Box (Right side)
  const currentCHF = (head.debt).toFixed(1);
  const isCritical = head.debt > 15.0;
  
  ctx.fillStyle = "rgba(15, 20, 32, 0.85)";
  ctx.strokeStyle = isCritical ? "#FF3355" : "#FFD700";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(1920 - margin.right - 380, 45, 380, 85, 8);
  ctx.fill();
  ctx.stroke();
  
  ctx.fillStyle = isCritical ? "#FF3355" : "#FFD700";
  ctx.font = "900 38px 'Segoe UI', monospace";
  ctx.textAlign = "right";
  ctx.fillText(`${currentCHF} BILLION CHF`, 1920 - margin.right - 25, 95);
  
  ctx.fillStyle = isCritical ? "#FFAAAA" : "rgba(255, 215, 0, 0.7)";
  ctx.font = "bold 13px 'Segoe UI', sans-serif";
  ctx.fillText(isCritical ? "CRITICAL INSOLVENCY / RESTRUCTURING COLLAPSE" : "AGGRESSIVE HUNTER ACQUISITIONS", 1920 - margin.right - 25, 118);
  
  // Final Impact Card when debt reaches 17B
  if (t >= 0.85) {
    const cardAlpha = Math.min(1.0, (t - 0.85) / 0.15);
    ctx.fillStyle = `rgba(255, 30, 60, ${cardAlpha * 0.2})`;
    ctx.strokeStyle = `rgba(255, 51, 85, ${cardAlpha})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(hx - 360, hy - 140, 340, 100, 6);
    ctx.fill();
    ctx.stroke();
    
    ctx.fillStyle = `rgba(255, 255, 255, ${cardAlpha})`;
    ctx.font = "900 20px 'Segoe UI', sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("TOTAL SYSTEMIC LIQUIDITY CRASH", hx - 340, hy - 105);
    
    ctx.fillStyle = `rgba(255, 215, 0, ${cardAlpha})`;
    ctx.font = "900 24px 'Segoe UI', monospace";
    ctx.fillText("17,200,000,000 CHF", hx - 340, hy - 72);
  }
  
  ctx.restore();
}

function drawPill(ctx, x, y, text, color, align) {
  ctx.save();
  ctx.font = "bold 14px 'Segoe UI', sans-serif";
  const metrics = ctx.measureText(text);
  const w = metrics.width + 24;
  const h = 28;
  const px = align === "center" ? x - w/2 : (align === "left" ? x : x - w);
  
  ctx.fillStyle = "rgba(10, 15, 25, 0.85)";
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(px, y - h + 6, w, h, 4);
  ctx.fill();
  ctx.stroke();
  
  ctx.fillStyle = "#FFFFFF";
  ctx.textAlign = "left";
  ctx.fillText(text, px + 12, y);
  ctx.restore();
}

// Drive frame capture via async loop
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

// Start once loaded
window.addEventListener('load', () => {
  setTimeout(generateAllFrames, 500);
});
</script>
</body>
</html>
"""

Path(BASE_DIR / 'd3_chart.html').write_text(d3_html_content, encoding='utf-8')

# Start HTTP Server in background thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print(f"HTTP Server listening on port {PORT} for D3 frame dispatch...")

# Launch Chrome headless to render D3 frames
chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
chrome_cmd = [
    chrome_path,
    '--headless=new',
    '--disable-gpu',
    '--window-size=1920,1080',
    f'http://127.0.0.1:{PORT}/index.html'
]
print("Launching Chrome headless to generate D3.js 60fps frames...")
chrome_proc = subprocess.Popen(chrome_cmd)

# Wait for all frames
timeout = 60
start_w = time.time()
while not done_event.is_set() and (time.time() - start_w) < timeout:
    time.sleep(0.5)

chrome_proc.terminate()
print(f"Captured {received_count} D3 frames in {time.time() - start_w:.2f}s!")

# Encode D3 frames to anim_02_chart.mp4 with FFmpeg
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
print(f"SUCCESS: D3.js Forensic Debt Chart rendered to {OUT_VIDEO} ({OUT_VIDEO.stat().st_size / (1024*1024):.2f} MB)")
