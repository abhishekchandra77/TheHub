import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

st.set_page_config(page_title="Creator Gig Marketplace", page_icon="🎨", layout="wide")
st.title("🎨 Creator Gig Marketplace")
st.caption("Code2Career AI Hackathon 2026")

tabs = st.tabs(["🛒 Marketplace (Browse & Book)", "➕ Post a Gig", "📊 Creator Dashboard", "📋 My Bookings"])

# Feature 2: Browse & Search
with tabs[0]:
    st.header("Browse Available Gigs")
    c1, c2 = st.columns([1, 2])
    with c1:
        cat_filter = st.selectbox("Category", ["All", "Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI"])
    with c2:
        search_query = st.text_input("Search Gigs", placeholder="e.g. UGC Video, Thumbnail...")
        
    try:
        res = requests.get(f"{API_URL}/gigs", params={"category": cat_filter, "search": search_query})
        if res.status_code == 200:
            gigs = res.json()
            if not gigs:
                st.info("No gigs found matching criteria.")
            for gig in gigs:
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.subheader(gig['title'])
                        st.caption(f"By {gig['creator_name']} | Category: {gig['category']}")
                        st.write(gig['description'])
                    with col_b:
                        st.metric("Rate", f"${gig['rate']}")
                        # Feature 3: Book a Gig
                        with st.popover("Book Now"):
                            st.write(f"Book **{gig['title']}**")
                            c_name = st.text_input("Your Name", key=f"cn_{gig['id']}")
                            c_email = st.text_input("Your Email", key=f"ce_{gig['id']}")
                            reqs = st.text_area("Requirements", key=f"req_{gig['id']}")
                            if st.button("Confirm Booking", key=f"btn_{gig['id']}"):
                                b_res = requests.post(f"{API_URL}/bookings", json={
                                    "gig_id": gig['id'],
                                    "client_name": c_name,
                                    "client_email": c_email,
                                    "requirements": reqs
                                })
                                if b_res.status_code == 200:
                                    st.success("Booking request sent successfully!")
                                else:
                                    st.error("Failed to book gig.")
    except Exception as e:
        st.error(f"Cannot connect to API server: {str(e)}")

# Feature 1: Post a Gig
with tabs[1]:
    st.header("List Your Creator Skill")
    with st.form("post_gig_form"):
        creator = st.text_input("Creator Name")
        title = st.text_input("Gig Title")
        category = st.selectbox("Category", ["Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI"])
        rate = st.number_input("Rate ($)", min_value=1.0, value=50.0)
        desc = st.text_area("Gig Description")
        
        submitted = st.form_submit_button("Publish Gig")
        if submitted:
            if not creator or not title or not desc:
                st.error("Please fill all required fields.")
            else:
                p_res = requests.post(f"{API_URL}/gigs", json={
                    "creator_name": creator, "title": title, "category": category, "rate": rate, "description": desc
                })
                if p_res.status_code == 200:
                    st.success("Gig successfully published!")

# Feature 4: Creator Dashboard
with tabs[2]:
    st.header("Incoming Booking Requests")
    try:
        res = requests.get(f"{API_URL}/creator/bookings")
        if res.status_code == 200:
            bookings = res.json()
            for b in bookings:
                with st.container(border=True):
                    st.write(f"**Gig:** {b['gig_title']} | **Client:** {b['client_name']} ({b['client_email']})")
                    st.write(f"**Requirements:** {b['requirements']}")
                    st.caption(f"Current Status: **{b['status']}**")
                    
                    if b['status'] == "Pending":
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Accept", key=f"acc_{b['id']}"):
                                requests.patch(f"{API_URL}/bookings/{b['id']}", json={"status": "Accepted"})
                                st.rerun()
                        with col2:
                            reason = st.text_input("Rejection Reason (Optional)", key=f"reas_{b['id']}")
                            if st.button("Decline", key=f"dec_{b['id']}"):
                                requests.patch(f"{API_URL}/bookings/{b['id']}", json={"status": "Declined", "rejection_reason": reason})
                                st.rerun()
    except Exception as e:
        st.error(f"Error fetching dashboard data: {str(e)}")

# Feature 5: My Bookings (Client View)
with tabs[3]:
    st.header("Client Bookings Status")
    client_filter = st.text_input("Filter by Your Client Name", placeholder="Enter your name to view bookings")
    
    try:
        res = requests.get(f"{API_URL}/client/bookings", params={"client_name": client_filter if client_filter else None})
        if res.status_code == 200:
            my_bookings = res.json()
            for mb in my_bookings:
                with st.container(border=True):
                    st.subheader(mb['gig_title'])
                    st.write(f"**Creator:** {mb['creator_name']} | **Rate:** ${mb['rate']}")
                    
                    status = mb['status']
                    if status == "Accepted":
                        st.success(f"Status: {status} 🎉")
                    elif status == "Declined":
                        st.error(f"Status: {status} ❌")
                        if mb.get('rejection_reason'):
                            st.caption(f"Reason: {mb['rejection_reason']}")
                        st.info("💡 **DP1 Decision Point:** You can rebook another creator directly from the Marketplace tab.")
                    else:
                        st.warning(f"Status: {status} ⏳")
    except Exception as e:
        st.error(f"Error fetching bookings: {str(e)}")