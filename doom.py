import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DOOM-ish (Streamlit)", page_icon="🔫", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp{
      background:
        radial-gradient(1000px 600px at 15% 15%, rgba(255,0,60,.18), transparent 60%),
        radial-gradient(900px 600px at 80% 20%, rgba(0,255,255,.10), transparent 55%),
        linear-gradient(180deg,#050014,#02000a);
      color: rgba(255,255,255,.92);
    }
    .card{
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 18px;
      padding: 16px;
      box-shadow: 0 0 35px rgba(255,0,60,.12), 0 0 40px rgba(0,255,255,.08);
      backdrop-filter: blur(10px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="card">
      <div style="font-weight:900;font-size:2.1rem;letter-spacing:1px;
                  text-shadow:0 0 14px rgba(255,0,60,.45),0 0 16px rgba(0,255,255,.20);">
        DOOM-ish Raycaster + HUD + Wapensprite
      </div>
      <div style="opacity:.82;margin-top:6px;">
        Besturing: <b>WASD</b> lopen · <b>←/→</b> draaien · <b>Shift</b> sprint · <b>Space</b> schieten · <b>R</b> reset.
        Klik één keer in het speelveld voor focus.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

left, right = st.columns([0.36, 0.64], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎛️ Instellingen (kwaliteit vs snelheid)")
    fov_deg = st.slider("Field of view (FOV)", 55, 100, 75)
    cols = st.slider("Render kolommen (kwaliteit)", 140, 520, 320, step=10)
    mouse_look = st.slider("Draaisnelheid (←/→)", 20, 90, 45)
    brightness = st.slider("Brightness", 70, 140, 105)
    enemy_count = st.slider("Enemies", 1, 10, 6)
    show_minimap = st.checkbox("Minimap", value=False)
    st.caption("Meer kolommen = mooier maar zwaarder. Probeer 280–380.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- HTML/JS template (NOT an f-string) ----------
HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    html,body{margin:0;padding:0;background:transparent;}
    canvas{
      width:100%;
      height:620px;
      border-radius:18px;
      border:1px solid rgba(255,255,255,.12);
      outline:none;
      background:
        radial-gradient(900px 520px at 20% 15%, rgba(255,0,60,.10), transparent 60%),
        radial-gradient(900px 520px at 80% 20%, rgba(0,255,255,.08), transparent 55%),
        linear-gradient(180deg, rgba(10,0,25,.65), rgba(3,0,10,.78));
      box-shadow: 0 0 0 1px rgba(0,255,255,.08) inset, 0 0 40px rgba(255,0,60,.12);
    }
  </style>
</head>
<body>
  <canvas id="c" tabindex="0"></canvas>

  <script>
  // -------------------- Config (injected) --------------------
  const CFG = {
    FOV_DEG: %%FOV_DEG%%,
    COLS: %%COLS%%,
    TURN_SPEED: %%TURN_SPEED%%,     // degrees/sec-ish feel
    BRIGHT: %%BRIGHT%% / 100,
    ENEMIES: %%ENEMIES%%,
    MINIMAP: %%MINIMAP%%
  };

  // -------------------- Canvas setup --------------------
  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d");

  function resize(){
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
  }
  window.addEventListener("resize", resize);

  // -------------------- Map (multi-wall types) --------------------
  // 0 empty, 1/2/3 different wall textures
  const mapW = 18, mapH = 13;
  const mapRows = [
    "111111111111111111",
    "100000000000000001",
    "102222022222220201",
    "100001000100000001",
    "103301330133013301",
    "100100000001000001",
    "111101011101110101",
    "100001000001000001",
    "102222022222220201",
    "100000000000000001",
    "100000011000000001",
    "100000000000000001",
    "111111111111111111",
  ];
  const map = mapRows.map(r => r.split("").map(ch => parseInt(ch,10)));

  function isWall(x,y){
    const mx = Math.floor(x), my = Math.floor(y);
    if(mx<0||my<0||mx>=mapW||my>=mapH) return 1;
    return map[my][mx];
  }

  // -------------------- Procedural textures --------------------
  // create 3 wall textures (pixel style)
  function makeWallTex(seedR, seedG, seedB){
    const W=64,H=64;
    const t = document.createElement("canvas");
    t.width=W; t.height=H;
    const g = t.getContext("2d");
    const img = g.createImageData(W,H);
    for(let y=0;y<H;y++){
      for(let x=0;x<W;x++){
        const i=(y*W+x)*4;
        // bricks-ish
        const brick = ((Math.floor(y/8)%2)*4 + Math.floor(x/8))%2;
        const grout = (x%8===0) || (y%8===0);
        let v = 0.6 + 0.4*Math.sin((x*0.35)+(y*0.18));
        v *= grout ? 0.55 : 1.0;
        v *= brick ? 0.95 : 1.05;

        // noise
        const n = (Math.sin(x*12.9898 + y*78.233)*43758.5453)%1;
        v *= 0.92 + 0.18*n;

        img.data[i+0] = Math.max(0, Math.min(255, seedR*v));
        img.data[i+1] = Math.max(0, Math.min(255, seedG*v));
        img.data[i+2] = Math.max(0, Math.min(255, seedB*v));
        img.data[i+3] = 255;
      }
    }
    g.putImageData(img,0,0);
    return t;
  }

  const TEX = {
    1: makeWallTex(200, 60, 120),   // red-ish
    2: makeWallTex(80, 180, 200),   // cyan-ish
    3: makeWallTex(170, 160, 70),   // yellow-ish
  };

  // -------------------- Player --------------------
  const FOV = CFG.FOV_DEG * Math.PI/180;
  let player = {
    x: 2.6, y: 2.6,
    a: 0,
    hp: 100,
    armor: 0,
    ammo: 40,
    score: 0,
    alive: true,
    hurtTimer: 0
  };

  // -------------------- Enemies (sprites) --------------------
  function spawnEnemies(n){
    const arr = [];
    let tries=0;
    while(arr.length<n && tries<8000){
      tries++;
      const x = 1.5 + Math.random()*(mapW-3);
      const y = 1.5 + Math.random()*(mapH-3);
      const w = isWall(x,y);
      if(w===0 && Math.hypot(x-player.x,y-player.y)>3.0){
        arr.push({
          x,y,
          hp: 40,
          t: Math.random()*100,
          flash: 0
        });
      }
    }
    return arr;
  }
  let enemies = spawnEnemies(CFG.ENEMIES);

  // -------------------- Input --------------------
  const keys = {};
  window.addEventListener("keydown", (e)=>{
    keys[e.key.toLowerCase()] = true;
    if(e.key === " "){
      e.preventDefault();
      shoot();
    }
    if(e.key.toLowerCase()==="r"){
      e.preventDefault();
      resetAll();
    }
  });
  window.addEventListener("keyup", (e)=>{ keys[e.key.toLowerCase()] = false; });
  canvas.addEventListener("click", ()=>canvas.focus());

  // -------------------- Shoot + FX --------------------
  let muzzle = 0;
  let recoil = 0;
  let camShake = 0;

  function lineOfSight(ax,ay,bx,by){
    const dx=bx-ax, dy=by-ay;
    const dist = Math.hypot(dx,dy);
    const steps = Math.max(10, Math.floor(dist*18));
    for(let i=1;i<steps;i++){
      const t=i/steps;
      const x=ax+dx*t;
      const y=ay+dy*t;
      if(isWall(x,y)!==0) return false;
    }
    return true;
  }

  function shoot(){
    if(!player.alive) return;
    if(player.ammo<=0) return;

    player.ammo--;
    muzzle = 7;
    recoil = 10;
    camShake = 7;

    // find enemy in crosshair cone + LOS
    const dirx = Math.cos(player.a), diry = Math.sin(player.a);
    let best = null;

    for(const e of enemies){
      if(e.hp<=0) continue;
      const vx=e.x-player.x, vy=e.y-player.y;
      const dist=Math.hypot(vx,vy);
      const ang=Math.atan2(vy,vx);
      let d = ang - player.a;
      d = Math.atan2(Math.sin(d), Math.cos(d));
      const cone = (FOV / 18); // a small cone
      if(Math.abs(d) < cone && dist < 10 && lineOfSight(player.x,player.y,e.x,e.y)){
        if(best===null || dist<best.dist) best={e,dist};
      }
    }

    if(best){
      best.e.hp -= 22;
      best.e.flash = 6;
      if(best.e.hp<=0) player.score += 150;
      else player.score += 10;
    }
  }

  // -------------------- Raycasting (DDA) --------------------
  function castRay(angle){
    const rayDirX = Math.cos(angle);
    const rayDirY = Math.sin(angle);

    let mapX = Math.floor(player.x);
    let mapY = Math.floor(player.y);

    const deltaDistX = Math.abs(1 / (rayDirX || 1e-9));
    const deltaDistY = Math.abs(1 / (rayDirY || 1e-9));

    let stepX, stepY;
    let sideDistX, sideDistY;

    if(rayDirX < 0){
      stepX = -1;
      sideDistX = (player.x - mapX) * deltaDistX;
    } else {
      stepX = 1;
      sideDistX = (mapX + 1.0 - player.x) * deltaDistX;
    }
    if(rayDirY < 0){
      stepY = -1;
      sideDistY = (player.y - mapY) * deltaDistY;
    } else {
      stepY = 1;
      sideDistY = (mapY + 1.0 - player.y) * deltaDistY;
    }

    let hitType = 0;
    let side = 0; // 0 x-side, 1 y-side

    // DDA loop
    for(let i=0;i<64;i++){
      if(sideDistX < sideDistY){
        sideDistX += deltaDistX;
        mapX += stepX;
        side = 0;
      } else {
        sideDistY += deltaDistY;
        mapY += stepY;
        side = 1;
      }
      if(mapX<0||mapY<0||mapX>=mapW||mapY>=mapH){
        hitType = 1;
        break;
      }
      hitType = map[mapY][mapX];
      if(hitType !== 0) break;
    }

    let perpDist;
    if(side === 0) perpDist = (sideDistX - deltaDistX);
    else perpDist = (sideDistY - deltaDistY);

    // texture coordinate
    let wallX;
    if(side === 0) wallX = player.y + perpDist * rayDirY;
    else wallX = player.x + perpDist * rayDirX;
    wallX -= Math.floor(wallX);

    return { dist: perpDist, type: hitType, side, wallX };
  }

  function shade(d){
    // distance shading
    const s = 1 / (1 + d*d*0.14);
    return Math.max(0, Math.min(1, s * CFG.BRIGHT));
  }

  // -------------------- Enemy AI --------------------
  function updateEnemies(){
    for(const e of enemies){
      if(e.hp<=0) continue;
      e.t += 0.018;
      if(e.flash>0) e.flash--;

      const vx = player.x - e.x;
      const vy = player.y - e.y;
      const dist = Math.hypot(vx,vy);

      const los = dist < 9 && lineOfSight(e.x,e.y,player.x,player.y);

      if(los && dist > 0.85 && player.alive){
        const speed = 0.010 + 0.004*Math.sin(e.t*2.2);
        const nx = e.x + (vx/dist)*speed;
        const ny = e.y + (vy/dist)*speed;
        if(isWall(nx,e.y)===0) e.x = nx;
        if(isWall(e.x,ny)===0) e.y = ny;
      }

      if(dist < 0.95 && player.alive){
        // damage tick
        const dmg = 0.22;
        player.hp -= dmg;
        player.hurtTimer = 18;
        if(player.hp <= 0){
          player.hp = 0;
          player.alive = false;
        }
      }
    }
  }

  // -------------------- Movement --------------------
  function move(dt){
    if(!player.alive) return;

    const rot = (CFG.TURN_SPEED * Math.PI/180) * dt;
    if(keys["arrowleft"]) player.a -= rot;
    if(keys["arrowright"]) player.a += rot;

    const forward = (keys["w"]?1:0) - (keys["s"]?1:0);
    const strafe  = (keys["d"]?1:0) - (keys["a"]?1:0);
    const sprint = keys["shift"] ? 1.75 : 1.0;

    const baseSpeed = 2.7; // units/sec feel
    const sp = baseSpeed * sprint * dt;

    const fx = Math.cos(player.a), fy = Math.sin(player.a);
    const sx = Math.cos(player.a + Math.PI/2), sy = Math.sin(player.a + Math.PI/2);

    const dx = (fx*forward + sx*strafe) * sp;
    const dy = (fy*forward + sy*strafe) * sp;

    const nx = player.x + dx;
    const ny = player.y + dy;

    if(isWall(nx, player.y)===0) player.x = nx;
    if(isWall(player.x, ny)===0) player.y = ny;

    // gun bob based on movement
    if(forward!==0 || strafe!==0) gunBob += dt * (sprint>1 ? 10 : 7);
  }

  function resetAll(){
    player = { x:2.6,y:2.6,a:0,hp:100,armor:0,ammo:40,score:0,alive:true,hurtTimer:0 };
    enemies = spawnEnemies(CFG.ENEMIES);
    muzzle = 0; recoil=0; camShake=0; gunBob=0;
  }

  // -------------------- HUD + Weapon sprite --------------------
  // Procedural pixel-art gun sprite
  const gunSprite = document.createElement("canvas");
  gunSprite.width = 160; gunSprite.height = 120;
  const gctx = gunSprite.getContext("2d");

  function drawGunSprite(){
    gctx.clearRect(0,0,gunSprite.width,gunSprite.height);

    // hands
    function pixRect(x,y,w,h,fill,stroke){
      gctx.fillStyle = fill; gctx.fillRect(x,y,w,h);
      if(stroke){ gctx.strokeStyle=stroke; gctx.strokeRect(x+0.5,y+0.5,w-1,h-1); }
    }

    // base shading
    pixRect(40,70,32,30,"#9b6a3f","#2a1b12");   // left hand
    pixRect(88,70,32,30,"#9b6a3f","#2a1b12");   // right hand
    pixRect(44,74,24,18,"#b37b4a",null);
    pixRect(92,74,24,18,"#b37b4a",null);

    // gun body
    pixRect(58,48,44,40,"#3a3a3f","#101014");
    pixRect(62,52,36,16,"#5a5a62",null);
    pixRect(70,40,20,12,"#2a2a2e","#0d0d10"); // top
    pixRect(74,30,12,12,"#1f1f22","#0b0b0d"); // sight
    pixRect(78,18,4,12,"#151518",null);

    // barrel
    pixRect(76,44,8,30,"#1a1a1d","#070709");
    pixRect(74,68,12,8,"#0f0f11","#050506");

    // neon accents
    gctx.shadowBlur = 10;
    gctx.shadowColor = "rgba(0,255,255,0.45)";
    pixRect(60,62,40,4,"rgba(0,255,255,0.45)",null);
    gctx.shadowBlur = 0;

    // pixel edges
    gctx.globalAlpha = 0.25;
    pixRect(58,48,44,1,"#ffffff",null);
    pixRect(58,48,1,40,"#ffffff",null);
    gctx.globalAlpha = 1;
  }
  drawGunSprite();

  // HUD face (changes with HP + hurt)
  function drawFace(x,y,sz){
    ctx.save();
    ctx.translate(x,y);

    // base frame
    ctx.fillStyle = "rgba(0,0,0,0.55)";
    ctx.fillRect(0,0,sz,sz);
    ctx.strokeStyle = "rgba(255,255,255,0.18)";
    ctx.strokeRect(0.5,0.5,sz-1,sz-1);

    const hp = player.hp;
    const hurt = player.hurtTimer > 0;

    // skin tone shifts
    const r = hurt ? 220 : 190;
    const g = hurt ? 90 : 140;
    const b = hurt ? 90 : 120;

    // face
    ctx.fillStyle = `rgb(${r},${g},${b})`;
    ctx.fillRect(10,10,sz-20,sz-20);

    // eyes
    ctx.fillStyle = "rgba(0,0,0,0.75)";
    const eyeY = 22;
    const eyeW = 10, eyeH=6;
    ctx.fillRect(22,eyeY,eyeW,eyeH);
    ctx.fillRect(sz-22-eyeW,eyeY,eyeW,eyeH);

    // eyebrows (angry when low hp)
    ctx.strokeStyle = "rgba(0,0,0,0.8)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    if(hp > 60){
      ctx.moveTo(18,18); ctx.lineTo(36,16);
      ctx.moveTo(sz-18,18); ctx.lineTo(sz-36,16);
    } else if(hp > 25){
      ctx.moveTo(18,16); ctx.lineTo(36,20);
      ctx.moveTo(sz-18,16); ctx.lineTo(sz-36,20);
    } else {
      ctx.moveTo(18,14); ctx.lineTo(36,24);
      ctx.moveTo(sz-18,14); ctx.lineTo(sz-36,24);
    }
    ctx.stroke();

    // mouth
    ctx.lineWidth = 4;
    ctx.beginPath();
    if(!player.alive){
      ctx.moveTo(22,sz-26); ctx.lineTo(sz-22,sz-26);
    } else if(hp > 60){
      ctx.moveTo(26,sz-26); ctx.lineTo(sz-26,sz-26);
    } else if(hp > 25){
      ctx.moveTo(26,sz-24); ctx.lineTo(sz-26,sz-28);
    } else {
      ctx.moveTo(26,sz-22); ctx.lineTo(sz-26,sz-32);
    }
    ctx.stroke();

    ctx.restore();
  }

  // -------------------- Render --------------------
  let gunBob = 0;
  let lastTs = performance.now();
  const zbuf = [];

  function drawMinimap(){
    const w = canvas.getBoundingClientRect().width;
    const pad = 12;
    const size = 180;
    const cell = size / Math.max(mapW,mapH);

    ctx.save();
    ctx.globalAlpha = 0.9;
    ctx.translate(pad,pad);
    ctx.fillStyle = "rgba(0,0,0,0.45)";
    ctx.fillRect(0,0,size,size);
    ctx.strokeStyle = "rgba(255,255,255,0.20)";
    ctx.strokeRect(0.5,0.5,size-1,size-1);

    for(let y=0;y<mapH;y++){
      for(let x=0;x<mapW;x++){
        const v = map[y][x];
        if(v!==0){
          ctx.fillStyle = v===1 ? "rgba(255,0,60,0.45)" : (v===2 ? "rgba(0,255,255,0.35)" : "rgba(255,220,80,0.35)");
          ctx.fillRect(x*cell,y*cell,cell,cell);
        }
      }
    }
    // enemies
    for(const e of enemies){
      if(e.hp<=0) continue;
      ctx.fillStyle = "rgba(255,120,160,0.9)";
      ctx.fillRect(e.x*cell-2,e.y*cell-2,4,4);
    }
    // player
    ctx.fillStyle = "rgba(255,255,255,0.95)";
    ctx.beginPath();
    ctx.arc(player.x*cell, player.y*cell, 4, 0, Math.PI*2);
    ctx.fill();
    ctx.strokeStyle = "rgba(0,255,255,0.6)";
    ctx.beginPath();
    ctx.moveTo(player.x*cell, player.y*cell);
    ctx.lineTo((player.x+Math.cos(player.a)*0.8)*cell, (player.y+Math.sin(player.a)*0.8)*cell);
    ctx.stroke();

    ctx.restore();
  }

  function draw(){
    const w = canvas.getBoundingClientRect().width;
    const h = canvas.getBoundingClientRect().height;

    // camera shake
    let shx=0, shy=0;
    if(camShake>0){
      shx = (Math.random()-0.5)*camShake;
      shy = (Math.random()-0.5)*camShake;
      camShake *= 0.85;
      if(camShake<0.2) camShake=0;
    }

    ctx.save();
    ctx.translate(shx,shy);

    // clear
    ctx.clearRect(-50,-50,w+100,h+100);

    // ceiling + floor gradients
    const sky = ctx.createLinearGradient(0,0,0,h*0.55);
    sky.addColorStop(0,"rgba(0,255,255,0.08)");
    sky.addColorStop(1,"rgba(0,0,0,0)");
    ctx.fillStyle = sky;
    ctx.fillRect(0,0,w,h*0.55);

    const floor = ctx.createLinearGradient(0,h*0.45,0,h);
    floor.addColorStop(0,"rgba(255,0,60,0.05)");
    floor.addColorStop(1,"rgba(0,0,0,0.65)");
    ctx.fillStyle = floor;
    ctx.fillRect(0,h*0.45,w,h);

    // walls
    const halfF = FOV/2;
    const colW = w / CFG.COLS;
    zbuf.length = CFG.COLS;

    for(let i=0;i<CFG.COLS;i++){
      const t = i/(CFG.COLS-1);
      const ang = player.a - halfF + t*FOV;
      const hit = castRay(ang);

      const corrected = hit.dist * Math.cos(ang - player.a);
      zbuf[i] = corrected;

      const wallH = Math.min(h, (h*0.98) / Math.max(0.0001, corrected));
      const y0 = (h - wallH)/2;

      const s = shade(corrected) * (hit.side===1 ? 0.85 : 1.0); // side shading
      const tex = TEX[hit.type] || TEX[1];

      // sample texture column
      const tx = Math.floor(hit.wallX * 64);

      // draw scaled slice
      ctx.globalAlpha = 1.0;
      ctx.drawImage(tex, tx, 0, 1, 64, i*colW, y0, colW+1, wallH);

      // apply shading overlay
      ctx.fillStyle = `rgba(0,0,0,${(1.0 - s) * 0.85})`;
      ctx.fillRect(i*colW, y0, colW+1, wallH);

      // subtle neon edge
      ctx.fillStyle = `rgba(0,255,255,${0.04*s})`;
      ctx.fillRect(i*colW, y0, 1, wallH);
    }

    // sprites (enemies) back-to-front
    const sprites = enemies
      .filter(e=>e.hp>0)
      .map(e=>{
        const dx=e.x-player.x, dy=e.y-player.y;
        return { e, dist: Math.hypot(dx,dy), ang: Math.atan2(dy,dx) };
      })
      .sort((a,b)=>b.dist-a.dist);

    for(const sp of sprites){
      let rel = sp.ang - player.a;
      rel = Math.atan2(Math.sin(rel), Math.cos(rel));
      if(Math.abs(rel) > halfF + 0.35) continue;

      const sx = ((rel + halfF)/FOV) * w;
      const size = Math.min(h, (h*0.70) / Math.max(0.0001, sp.dist));
      const sy = h*0.5;

      const col = Math.floor((sx / w) * CFG.COLS);
      if(col>=0 && col<CFG.COLS && sp.dist > zbuf[col]) continue; // occluded

      const alpha = Math.max(0.15, Math.min(0.95, 1/(1+sp.dist*0.45)));

      ctx.save();
      ctx.globalAlpha = alpha;

      // glow
      ctx.shadowBlur = 26;
      ctx.shadowColor = sp.e.flash>0 ? "rgba(255,255,255,0.7)" : "rgba(255,0,60,0.45)";

      // enemy body
      ctx.beginPath();
      ctx.arc(sx, sy, size*0.22, 0, Math.PI*2);
      ctx.fillStyle = sp.e.flash>0 ? "rgba(255,255,255,0.92)" : "rgba(255,90,140,0.92)";
      ctx.fill();

      // face detail
      ctx.shadowBlur = 0;
      ctx.globalAlpha = alpha*0.85;
      ctx.fillStyle = "rgba(0,0,0,0.55)";
      ctx.fillRect(sx - size*0.08, sy - size*0.05, size*0.06, size*0.05);
      ctx.fillRect(sx + size*0.02, sy - size*0.05, size*0.06, size*0.05);

      // outline
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = "rgba(255,255,255,0.28)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(sx, sy, size*0.22, 0, Math.PI*2);
      ctx.stroke();

      ctx.restore();
    }

    // crosshair
    ctx.save();
    ctx.globalAlpha = 0.82;
    ctx.strokeStyle = "rgba(255,255,255,0.72)";
    ctx.lineWidth = 2;
    const cx=w/2, cy=h/2;
    ctx.beginPath();
    ctx.moveTo(cx-10,cy); ctx.lineTo(cx-4,cy);
    ctx.moveTo(cx+4,cy);  ctx.lineTo(cx+10,cy);
    ctx.moveTo(cx,cy-10); ctx.lineTo(cx,cy-4);
    ctx.moveTo(cx,cy+4);  ctx.lineTo(cx,cy+10);
    ctx.stroke();
    ctx.restore();

    // hurt vignette
    if(player.hurtTimer>0){
      ctx.save();
      ctx.globalAlpha = Math.min(0.45, player.hurtTimer/30);
      const g = ctx.createRadialGradient(cx, cy, 10, cx, cy, Math.max(w,h)*0.65);
      g.addColorStop(0, "rgba(255,0,60,0.00)");
      g.addColorStop(1, "rgba(255,0,60,0.35)");
      ctx.fillStyle = g;
      ctx.fillRect(0,0,w,h);
      ctx.restore();
    }

    // muzzle flash
    if(muzzle>0){
      ctx.save();
      ctx.globalAlpha = Math.min(0.55, muzzle/10);
      const g = ctx.createRadialGradient(cx, cy, 10, cx, cy, 260);
      g.addColorStop(0,"rgba(255,255,255,0.65)");
      g.addColorStop(0.25,"rgba(255,0,60,0.25)");
      g.addColorStop(1,"rgba(0,0,0,0)");
      ctx.fillStyle=g;
      ctx.fillRect(0,0,w,h);
      ctx.restore();
      muzzle--;
    }

    // HUD bottom panel
    const hudH = 104;
    ctx.save();
    ctx.fillStyle = "rgba(0,0,0,0.62)";
    ctx.fillRect(0, h-hudH, w, hudH);
    ctx.strokeStyle = "rgba(255,255,255,0.14)";
    ctx.strokeRect(0.5, h-hudH+0.5, w-1, hudH-1);

    // top separator line (Doom-ish)
    ctx.strokeStyle = "rgba(0,255,255,0.15)";
    ctx.beginPath();
    ctx.moveTo(0, h-hudH);
    ctx.lineTo(w, h-hudH);
    ctx.stroke();

    // labels
    ctx.font = "800 16px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial";
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    ctx.fillText("AMMO", 18, h-hudH+26);
    ctx.fillText("HEALTH", 140, h-hudH+26);
    ctx.fillText("ARMOR", 270, h-hudH+26);
    ctx.fillText("SCORE", 410, h-hudH+26);

    // values
    ctx.font = "900 30px ui-sans-serif, system-ui";
    ctx.shadowBlur = 14;

    ctx.shadowColor = "rgba(255,0,60,0.35)";
    ctx.fillStyle = "rgba(255,0,60,0.95)";
    ctx.fillText(String(player.ammo).padStart(2,"0"), 18, h-hudH+66);

    ctx.shadowColor = "rgba(0,255,255,0.28)";
    ctx.fillStyle = "rgba(0,255,255,0.95)";
    ctx.fillText(Math.round(player.hp) + "%", 140, h-hudH+66);

    ctx.shadowColor = "rgba(255,220,80,0.28)";
    ctx.fillStyle = "rgba(255,220,80,0.95)";
    ctx.fillText(String(Math.round(player.armor)) + "%", 270, h-hudH+66);

    ctx.shadowBlur = 0;
    ctx.fillStyle = "rgba(255,255,255,0.92)";
    ctx.fillText(String(player.score), 410, h-hudH+66);

    // face
    drawFace(w-112, h-hudH+14, 78);

    // status
    ctx.font = "700 14px ui-sans-serif, system-ui";
    ctx.fillStyle = "rgba(255,255,255,0.75)";
    ctx.fillText(player.alive ? "RUN 'N GUN" : "YOU DIED  (press R)", w-240, h-hudH+26);

    ctx.restore();

    // weapon sprite (center bottom)
    // bob + recoil
    const bobX = Math.sin(gunBob)*6;
    const bobY = Math.abs(Math.cos(gunBob))*8;
    if(recoil>0){ recoil *= 0.72; if(recoil<0.2) recoil=0; }

    const gunW = 280;
    const gunH = 210;
    const gx = (w/2) - gunW/2 + bobX;
    const gy = h - hudH - gunH + 40 + bobY - recoil*2.2;

    ctx.save();
    // glow
    ctx.globalAlpha = 0.95;
    ctx.shadowBlur = 18;
    ctx.shadowColor = "rgba(255,0,60,0.22)";
    ctx.drawImage(gunSprite, gx, gy, gunW, gunH);

    // extra neon accent
    ctx.shadowBlur = 14;
    ctx.shadowColor = "rgba(0,255,255,0.22)";
    ctx.globalAlpha = 0.35;
    ctx.drawImage(gunSprite, gx+2, gy+1, gunW, gunH);

    ctx.restore();

    // minimap
    if(CFG.MINIMAP) drawMinimap();

    ctx.restore(); // shake translate
  }

  // -------------------- Main loop --------------------
  function tick(ts){
    const dt = Math.min(0.05, (ts-lastTs)/1000);
    lastTs = ts;

    if(player.hurtTimer>0) player.hurtTimer--;

    // if dead, allow slow turn only
    move(dt);
    updateEnemies();

    // tiny ammo pickup every so often (keeps it fun)
    // (purely arcade-ish)
    if(player.alive && player.ammo < 10 && Math.random() < 0.006){
      player.ammo += 3;
      player.score += 5;
    }

    draw();
    requestAnimationFrame(tick);
  }

  // Start
  resize();
  canvas.focus();
  requestAnimationFrame(tick);
  </script>
</body>
</html>
"""

# Inject values safely via replace (no f-string -> no curly brace issues)
HTML = (
    HTML.replace("%%FOV_DEG%%", str(int(fov_deg)))
        .replace("%%COLS%%", str(int(cols)))
        .replace("%%TURN_SPEED%%", str(int(mouse_look)))
        .replace("%%BRIGHT%%", str(int(brightness)))
        .replace("%%ENEMIES%%", str(int(enemy_count)))
        .replace("%%MINIMAP%%", "true" if show_minimap else "false")
)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔫 Speelveld")
    components.html(HTML, height=650, scrolling=False)
    st.caption("Tip: klik in het canvas voor focus. Space schiet. R reset.")
    st.markdown("</div>", unsafe_allow_html=True)
