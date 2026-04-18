import streamlit as st

# 1. Page Configuration & Branding
st.set_page_config(
    page_title="GLOBALINTERNET.PY - Cash Runner",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Professional Header
st.title("🏃‍♂️ GLOBALINTERNET.PY: Cash Runner")
st.markdown("""
**Controls:** - **A / D** or **Left / Right Arrows**: Move Forward & Backward  
- **Space / W** or **Up Arrow**: Jump to catch bags or avoid obstacles  
""")

# 2. The Game Engine (HTML/JavaScript)
# This handles the Man Figure, Parallax, and Collision logic
game_html = """
<style>
    body { margin: 0; background-color: #0e1117; color: white; display: flex; flex-direction: column; align-items: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    canvas { border: 4px solid #4ade80; border-radius: 12px; background: #1e293b; outline: none; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
    #ui { margin-top: 15px; padding: 10px 20px; background: #1e293b; border-radius: 8px; border: 1px solid #334155; min-width: 400px; text-align: center; }
    .stat { font-weight: bold; color: #4ade80; font-size: 1.2rem; }
</style>

<canvas id="gameCanvas" width="900" height="450" tabindex="0"></canvas>
<div id="ui">
    💰 Score: <span id="score" class="stat">0</span>/5 | 
    <span id="msg">Collect 5 bags to win!</span>
</div>

<script>
(function() {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreEl = document.getElementById('score');
    const msgEl = document.getElementById('msg');

    // --- State Variables ---
    let p = { x: 150, y: 380, vy: 0, speed: 5, jumping: false, dir: 0, f: 0 };
    let worldX = 0;
    let score = 0;
    let active = true;

    // Obstacles & Collectibles (Relative to worldX)
    let bags = [
        { x: 600, y: 220, c: false }, { x: 1200, y: 180, c: false }, 
        { x: 1800, y: 250, c: false }, { x: 2400, y: 150, c: false }, 
        { x: 3000, y: 200, c: false }
    ];
    let cars = [{ x: 900 }, { x: 1600 }, { x: 2300 }, { x: 2900 }];

    // --- Input Handling ---
    const keys = {};
    window.addEventListener('keydown', e => { 
        keys[e.code] = true; 
        if((e.code==='Space' || e.code==='ArrowUp' || e.code==='KeyW') && !p.jumping) {
            p.vy = -16; p.jumping = true;
        }
    });
    window.addEventListener('keyup', e => { keys[e.code] = false; });

    function drawMan(xPos, yPos, frame, isJumping, direction) {
        ctx.strokeStyle = "#fff"; ctx.lineWidth = 3;
        let swing = isJumping ? 0.3 : Math.sin(frame * 0.2) * 15;
        
        // Head
        ctx.beginPath(); ctx.arc(xPos, yPos - 55, 8, 0, Math.PI*2); ctx.stroke();
        // Body
        ctx.beginPath(); ctx.moveTo(xPos, yPos - 47); ctx.lineTo(xPos, yPos - 20);
        // Arms (reactive to movement)
        ctx.moveTo(xPos, yPos - 40); ctx.lineTo(xPos + (direction * 10) + swing, yPos - 25);
        ctx.moveTo(xPos, yPos - 40); ctx.lineTo(xPos - (direction * 10) - swing, yPos - 25);
        // Legs
        ctx.moveTo(xPos, yPos - 20); ctx.lineTo(xPos + swing, yPos);
        ctx.moveTo(xPos, yPos - 20); ctx.lineTo(xPos - swing, yPos);
        ctx.stroke();
    }

    function drawParallax(wX) {
        // Distant Mountains (Slowest)
        ctx.fillStyle = "#1e293b";
        for(let i=0; i<3; i++) {
            let off = (i * 900 - (wX * 0.2)) % 2700;
            ctx.beginPath(); ctx.moveTo(off, 400); ctx.lineTo(off+150, 150); ctx.lineTo(off+300, 400); ctx.fill();
        }
        // Hills (Medium)
        ctx.fillStyle = "#334155";
        for(let i=0; i<5; i++) {
            let off = (i * 400 - (wX * 0.5)) % 2000;
            ctx.beginPath(); ctx.arc(off, 420, 150, 0, Math.PI, true); ctx.fill();
        }
    }

    function loop() {
        if(!active) return;
        ctx.clearRect(0, 0, 900, 450);
        
        // 1. Update Movement
        p.dir = keys['ArrowRight'] || keys['KeyD'] ? 1 : (keys['ArrowLeft'] || keys['KeyA'] ? -1 : 0);
        p.x += p.dir * p.speed;
        
        // Scroll world if player moves past center
        if(p.x > 500) { worldX += p.speed; p.x = 500; }
        if(p.x < 100 && worldX > 0) { worldX -= p.speed; p.x = 100; }
        if(p.x < 20) p.x = 20;

        // Gravity
        p.vy += 0.8; p.y += p.vy;
        if(p.y > 400) { p.y = 400; p.vy = 0; p.jumping = false; }
        p.f++;

        // 2. Render Environment
        drawParallax(worldX);
        ctx.fillStyle = "#475569"; ctx.fillRect(0, 400, 900, 50); // Ground

        // 3. Collectibles
        bags.forEach(b => {
            if(!b.c) {
                let bx = b.x - worldX;
                ctx.fillStyle = "#fbbf24"; ctx.fillRect(bx, b.y, 30, 35);
                ctx.fillStyle = "#000"; ctx.fillText("$", bx+10, b.y+22);
                // Collision
                if(Math.abs(p.x - bx) < 30 && Math.abs((p.y-30) - b.y) < 40) {
                    b.c = true; score++; scoreEl.innerText = score;
                    if(score >= 5) msgEl.innerText = "MISSION COMPLETE! REACH THE END!";
                }
            }
        });

        // 4. Obstacles
        ctx.fillStyle = "#ef4444";
        cars.forEach(car => {
            let cx = car.x - worldX;
            ctx.fillRect(cx, 375, 60, 25);
            // Crash Logic
            if(Math.abs(p.x - cx) < 40 && p.y > 370) {
                active = false; msgEl.innerText = "💥 CRASHED! Refresh to try again.";
                msgEl.style.color = "#f87171";
            }
        });

        // 5. Player
        drawMan(p.x, p.y, p.f, p.jumping, p.dir);

        if(worldX > 3200 && score >= 5) {
            active = false; msgEl.innerText = "🏆 WINNER! CASH SECURED!";
        }

        requestAnimationFrame(loop);
    }

    canvas.focus();
    loop();
})();
</script>
"""

# 3. Render Component
st.components.v1.html(game_html, height=550)

# 4. Footer Info
st.divider()
with st.expander("About this Build"):
    st.write("""
    - **Engine:** JavaScript Canvas (Zero Python dependencies for low latency)
    - **Architecture:** Parallax 3-layer scrolling
    - **Business Model:** Full Source Code Included, Zero Subscriptions
    - **Developer:** Gesner Deslandes
    """)
