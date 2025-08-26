// Included the PURPOSE to help in case the endpoint
// requested already exists

// "purpose": "endpoint"
const endpoints = {
    // "get_all_orders"            : "buyer/:id/orders",                       // GET
    // "get_one_order"             : "buyer/:id/order/:id",                    // GET
    // "get_all_wishlist_items"    : "buyer/:id/wishlist",                     // GET
    // "get_one_wishlist_item"     : "buyer/:id/wishlist/:id",                 // GET
    "request_for_quote"         : "buyer/:id/rfq",                          // POST {buyer,title,supplier,item,quantity,description}
    "get_all_bids"              : "buyer/:id/bids",                         // GET
    "get_one_bid"               : "buyer/:id/bid/:id",                      // GET
    "get_all_notifications"     : "buyer/:id/notifications",                // GET
    "get_specific_notifications": "buyer/:id/notifications/:category",      // GET <all,contracts,others>
    "get_specific_notification" : "buyer/:id/notification/:id",             // GET
    "schedule_calendar_event"   : "buyer/:id/calendar/create",              // POST {buyer,title}
    "retrieve_calendar_events"  : "buyer/:id/calendar/events",              // GET
}





