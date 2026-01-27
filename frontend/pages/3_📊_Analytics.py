import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from services import get_all_hikes
from nature_theme import apply_nature_theme

init_database()

# Page configuration
st.set_page_config(
    page_title="Analytics - Kilele",
    page_icon="📊",
    layout="wide"
)
apply_nature_theme()

@st.cache_data(ttl=300)
def fetch_hikes():
    """Fetch all hikes from database"""
    try:
        return get_all_hikes()
    except Exception as e:
        st.error(f"Error fetching hikes: {str(e)}")
        return []

def main():
    st.title("📊 Trail Analytics & Statistics")
    st.markdown("*Comprehensive analysis of Kilele hiking trails*")
    
    # Fetch data
    hikes = fetch_hikes()
    
    if not hikes:
        st.warning("No data available for analysis")
        return
    
    df = pd.DataFrame(hikes)
    
    # Overview metrics
    st.markdown("---")
    st.markdown("### 🎯 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🏔️ Total Trails", len(df))
    with col2:
        st.metric("📏 Total Distance", f"{df['distance_km'].sum():.1f} km")
    with col3:
        st.metric("⏱️ Total Time", f"{df['estimated_duration_hours'].sum():.1f} hrs")
    with col4:
        avg_elev = df['elevation_gain_m'].mean()
        st.metric("⛰️ Avg Elevation", f"{avg_elev:.0f} m" if not pd.isna(avg_elev) else "N/A")
    with col5:
        st.metric("🗺️ Trail Types", df['trail_type'].nunique())
    
    # Difficulty Distribution
    st.markdown("---")
    st.markdown("### 🎯 Difficulty Analysis")
    col_diff1, col_diff2 = st.columns(2)
    
    with col_diff1:
        # Pie chart
        difficulty_counts = df['difficulty'].value_counts().reset_index()
        difficulty_counts.columns = ['Difficulty', 'Count']
        
        fig_pie = px.pie(
            difficulty_counts,
            values='Count',
            names='Difficulty',
            title='Trail Distribution by Difficulty',
            color='Difficulty',
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            },
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_diff2:
        # Bar chart with metrics
        difficulty_stats = df.groupby('difficulty').agg({
            'distance_km': 'mean',
            'estimated_duration_hours': 'mean',
            'elevation_gain_m': 'mean'
        }).reset_index()
        
        fig_bar = px.bar(
            difficulty_stats,
            x='difficulty',
            y='distance_km',
            title='Average Distance by Difficulty',
            labels={'distance_km': 'Avg Distance (km)', 'difficulty': 'Difficulty'},
            color='difficulty',
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            }
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Distance and Duration Analysis
    st.markdown("---")
    st.markdown("### 📏 Distance & Duration Analysis")
    
    col_dist1, col_dist2 = st.columns(2)
    
    with col_dist1:
        # Scatter plot
        fig_scatter = px.scatter(
            df,
            x='distance_km',
            y='estimated_duration_hours',
            size='elevation_gain_m',
            color='difficulty',
            hover_data=['name', 'location'],
            title='Distance vs Duration (bubble size = elevation)',
            labels={
                'distance_km': 'Distance (km)',
                'estimated_duration_hours': 'Duration (hours)'
            },
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col_dist2:
        # Box plot
        fig_box = px.box(
            df,
            x='difficulty',
            y='distance_km',
            color='difficulty',
            title='Distance Distribution by Difficulty',
            labels={'distance_km': 'Distance (km)', 'difficulty': 'Difficulty'},
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            }
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Trail Types
    st.markdown("---")
    st.markdown("### 🗺️ Trail Types Analysis")
    
    col_type1, col_type2 = st.columns(2)
    
    with col_type1:
        trail_type_counts = df['trail_type'].value_counts().reset_index()
        trail_type_counts.columns = ['Trail Type', 'Count']
        
        fig_trail_type = px.bar(
            trail_type_counts,
            x='Trail Type',
            y='Count',
            title='Trails by Type',
            color='Trail Type',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_trail_type, use_container_width=True)
    
    with col_type2:
        # Sunburst chart
        df_sunburst = df[['trail_type', 'difficulty', 'name']].copy()
        fig_sunburst = px.sunburst(
            df_sunburst,
            path=['trail_type', 'difficulty'],
            title='Trail Hierarchy (Type → Difficulty)',
            color='difficulty',
            color_discrete_map={
                'Easy': '#4caf50',
                'Moderate': '#ff9800',
                'Hard': '#f44336',
                'Extreme': '#9c27b0'
            }
        )
        st.plotly_chart(fig_sunburst, use_container_width=True)
    
    # Elevation Analysis
    st.markdown("---")
    st.markdown("### ⛰️ Elevation Analysis")
    
    df_with_elev = df[df['elevation_gain_m'].notna()].copy()
    
    if not df_with_elev.empty:
        col_elev1, col_elev2 = st.columns(2)
        
        with col_elev1:
            fig_elev_hist = px.histogram(
                df_with_elev,
                x='elevation_gain_m',
                title='Elevation Gain Distribution',
                labels={'elevation_gain_m': 'Elevation Gain (m)'},
                color_discrete_sequence=['#2e7d32']
            )
            st.plotly_chart(fig_elev_hist, use_container_width=True)
        
        with col_elev2:
            # Top trails by elevation
            top_elevation = df_with_elev.nlargest(10, 'elevation_gain_m')[['name', 'elevation_gain_m', 'difficulty']]
            
            fig_top_elev = px.bar(
                top_elevation,
                x='elevation_gain_m',
                y='name',
                orientation='h',
                title='Top 10 Trails by Elevation Gain',
                labels={'elevation_gain_m': 'Elevation Gain (m)', 'name': 'Trail'},
                color='difficulty',
                color_discrete_map={
                    'Easy': '#4caf50',
                    'Moderate': '#ff9800',
                    'Hard': '#f44336',
                    'Extreme': '#9c27b0'
                }
            )
            st.plotly_chart(fig_top_elev, use_container_width=True)
    else:
        st.info("No elevation data available")
    
    # Data Table
    st.markdown("---")
    st.markdown("### 📋 Detailed Trail Data")
    
    # Select columns to display
    display_cols = st.multiselect(
        "Select columns to display",
        df.columns.tolist(),
        default=['name', 'location', 'difficulty', 'distance_km', 'estimated_duration_hours', 'elevation_gain_m']
    )
    
    if display_cols:
        st.dataframe(
            df[display_cols].sort_values('distance_km', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Download full data
    st.markdown("---")
    col_download1, col_download2, col_download3 = st.columns(3)
    
    with col_download1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Data (CSV)",
            data=csv_data,
            file_name="kilele_trails_complete.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_download2:
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download Full Data (JSON)",
            data=json_data,
            file_name="kilele_trails_complete.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Summary statistics
    st.markdown("---")
    st.markdown("### 📈 Summary Statistics")
    
    st.dataframe(
        df[['distance_km', 'estimated_duration_hours', 'elevation_gain_m']].describe(),
        use_container_width=True
    )

if __name__ == "__main__":
    main()
