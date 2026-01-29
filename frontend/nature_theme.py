"""Reusable Kilele Explorers theme CSS - based on logo colors"""

NATURE_CSS = """
    <style>
    /* Main app background - mountain sky gradient from logo */
    .stApp {
        background: linear-gradient(180deg, 
            #e3f2fd 0%,
            #bbdefb 25%, 
            #90caf9 50%,
            #64b5f6 100%
        );
        background-attachment: fixed;
    }
    
    /* Mobile-first responsive viewport */
    @viewport {
        width: device-width;
        zoom: 1.0;
    }
    
    /* Sidebar with logo navy blue theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            #1e3a5f 0%, 
            #2c4563 50%,
            #3a5270 100%
        ) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Hero/Header sections - deep navy from compass */
    .hero-section, .header-section {
        background: linear-gradient(135deg, 
            #1e3a5f 0%, 
            #2c4563 25%,
            #4a6fa5 50%,
            #5b7ea8 100%
        );
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 12px 30px rgba(30, 58, 95, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Mobile responsive hero */
    @media (max-width: 768px) {
        .hero-section, .header-section {
            padding: 20px 15px;
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.2);
        }
    }
    
    /* Content cards with mountain blue theme */
    .content-card, .feature-card {
        background: linear-gradient(135deg, 
            #ffffff 0%, 
            #e3f2fd 50%,
            #bbdefb 100%
        );
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #90caf9;
        box-shadow: 0 4px 15px rgba(100, 181, 246, 0.15);
        transition: all 0.3s ease;
        margin-bottom: 15px;
        color: #1e3a5f;
    }
    
    .content-card:hover, .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(100, 181, 246, 0.25);
        border-color: #64b5f6;
    }
    
    /* Mobile responsive cards */
    @media (max-width: 768px) {
        .content-card, .feature-card {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
    }
    
    /* Stats boxes - medium blue from logo */
    .stat-box, .metric-box {
        background: linear-gradient(135deg, 
            #2c4563 0%, 
            #4a6fa5 50%,
            #5b7ea8 100%
        );
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(44, 69, 99, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-number, .metric-number {
        font-size: 36px;
        font-weight: bold;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Mobile responsive stats */
    @media (max-width: 768px) {
        .stat-box, .metric-box {
            padding: 12px;
            margin-bottom: 10px;
        }
        .stat-number, .metric-number {
            font-size: 24px;
        }
    }
    
    /* Buttons with compass blue theme */
    .stButton>button {
        background: linear-gradient(135deg, #4a6fa5 0%, #5b7ea8 100%) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(74, 111, 165, 0.4) !important;
    }
    
    /* Input fields with blue mountain border */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        border: 2px solid #90caf9 !important;
        background: rgba(255, 255, 255, 0.98) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        line-height: 1.6 !important;
        transition: all 0.3s ease !important;
        color: #1e3a5f !important;
        font-weight: 500 !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #2c4563 !important;
        box-shadow: 0 0 0 4px rgba(74, 111, 165, 0.2) !important;
        background: rgba(255, 255, 255, 1) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
    }
    
    /* Mobile-optimized form inputs */
    @media (max-width: 768px) {
        /* Make inputs larger and easier to tap */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select,
        .stNumberInput>div>div>input {
            font-size: 18px !important;
            padding: 16px 20px !important;
            border-radius: 14px !important;
            border-width: 2.5px !important;
            min-height: 52px !important;
            -webkit-appearance: none !important;
            appearance: none !important;
        }
        
        /* Better spacing between form elements */
        .stTextInput, .stTextArea, .stNumberInput, .stSelectbox {
            margin-bottom: 20px !important;
        }
        
        /* Dropdown arrow on mobile */
        .stSelectbox>div>div>select {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='%232c4563'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E") !important;
            background-repeat: no-repeat !important;
            background-position: right 16px center !important;
            background-size: 24px !important;
            padding-right: 52px !important;
        }
        
        /* Number input controls */
        .stNumberInput>div>div>button {
            min-width: 48px !important;
            min-height: 48px !important;
            font-size: 24px !important;
            border-radius: 12px !important;
            background: linear-gradient(135deg, #4a6fa5 0%, #5b7ea8 100%) !important;
            color: white !important;
            border: none !important;
            margin: 0 4px !important;
        }
        
        .stNumberInput>div>div>button:active {
            transform: scale(0.95) !important;
        }
        
        /* Text area needs more height on mobile */
        .stTextArea>div>div>textarea {
            min-height: 120px !important;
        }
        
        /* Focus state more prominent on mobile */
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus,
        .stSelectbox>div>div>select:focus,
        .stNumberInput>div>div>input:focus {
            box-shadow: 0 0 0 5px rgba(74, 111, 165, 0.25) !important;
            border-width: 3px !important;
        }
    }
    
    /* Input labels - make them more prominent */
    .stTextInput>label,
    .stTextArea>label,
    .stSelectbox>label,
    .stNumberInput>label {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #1e3a5f !important;
        margin-bottom: 10px !important;
        display: block !important;
        letter-spacing: 0.3px !important;
    }
    
    /* Mobile labels */
    @media (max-width: 768px) {
        .stTextInput>label,
        .stTextArea>label,
        .stSelectbox>label,
        .stNumberInput>label {
            font-size: 18px !important;
            margin-bottom: 12px !important;
        }
    }
    
    /* Placeholder text - clearer on mobile */
    .stTextInput>div>div>input::placeholder,
    .stTextArea>div>div>textarea::placeholder {
        color: #78909c !important;
        opacity: 0.85 !important;
        font-style: italic !important;
        font-weight: 400 !important;
    }
    
    @media (max-width: 768px) {
        .stTextInput>div>div>input::placeholder,
        .stTextArea>div>div>textarea::placeholder {
            font-size: 16px !important;
        }
    }
    
    /* Expander with mountain theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
        border: 2px solid #90caf9 !important;
        border-radius: 8px !important;
    }
    
    /* Tabs with mountain blue colors */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #2c4563 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4a6fa5 0%, #5b7ea8 100%) !important;
        color: white !important;
    }
    
    /* Difficulty badges */
    .difficulty-easy { 
        color: #64b5f6; 
        font-weight: bold; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    .difficulty-moderate { 
        color: #ffa726; 
        font-weight: bold; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    .difficulty-hard { 
        color: #ef5350; 
        font-weight: bold; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    .difficulty-extreme { 
        color: #ab47bc; 
        font-weight: bold; 
        text-shadow: 0 1px 2px rgba(0,0,0,0.1); 
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
        border-left: 5px solid #64b5f6 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%) !important;
        border-left: 5px solid #ef5350 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #e3f2fd 0%, #90caf9 100%) !important;
        border-left: 5px solid #42a5f5 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
        border-left: 5px solid #42a5f5 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 2px solid #90caf9 !important;
        border-radius: 8px !important;
    }
    
    /* Card hover effects */
    .hike-card, .trail-card, .user-card {
        background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 5px solid #4a6fa5;
        box-shadow: 0 4px 12px rgba(74, 111, 165, 0.15);
        transition: all 0.3s ease;
    }
    
    .hike-card:hover, .trail-card:hover, .user-card:hover {
        box-shadow: 0 8px 20px rgba(74, 111, 165, 0.25);
        transform: translateY(-2px);
    }
    
    /* Metric styling */
    .big-metric {
        font-size: 42px;
        font-weight: bold;
        color: #2c4563;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1e3a5f !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* ===== MOBILE RESPONSIVENESS ===== */
    
    /* Mobile: screens smaller than 768px */
    @media only screen and (max-width: 768px) {
        /* Reduce padding on mobile */
        .stApp {
            padding: 10px !important;
        }
        
        /* Enhanced mobile input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select,
        .stNumberInput>div>div>input {
            font-size: 16px !important;
            padding: 14px 18px !important;
            min-height: 48px !important;
            border-radius: 10px !important;
            border-width: 2px !important;
        }
        
        /* Textarea specific */
        .stTextArea>div>div>textarea {
            min-height: 120px !important;
            resize: vertical !important;
        }
        
        /* Labels larger on mobile */
        .stTextInput>label,
        .stTextArea>label,
        .stSelectbox>label,
        .stNumberInput>label {
            font-size: 17px !important;
            font-weight: 700 !important;
            margin-bottom: 10px !important;
        }
        
        /* Focus states more visible on mobile */
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus,
        .stNumberInput>div>div>input:focus {
            border-color: #1e3a5f !important;
            box-shadow: 0 0 0 4px rgba(30, 58, 95, 0.15) !important;
            transform: scale(1.01) !important;
        }
        
        /* Better error/success feedback */
        .stTextInput>div>div>input[aria-invalid="true"] {
            border-color: #ef5350 !important;
            background: rgba(255, 235, 238, 0.5) !important;
        }
        
        /* Hero sections - smaller on mobile */
        .hero-section, .header-section {
            padding: 20px 15px !important;
            margin-bottom: 20px !important;
            border-radius: 10px !important;
        }
        
        .hero-section h1, .header-section h1 {
            font-size: 24px !important;
        }
        
        .hero-section h2, .header-section h2 {
            font-size: 18px !important;
        }
        
        /* Content cards - stack better on mobile */
        .content-card, .feature-card, .stat-card {
            margin-bottom: 15px !important;
            padding: 15px !important;
            border-radius: 10px !important;
        }
        
        /* Trail/Hike cards - full width on mobile */
        .hike-card, .trail-card, .user-card {
            margin-bottom: 15px !important;
            padding: 15px !important;
            width: 100% !important;
        }
        
        /* Buttons - larger tap targets */
        button, .stButton button {
            min-height: 44px !important;
            font-size: 16px !important;
            padding: 12px 20px !important;
        }
        
        /* Input fields - easier to use on mobile */
        input, textarea, select {
            font-size: 16px !important;
            padding: 12px !important;
            min-height: 44px !important;
        }
        
        /* Metrics - smaller on mobile */
        .big-metric {
            font-size: 28px !important;
        }
        
        /* Columns - stack on mobile */
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 10px !important;
        }
        
        /* Sidebar - easier to open on mobile */
        [data-testid="stSidebar"] {
            width: 280px !important;
        }
        
        /* Tables - scroll horizontally on mobile */
        table {
            display: block !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
        }
        
        /* Text - readable size on mobile */
        p, div, span {
            font-size: 15px !important;
            line-height: 1.5 !important;
        }
        
        /* Headers - proportional on mobile */
        h1 { font-size: 24px !important; }
        h2 { font-size: 20px !important; }
        h3 { font-size: 18px !important; }
        h4 { font-size: 16px !important; }
        
        /* Images - responsive */
        img {
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* Expanders - easier to tap */
        [data-testid="stExpander"] summary {
            font-size: 16px !important;
            padding: 15px !important;
        }
        
        /* Tabs - better spacing */
        [data-baseweb="tab"] {
            padding: 12px 15px !important;
            font-size: 14px !important;
        }
        
        /* File uploader - mobile friendly */
        [data-testid="stFileUploader"] {
            font-size: 14px !important;
        }
        
        /* Date/time inputs */
        [data-baseweb="input"] {
            font-size: 16px !important;
        }
        
        /* Success/error/warning boxes */
        .element-container div[data-testid="stNotification"] {
            font-size: 14px !important;
            padding: 12px !important;
        }
    }
    
    /* Tablet: 768px to 1024px */
    @media only screen and (min-width: 768px) and (max-width: 1024px) {
        .hero-section, .header-section {
            padding: 30px !important;
        }
        
        .content-card, .feature-card {
            padding: 20px !important;
        }
        
        /* Two-column layout on tablet */
        [data-testid="column"] {
            width: 48% !important;
            display: inline-block !important;
            margin-right: 2% !important;
        }
    }
    
    /* Touch-friendly enhancements for all mobile devices */
    @media (hover: none) and (pointer: coarse) {
        /* Larger tap targets */
        button, a, [role="button"] {
            min-height: 44px !important;
            min-width: 44px !important;
        }
        
        /* Remove hover effects on touch devices */
        .hike-card:hover, .trail-card:hover, .user-card:hover {
            transform: none !important;
        }
        
        /* Better spacing for touch */
        button, input, select, textarea {
            margin: 8px 0 !important;
        }
    }
    
    /* Landscape mobile orientation */
    @media only screen and (max-height: 500px) and (orientation: landscape) {
        .hero-section, .header-section {
            padding: 15px !important;
            margin-bottom: 15px !important;
        }
        
        [data-testid="stSidebar"] {
            height: 100vh !important;
            overflow-y: auto !important;
        }
    }
    </style>
"""

def apply_nature_theme():
    """Apply the nature theme CSS to any Streamlit page"""
    import streamlit as st
    
    # Add mobile viewport meta tag
    st.markdown("""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    """, unsafe_allow_html=True)
    
    # Apply main CSS theme
    st.markdown(NATURE_CSS, unsafe_allow_html=True)
