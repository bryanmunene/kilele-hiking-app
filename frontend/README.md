# Kilele Hiking Trails - Frontend

Streamlit web application for browsing Kenyan hiking trails.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Make Sure Backend is Running
The backend API must be running on http://localhost:8000

```bash
cd ../backend
python main.py
```

### 3. Run Streamlit App
```bash
streamlit run app.py
```

The app will automatically open in your browser at http://localhost:8501

## Features

- 🏔️ Browse all Kenyan hiking trails
- 🔍 Filter by difficulty level (Easy, Moderate, Hard, Extreme)
- 📊 Sort by name, distance, duration, or difficulty
- 📱 Mobile-responsive design
- 🎨 Clean, nature-themed interface
- 🔄 Real-time data from FastAPI backend

## Usage

### Filtering
Use the sidebar to filter trails by difficulty level.

### Viewing Details
Click "View Details" on any trail card to see:
- Distance and duration
- Elevation gain
- Full description
- Trail type
- Best season to visit
- GPS coordinates

### Sorting
Sort trails by:
- Name (alphabetical)
- Distance (shortest to longest)
- Duration (quickest to longest)
- Difficulty (easiest to hardest)

## Configuration

To change the API endpoint, edit the `API_BASE_URL` in `app.py`:

```python
API_BASE_URL = "http://localhost:8000/api/v1"
```

## Troubleshooting

### "Cannot connect to backend"
- Ensure the FastAPI backend is running on port 8000
- Check that you're in the backend directory and ran `python main.py`

### Port Already in Use
If port 8501 is busy, specify a different port:
```bash
streamlit run app.py --server.port 8502
```

## Development

The app automatically reloads when you save changes to `app.py`.

To disable the "Running" indicator in the browser tab:
```bash
streamlit run app.py --server.runOnSave true
```

## Deployment

### Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo
4. Deploy!

### Other Options
- Railway
- Heroku
- Docker container
- Any Python hosting platform

**Note**: You'll need to deploy the backend separately and update `API_BASE_URL` to point to your production API.
