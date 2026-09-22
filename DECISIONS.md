# Hackathon Decision Points (Track 2: Creator Gig Marketplace)

### DP1 · Rejection
**Choice:** The client sees the status updated to **Declined** along with an optional rejection reason provided by the creator, accompanied by a recommendation hint to browse alternative creators.
**Why:** Displaying the explicit status and optional feedback prevents user confusion. Prompting clients to explore alternative creators keeps them engaged on the marketplace platform rather than leaving after a rejection.

### DP2 · Double Booking
**Choice:** **Yes**, new booking requests remain open for a gig even while another request is in **Pending** status.
**Why:** Creators handle variable workloads and schedules. Automatically blocking incoming booking requests during a pending inquiry creates unnecessary bottlenecks if the creator ultimately declines or fails to respond promptly.

### DP3 · Discovery
**Choice:** **Hybrid Ranking Strategy** (Recency + Active Availability).
**Why:** Sorting solely by lowest price promotes low-quality listings, while sorting solely by newest penalizes reliable creators with established track records. Ranking by active recency gives new listings visibility while maintaining baseline quality for clients.