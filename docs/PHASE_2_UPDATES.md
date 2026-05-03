\## Summary of Feature Additions Since Phase 0-2 Handoff



\### 1. Per-Listing Refund \& Payment Policy

A per-listing policy system was added across all three bookable services, giving each service provider granular control over refund eligibility and accepted payment modes independently of the global cancellation policy table.



For hotels, the policy is set at the room type level rather than the hotel level. This reflects real-world practice where a hotel may offer both a flexible rate and a non-refundable rate for the same room category. Two boolean fields were added to `HotelRoomType`: `is\_refundable` (default `True`) and `allows\_pay\_on\_arrival` (default `True`). When `is\_refundable=False`, the global `CancellationPolicy` tiers are bypassed entirely for that room — no refund is issued regardless of how far in advance the customer cancels. When `allows\_pay\_on\_arrival=False`, the Pay on Arrival option is suppressed both in the UI and enforced server-side in `BookingSummaryView.\_create\_booking()`, meaning a customer cannot select it even by manipulating the form. For car rentals, the same two fields were added directly to `CarRental`, applying to the entire vehicle. For tour packages, the same fields were added to `TourPackage`, applying to the entire package.



A critical architectural decision was made around snapshotting: when a booking is created, the `is\_refundable` value from the listing at that moment is written into a new `is\_refundable` field on the `Booking` model itself. This mirrors the existing price snapshotting pattern — the refund policy that applied at booking time is permanently recorded on the booking record and never retroactively affected by future changes to the listing. This ensures that if an admin later changes a room from refundable to non-refundable, existing bookings are unaffected.



The policy flags propagate through the entire booking flow. On the detail page, a non-refundable room shows a red warning notice in the booking panel when selected, and the Pay on Arrival footer note is hidden when the selected room disallows it. These notices are toggled by JavaScript on room selection for hotels, and rendered server-side for cars and tours. On the booking summary page, the Pay on Arrival radio option is conditionally rendered only when `data.allows\_pay\_on\_arrival` is `True` in the session — if it is `False`, a notice replaces it informing the customer that online payment is required. The trust sidebar's "Free Cancellation" item is replaced with a "Non-refundable" warning when the booking is non-refundable. On the booking confirmation page, a non-refundable badge appears in the booking summary row.



\### 2. Ratings \& Reviews

A dedicated `apps/reviews/` Django app was created to handle customer reviews. The `Review` model links a user, a booking, and a service (hotel, tour, or car) through nullable ForeignKeys, with `service\_type` as a discriminator. A `OneToOneField` on `booking` enforces exactly one review per booking at the database level, making duplicate reviews structurally impossible. Reviews have a `rating` field accepting integers from 1 to 10 validated by Django's `MinValueValidator` and `MaxValueValidator`.



Reviews require moderation before appearing publicly. The `status` field has three states: `pending`, `approved`, and `rejected`. Super Admins can approve or reject any review across all listings. Mini-admins can approve or reject reviews for their own hotel and car listings only. This moderation gate prevents fake or abusive reviews from reaching the public site.



The cold-start display problem — where showing "0 reviews" or "No rating yet" on every new listing looks worse than showing nothing — was solved with a threshold rule: ratings are only displayed when a listing has at least 3 approved reviews. Below that threshold, no rating badge appears anywhere. The average rating is computed as a queryset annotation using Django's `Avg` and `Count` aggregates directly in the list and detail views, avoiding any denormalized field on the listing model that would need to be kept in sync.



Rating badges appear in two places: on the listing cards in the list views (hotels, cars, tours), injected by JavaScript as part of the AJAX card rendering, and on the detail page header, rendered server-side by Django. The badge shows the average score out of 10 and the review count in parentheses. The review submission UI lives in the user dashboard on the booking detail page — a customer can only submit a review for a booking that has `status=completed`, ensuring only customers who actually received the service can review it. This is built in Phase 4 and sits on the booking detail template.



\### 3. Discounts

A discount system was added to all three listing types, supporting both permanent discounts and time-limited promotional pricing. The discount is configured with two fields: `discount\_percent` (a positive integer from 0 to 99) and `discount\_expires\_at` (a nullable `DateTimeField`). When `discount\_expires\_at` is `None`, the discount is permanent until manually removed. When a datetime is set, the discount automatically becomes inactive once that datetime passes — no scheduled task or manual intervention required, since the check happens at query time via `timezone.now()` comparison in the model method.



For hotels, the discount is placed at the `HotelRoomType` level rather than the `Hotel` level, giving room-level granularity. A hotel can have one room type at full price and another at a promotional rate simultaneously. For car rentals, the discount is on the `CarRental` model, applying to the whole vehicle. For tour packages, the discount is on `TourPackage`, applying to the package price per person.



Three methods were added to each model: `get\_discounted\_price()` returns the calculated discounted price if an active discount exists, otherwise `None`; `get\_display\_price()` returns the discounted price if active, otherwise the base price — this is the single method used everywhere a price is shown or snapshotted; and the `has\_active\_discount` property returns a boolean for use in templates and serializers.



The discount integrates with the price snapshotting pattern at the point of session storage. When a user submits the booking form, `get\_display\_price()` is called and the result is stored in the session — meaning the discounted price is what gets snapshotted into the `Booking` record when the customer confirms, not the original price. This is correct: the customer pays what was shown to them, and the booking record reflects that permanently.



Discount display is consistent across all surfaces. On list cards, a red pill badge showing the percentage (e.g. "12% OFF") appears in the top-right corner of the card image. The original price is shown with a CSS strikethrough using the `jd-price-original` class, and the discounted price is shown beside it in the primary price position. On detail pages, the discount badge appears in the price panel header alongside the struck-through original and the discounted price. On room type cards in the hotel detail, each room shows its own discount badge and price treatment independently, so a user can clearly see which rooms are discounted and by how much. On the booking summary page, the price breakdown reflects the already-discounted price per unit, since it was snapshotted at form submission time.

