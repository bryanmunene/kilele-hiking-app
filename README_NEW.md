# 🏔️ Kilele - Kenya's Premier Hiking Community Platform

> *Discover, track, and share your hiking adventures across Kenya's most beautiful trails*

[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/yourusername/kilele)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41.1-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎉 What's New in v2.0.0

**Social Features Release** - Transform your hiking experience with community-driven features!

- ⭐ **Trail Reviews & Ratings** - Share and read detailed hiking experiences
- 🔖 **Bookmarks System** - Save your favorite trails with personal notes
- 👥 **Social Following** - Connect with fellow hikers
- 📰 **Activity Feed** - See what your hiking community is up to
- 🏆 **38 Achievements** - Gamification across 9 categories
- 📊 **Comprehensive Statistics** - Track all your hiking metrics

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for complete feature details.

---

## ✨ Key Features

### 🗺️ Trail Discovery & Information
- Browse 8+ curated Kenyan hiking trails
- Detailed trail information (distance, elevation, duration, difficulty)
- Smart filtering and sorting
- Location-based trail discovery

### ⭐ Community Reviews
- Write detailed reviews with 1-5 star ratings
- Separate difficulty ratings
- Trail condition reporting
- Helpful voting system
- Visit date tracking

### 🎮 Gamification
- 38 unique achievements
- Progress tracking
- Point system (10-1000 points)
- 9 achievement categories:
  - Milestones, Distance, Elevation, Difficulty
  - Social, Reviews, Exploration, Consistency, Special

### 👥 Social Networking
- Follow other hikers
- Real-time activity feed
- Follower/following system
- User statistics dashboard

### 🔖 Personal Organization
- Bookmark favorite trails
- Add personal notes
- Quick access to saved trails
- Search and filter bookmarks

### 🔐 Security & Authentication
- Secure JWT authentication
- Profile picture uploads
- Two-Factor Authentication (2FA)
- Bcrypt password hashing

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip
- Git

### Installation (5 minutes)

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/kilele.git
cd kilele
```

**2. Setup Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed_data.py && python seed_achievements.py
python main.py
```
✅ Backend running at http://localhost:8000

**3. Setup Frontend** (New terminal)
```bash
cd frontend
pip install -r requirements.txt
streamlit run Home.py
```
✅ Frontend running at http://localhost:8501

**4. Create your account and start hiking! 🏔️**

---

## 📖 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Development reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Feature documentation
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (Swagger)

---

## 🛠️ Tech Stack

**Backend**
- FastAPI 0.115.0 - Modern async web framework
- SQLAlchemy 2.0.35 - ORM for database operations
- Pydantic - Data validation
- PyJWT - JWT authentication
- Bcrypt 4.0+ - Password hashing
- PyOTP - Two-factor authentication
- SQLite (dev) / PostgreSQL (production-ready)

**Frontend**
- Streamlit 1.41.1 - Python web framework
- Requests - HTTP client
- Plotly - Data visualization
- Pandas - Data manipulation

---

## 📁 Project Structure

```
Kilele Project/
├── backend/                  # FastAPI Backend
│   ├── main.py              # App entry point
│   ├── models/              # Database models (11 tables)
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API endpoints (25+)
│   └── static/              # Uploaded files
│
├── frontend/                 # Streamlit Frontend
│   ├── Home.py              # Homepage
│   └── pages/               # 12 application pages
│       ├── 🔐 Login         # Authentication
│       ├── 🗺️ Map View      # Trail browsing
│       ├── ⭐ Reviews       # Trail reviews ✨ NEW
│       ├── 🔖 Bookmarks     # Saved trails ✨ NEW
│       ├── 📰 Feed          # Activity feed ✨ NEW
│       ├── 🏆 Achievements  # Gamification ✨ NEW
│       └── 👥 Social        # Connections ✨ NEW
│
├── IMPLEMENTATION_SUMMARY.md # Feature docs
├── DEVELOPER_GUIDE.md        # Dev reference
├── USER_GUIDE.md             # User manual
└── README.md                 # This file
```

---

## 🎯 Usage Examples

### For Hikers

**Discover a Trail**
1. Open Map View
2. Filter by difficulty (Easy → Extreme)
3. Read reviews from other hikers
4. Bookmark for later

**Share Your Experience**
1. Complete a hike
2. Go to Reviews page
3. Rate the trail (1-5 stars)
4. Write detailed feedback
5. Help future hikers!

**Build Your Community**
1. Follow active hikers
2. Check your activity feed
3. See their completed hikes
4. Get inspired for your next adventure

### For Developers

**Add a New API Endpoint**
```python
# backend/routers/your_router.py
from fastapi import APIRouter, Depends
from database import get_db

router = APIRouter()

@router.get("/your-endpoint")
def your_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    return {"message": "Success"}
```

**Create a New Page**
```python
# frontend/pages/12_Your_Page.py
import streamlit as st

st.set_page_config(page_title="Your Feature", page_icon="🔥")
st.title("🔥 Your Feature")

# Add your Streamlit components
st.write("Hello, Kilele!")
```

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed development instructions.

---

## 📊 Stats

- **Lines of Code**: 5000+
- **API Endpoints**: 25+
- **Database Tables**: 11
- **Achievements**: 38
- **Frontend Pages**: 12
- **Seeded Trails**: 8

---

## 🗺️ Roadmap

### v2.1 (Next)
- [ ] Photo uploads for reviews
- [ ] Advanced search filters
- [ ] Weather integration
- [ ] Trail comparison tool

### v2.2
- [ ] Hike planning & scheduling
- [ ] Comments on reviews
- [ ] Notifications system
- [ ] Leaderboards

### v3.0
- [ ] Interactive maps
- [ ] GPS tracking
- [ ] Native mobile apps
- [ ] Offline mode

See full roadmap in [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md).

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for coding guidelines.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - For the excellent framework
- **Streamlit** - For making web apps simple
- **Kenya Wildlife Service** - For trail information
- **Community** - For feedback and support

---

## 📞 Support

- **Documentation**: See docs folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/kilele/issues)
- **Email**: support@kilele.app (coming soon)

---

## ⭐ Star Us!

If you find Kilele useful, please give us a star! It helps us grow the community.

---

**Built with ❤️ for the Kenyan hiking community**

*Happy Hiking! 🏔️*

---

*Last Updated: January 27, 2026*  
*Version: 2.0.0 - Social Features Release*
