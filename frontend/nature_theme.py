"""Reusable nature theme CSS for all pages"""

NATURE_CSS = """
    <style>
    /* Main app background - soft nature gradient */
    .stApp {
        background: linear-gradient(180deg, 
            #e8f5e9 0%,
            #f1f8e9 25%, 
            #fff8e1 50%,
            #fce4ec 100%
        );
        background-attachment: fixed;
    }
    
    /* Sidebar nature theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            #1b5e20 0%, 
            #2e7d32 50%,
            #388e3c 100%
        ) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Hero/Header sections */
    .hero-section, .header-section {
        background: linear-gradient(135deg, 
            #1b5e20 0%, 
            #2e7d32 25%,
            #43a047 50%,
            #66bb6a 100%
        );
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 12px 30px rgba(27, 94, 32, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Content cards with nature theme */
    .content-card, .feature-card {
        background: linear-gradient(135deg, 
            #ffffff 0%, 
            #f1f8e9 50%,
            #e8f5e9 100%
        );
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #a5d6a7;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.15);
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .content-card:hover, .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(76, 175, 80, 0.25);
        border-color: #66bb6a;
    }
    
    /* Stats boxes */
    .stat-box, .metric-box {
        background: linear-gradient(135deg, 
            #2e7d32 0%, 
            #43a047 50%,
            #66bb6a 100%
        );
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-number, .metric-number {
        font-size: 36px;
        font-weight: bold;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Buttons with nature theme */
    .stButton>button {
        background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
    }
    
    /* Input fields with nature border */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        border: 2px solid #a5d6a7 !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus {
        border-color: #66bb6a !important;
        box-shadow: 0 0 8px rgba(102, 187, 106, 0.3) !important;
    }
    
    /* Expander with nature theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%) !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 8px !important;
    }
    
    /* Tabs with nature colors */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #2e7d32 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%) !important;
        color: white !important;
    }
    
    /* Difficulty badges */
    .difficulty-easy { 
        color: #66bb6a; 
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
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%) !important;
        border-left: 5px solid #66bb6a !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%) !important;
        border-left: 5px solid #ef5350 !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%) !important;
        border-left: 5px solid #ffa726 !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%) !important;
        border-left: 5px solid #42a5f5 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border: 2px solid #a5d6a7 !important;
        border-radius: 8px !important;
    }
    
    /* Card hover effects */
    .hike-card, .trail-card, .user-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 5px solid #43a047;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
        transition: all 0.3s ease;
    }
    
    .hike-card:hover, .trail-card:hover, .user-card:hover {
        box-shadow: 0 8px 20px rgba(76, 175, 80, 0.25);
        transform: translateY(-2px);
    }
    
    /* Metric styling */
    .big-metric {
        font-size: 42px;
        font-weight: bold;
        color: #2e7d32;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1b5e20 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* ===== MOBILE RESPONSIVENESS ===== */
    
    /* Mobile: screens smaller than 768px */
    @media only screen and (max-width: 768px) {
        /* Reduce padding on mobile */
        .stApp {
            padding: 10px !important;
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
    st.markdown(NATURE_CSS, unsafe_allow_html=True)
