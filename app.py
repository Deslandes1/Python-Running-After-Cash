// --- Updated Game Logic ---
let p = { 
    x: 100, y: 340, vy: 0, 
    speed: 5, jumping: false, 
    dir: 0, // -1 for left, 1 for right, 0 for idle
    frame: 0 
};

// Movement Listeners
window.addEventListener('keydown', (e) => {
    if (e.code === 'ArrowRight' || e.code === 'KeyD') p.dir = 1;
    if (e.code === 'ArrowLeft' || e.code === 'KeyA') p.dir = -1;
    if ((e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'KeyW') && !p.jumping) {
        p.vy = -16;
        p.jumping = true;
    }
});

window.addEventListener('keyup', (e) => {
    if (['ArrowRight', 'ArrowLeft', 'KeyA', 'KeyD'].includes(e.code)) p.dir = 0;
});

function update() {
    // Horizontal Movement
    p.x += p.dir * p.speed;
    
    // Boundary Checks
    if (p.x < 20) p.x = 20;
    if (p.x > 780) p.x = 780;

    // Gravity Physics
    p.vy += 0.8; 
    p.y += p.vy;
    if (p.y > 340) { 
        p.y = 340; 
        p.vy = 0; 
        p.jumping = false; 
    }
    
    p.frame++;
    // Draw logic goes here...
}
