import streamlit as st
from nature_theme import apply_nature_theme

st.set_page_config(page_title="Privacy and terms - Kilele", page_icon=":material/policy:", layout="wide")
apply_nature_theme()
st.title("Privacy and terms")
st.caption("Kilele Explorers | Updated 8 September 2026")
st.markdown("[Contact: kileleexplorers@gmail.com](mailto:kileleexplorers@gmail.com)")
privacy, terms = st.tabs(["Privacy", "Community and bookings"])
with privacy:
    st.markdown("""
### Information we store
Account details, password hashes, authentication sessions, posts, messages,
bookings and the hike records or contacts you choose to provide. Profile pictures and
activity imports are optional. Emergency contacts are private to your account.

### Visibility and service providers
Your username, profile, reviews and community posts can be visible to other members.
Messages are available to conversation participants. Organizers can manage bookings and
investigate reports. Hosting and database providers process data to operate this service;
connected email or activity providers receive the information needed for those features.
Map providers receive network requests when maps load. Do not post sensitive information
in public content. Kilele does not sell your personal data.

### Your controls
Account and support provides a data export, account deletion, blocking and privacy requests.
Deletion removes your profile and private hike/contact records, anonymizes your posts, and
revokes local access. Limited booking/payment references remain for reconciliation.
Copies in backups may remain until their retention period expires. Contact the organizers
for questions about retained records or external-provider permissions.

### Browser storage
A random login token may be stored on your device when you sign in. Signing out revokes
that token. Avoid persistent sign-in on shared devices. Uploaded routes can contain precise
location history; only upload information you intend to store.
""")
with terms:
    st.markdown("""
### Community
Use an account you control. Do not harass others, spam, impersonate people or upload
content you have no right to share. Report concerns through Account and support.
Organizers may remove content or suspend accounts for abuse.

### Hikes and safety
Trail information and community reports may be incomplete or out of date. Confirm access,
weather, equipment and arrangements with the organizer before travelling. Hike logs are
manual records, not continuous GPS tracking. Saved contacts do not receive automatic
alerts. Kilele is not an emergency dispatch or rescue service.

### Bookings and cancellation
A confirmed registration reserves a place subject to the organizer's published details.
Free upcoming registrations can be cancelled from My registrations. Paid checkout remains
unavailable unless the payment provider is configured. Do not pay through unofficial links.
For a payment dispute, cancellation or refund request, contact kileleexplorers@gmail.com
with your booking reference, never your M-Pesa PIN. A refund request is not confirmation
that money has been returned. Confirm costs, transport and cancellation conditions before paying.

### Availability
This community service uses limited free hosting. Temporary delays and outages are possible.
Keep an independent copy of essential route and contact information before a hike.
""")
