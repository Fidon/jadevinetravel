# apps/portal/tasks.py
# Full email implementations added in Phase 5B.
# These stubs prevent ImportError when views call async_task() during Phase 5A.

def notify_superadmin_new_listing(listing_type, listing_id):
    """Notify Super Admin that a new listing is pending review."""
    # TODO Phase 5B: send branded HTML email
    pass


def send_listing_approved_email(listing_type, listing_id):
    """Notify mini-admin their listing was approved."""
    # TODO Phase 5B: send branded HTML email
    pass


def send_listing_rejected_email(listing_type, listing_id):
    """Notify mini-admin their listing was rejected with reason."""
    # TODO Phase 5B: send branded HTML email
    pass