# 🎮 Achilles and Patroclus Website - COMPLETE! 

## ✅ What's Been Created

### 📄 Pages (5 Total)
1. **MainWebsite.html** - Landing page with hero, features, levels
2. **Gallery.html** - 10 interactive animation players with play/pause controls
3. **Trailer.html** - ✨ NEW! Video placeholder with "Work in Progress" badge
4. **Credits.html** - Team member profiles and project stats
5. **Donate.html** - Donation page with interactive slider

### 🎨 Design Theme: Earthy Brown & Green
**Color Palette:**
- **Dirt Brown**: `#2d2416`, `#3a2e1c`, `#3d3020` (backgrounds)
- **Forest Green**: `#6b8e23`, `#556b2f` (accents, buttons, CTAs)
- **Sage Green**: `#8fbc8f` (hover states, links)
- **Gold**: `#d4af37` (titles, highlights)
- **Cream**: `#e8dcc4`, `#b0a090` (text)

**Inspired by:** Grass, dirt, ancient battlefields, natural environments

### 🎬 Trailer Page Features
✅ "Work in Progress" badge with green gradient
✅ Large video placeholder (1000px wide, 16:9 aspect ratio)
✅ Instructions for adding video (both iframe and HTML5 video)
✅ "What to Expect" section with 4 cards:
   - Epic Combat
   - Hand-Drawn Art
   - Rich Environments
   - Compelling Story
✅ CTA section linking to Gallery and Features
✅ Fully responsive design

### 🎥 How to Add Your Video (When Ready)

**Option 1: YouTube/Vimeo (Recommended)**
```html
<!-- In Trailer.html, uncomment and replace: -->
<iframe 
    class="video-frame"
    src="https://www.youtube.com/embed/YOUR_VIDEO_ID" 
    title="Achilles and Patroclus Game Trailer" 
    frameborder="0" 
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen>
</iframe>
```

**Option 2: Local Video File**
```html
<!-- In Trailer.html, uncomment and replace: -->
<video class="video-frame" controls>
    <source src="trailer.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>
```

Then **comment out or delete** the `.video-placeholder` div section.

### 🎯 Navigation Updated
All pages now include the Trailer link in the navigation bar:
- Home → About → Features → **Trailer** → Gallery → Credits → Donate

### 📊 Complete Feature List

#### Gallery Page
- 6 Achilles animations (Front Walk, Front Idle, Back Walk, Back Idle, Side Walk, Side Idle, Side Attack)
- 3 Patroclus animations (Front Idle, Healing, Side Walk)
- Each with:
  - Play/Pause button
  - Speed slider (50ms to 500ms per frame)
  - Pixel-perfect rendering

#### Credits Page
- **Cillian Lynch**: Lead Designer, Web Developer & Programmer
- **Alan Haugh**: Environment Designer & Systems Developer
- **Dylan Cooney**: Lead Programmer & Level Designer
- **Jihan Xu**: Enemy Designer & Combat Systems
- Project statistics (100+ frames, 10 animations, 3 levels, 4 team members)

#### Donation Page
- Interactive slider ($1-$100)
- Preset amounts ($3, $5, $10, $25)
- Dynamic tier descriptions
- Impact levels breakdown
- Mentions ALL development aspects (programming, art, game design)

### 🎨 Design Highlights
✨ Earthy, natural color scheme
✨ Smooth hover animations
✨ Responsive on all devices
✨ Professional but approachable
✨ Fits the ancient Greek/battlefield theme

---

## 🚀 Next Steps

1. **Test the website** - Open MainWebsite.html in a browser
2. **Create your trailer** - Record gameplay, animations, story
3. **Upload video** - To YouTube, Vimeo, or local file
4. **Update Trailer.html** - Follow instructions in the HTML comments
5. **Deploy online** - Use GitHub Pages, Netlify, or Vercel (free!)

---

**Website Complete! Ready for your game trailer! 🎬**

Made with 💚 by Team 2
