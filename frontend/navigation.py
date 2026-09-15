"""Stable routes with a compact, role-aware navigation menu."""
import streamlit as st

GROUPS = {
    "Explore": [
        ("views/explore.py", "Trails", "", "landscape"),
        ("screens/1_🗺️_Map_View.py", "Map", "Map_View", "map"),
        ("screens/21_🎫_Register_for_Hikes.py", "Group hikes", "Register_for_Hikes", "groups"),
        ("screens/19_🎒_Hiking_Gear.py", "Equipment", "Hiking_Gear", "backpack"),
        ("screens/18_🌤️_Trail_Info.py", "Trail conditions", "Trail_Info", "cloud"),
        ("screens/3_📊_Analytics.py", "Trail statistics", "Analytics", "bar_chart"),
    ],
    "My Hikes": [
        ("views/my_hikes.py", "Upcoming and past hikes", "My_Hikes", "event"),
        ("screens/20_🗓️_Plan_Hike.py", "Plan a hike", "Plan_Hike", "event_note"),
        ("screens/5_📍_Track_Hike.py", "Hike log", "Track_Hike", "route"),
        ("screens/8_🔖_Bookmarks.py", "Saved trails", "Bookmarks", "bookmark"),
        ("screens/13_⌚_Wearables.py", "Import activities", "Wearables", "upload_file"),
        ("screens/15_🎯_Goals.py", "Goals", "Goals", "flag"),
        ("screens/10_🏆_Achievements.py", "Achievements", "Achievements", "emoji_events"),
    ],
    "Community": [
        ("screens/9_📰_Feed.py", "Activity feed", "Feed", "feed"),
        ("screens/12_💬_Messages.py", "Messages", "Messages", "chat"),
        ("screens/11_👥_Social.py", "Members", "Social", "group"),
        ("screens/7_⭐_Reviews.py", "Reviews", "Reviews", "reviews"),
        ("screens/17_💬_Trail_Community.py", "Trail discussions", "Trail_Community", "forum"),
    ],
    "Account": [
        ("screens/4_👤_Profile.py", "Profile", "Profile", "person"),
        ("screens/0_🔐_Login.py", "Sign in and security", "Login", "login"),
        ("screens/6_🔐_2FA_Setup.py", "Authenticator", "2FA_Setup", "security"),
        ("screens/16_🚨_Emergency_Contacts.py", "Emergency contacts", "Emergency_Contacts", "contact_emergency"),
        ("screens/19_🟠_Strava.py", "Strava connection", "Strava", "link"),
        ("screens/24_Account_and_Support.py", "Support and privacy", "Account_and_Support", "support_agent"),
        ("screens/25_Privacy_and_Terms.py", "Privacy and terms", "Privacy_and_Terms", "policy"),
    ],
    "Organizer": [
        ("views/operations.py", "Operations", "Operations", "monitor_heart"),
        ("screens/22_👑_Manage_Hikes.py", "Manage hikes", "Manage_Hikes", "event_available"),
        ("screens/14_👑_Admin_Dashboard.py", "Administration", "Admin_Dashboard", "admin_panel_settings"),
        ("screens/2_➕_Add_Trail.py", "Add trail", "Add_Trail", "add_location"),
        ("screens/23_Integrations.py", "Integrations", "Integrations", "settings"),
    ],
}


def page_groups(is_admin=False):
    pages = {group: [st.Page(path, title=title, icon=f":material/{icon}:",
                url_path=route or None, default=not route,
                visibility="hidden" if group == "Organizer" and not is_admin else "visible")
            for path, title, route, icon in entries] for group, entries in GROUPS.items()}
    # Hidden pages remain routable; each sensitive page must enforce authorization.
    pages["Explore"].append(st.Page("views/trail.py", title="Trail details", url_path="Trail_Details", visibility="hidden"))
    return pages
