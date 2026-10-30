# Review Report: Bend Bike Shop Software Technical Design Document

**Scope:** Logical, structural, and other issues. Because the document is known to be partial, missing sections are noted only where their absence causes a concrete inconsistency elsewhere.

---

## 1. Critical Logical Issues

### 1.1 Invariant 3 is mathematically malformed
> "the final transaction amount charged ... must equal the sum of the booked rate unless the late fee applies"

- "Sum of the booked rate" is undefined (sum over bikes? hours? both?).
- It ignores `overrideRate` (Interface 6), which changes the rate after booking.
- It ignores damage charges. `returnBikes` accepts `damages` and says "damage is flagged", but nothing says whether damage fees are billed. The invariant would be violated by any damage fee.
- It also ignores pricing changes from the "dynamic price adjustments" goal.

### 1.2 Pre-authorization amount vs. final charge conflict
- `authPayment` guarantees authorization "for the expected amount not including possible late return fees".
- `returnBikes` then charges the final amount, which can include late fees.
- There is no defined behavior when the final charge exceeds the authorization (late fees, rate overrides upward, damages, early or extended rentals). Card authorizations also expire, which matters for long advance reservations. Neither expiry nor re-authorization is addressed.

### 1.3 Reservation state machine is undefined and inconsistent
States mentioned across the document: `pending`, `confirmed`, `active`, `completed`. Problems:
- There is no `cancelled`, `expired`, `no-show`, or `failed` state, even though cancellation is a constraint and `cancelReservation()` exists in the class diagram.
- Nothing defines what happens to a `pending` reservation whose payment never completes. Interface 1 locks inventory without payment, so abandoned pending reservations can hold bikes indefinitely. This is a resource-exhaustion and denial-of-inventory risk, and a timeout or TTL is needed.
- Overdue reservations (the "Rental Forgotten" failure mode) have no state; they would remain `active`.
- Status is a free `string` in the ER diagram and `ReservationStatus` in the class diagram, with no enumerated values.

### 1.4 Cancellation rule is ambiguous and unimplemented
- The constraint says "reservations can be canceled 24 hours before the rental time". This is ambiguous: *at least* 24 hours before, or *only within* the 24 hours before?
- The only mention of `cancelReservation()` is in the class diagram. There is no interface spec, no handling of releasing the card authorization, and no handling of inventory release.
- Kiosk "reserve now" bookings can never satisfy a 24-hour rule. The behavior for them is undefined.
- The non-goal "automated cancellation compensation" conflicts with a manual path that is not described anywhere.

### 1.5 Interface 5 contradicts its own purpose
- The purpose says it lets staff mark a bike "damaged **or repaired**", but the outcome only describes removal from inventory when the condition is `NEEDS_REPAIR` or `OUT_OF_SERVICE`. Re-adding a repaired bike to inventory is never specified.
- "Its removed from the inventory" conflicts with the goal of tracking status (`service`, `ready`, `checked out`) and with `removeBikeFromService`. Removal from *availability* is different from removal from *inventory*.
- The conditions in the goals (`service`, `ready`, `checked out`) do not match those in Invariant 4 / Interface 5 (`NEEDS_REPAIR`, `OUT_OF_SERVICE`). "Checked out" is a rental state, not a condition, so conflating them in one field is a modeling error.
- **Invariant 4 conflicts with the notes:** the note says a bike marked out of service while tied to a future reservation triggers a manager alert. The invariant says such a bike can't be assigned to a `PENDING` or `CONFIRMED` reservation. At the moment of the update, the invariant is already violated by design. The invariant must be reworded (e.g. "cannot be newly assigned") or the update must be rejected or blocked until the conflict is resolved.
- The same conflict applies to `ACTIVE` reservations. A bike broken during a rental (or flagged at return) isn't covered at all.

### 1.6 Invariant 1 vs. return/overdue behavior
- "One bike can't have more than one confirmed or active reservation at a single point in time" is checked against reserved windows, but an overdue active rental physically occupies a bike past `end_time`. A subsequent confirmed reservation starting at that time can't be fulfilled. The system doesn't address this. Because automatic reassignment is a non-goal, the manager workflow for this case should at least be defined.
- There is no buffer or turnaround time between rentals for inspection and cleaning. Back-to-back reservations that satisfy Invariant 1 can still fail in practice.

### 1.7 Late-fee rule is inconsistent
- Constraints: "late fee applied after 30 mins past the return time" (typo "feed"). Interface 4: "if returnTime is more than 30 mins past end time the late fee is applied".
- Is the fee for the *whole* overdue period, or only time beyond the 30-minute grace? Is it flat or hourly? Not defined.
- `returnTime` is passed in as a parameter. This allows an employee to enter an arbitrary time and affects fee integrity. It should be system-generated or audited.
- Interface 3 says the real pickup timestamp "is recorded for late fee timing", but late fees are computed from the return time vs. `end_time`, not the pickup time. The pickup timestamp has no consumer, and the data model has no field to store it (see 2.2).
- If a customer picks up late, is the rental still due at the original `end_time`? Unspecified.

---

## 2. Data Model Issues

### 2.1 ER diagram cardinalities are wrong or contradictory
- `RESERVATION ||--|{ BIKE : includes` means one reservation includes one-or-more bikes, and, by the notation, **each bike belongs to exactly one reservation**. That cannot be right for a bike rented many times over its lifetime. This is a many-to-many relationship (`RESERVATION }|--|{ BIKE`) that needs a join table (e.g. `RESERVATION_BIKE`), which also gives a place to store the per-reservation rate and per-bike damage.
- `RESERVATION ||--|| TRANSACTION` means exactly one transaction per reservation. This conflicts with:
  - pre-authorization and later charge (arguably two payment events),
  - retries (3 attempts in Failure Modes),
  - refunds, damage charges, and late fees as separate charges,
  - reservations that are cancelled before any transaction exists (a `||--||` relationship requires one always).
  
  It should likely be `||--o{` (zero or many).
- There is no `EMPLOYEE`/`STAFF` entity, though the Database component stores "staff accounts" and Interfaces 3, 5 and 6 reference `employeeId` and `managerId`. Roles (customer / employee / manager / owner) are also not modeled.
- The `CUSTOMER` entity has no auth credentials, although customers are an access tier. Kiosk walk-ins may not have accounts; `createReservation` requires a `customerId` "assigned", with no guest flow.

### 2.2 Missing attributes needed by the specified behavior
- `RESERVATION`: no actual pickup time, actual return time, total estimated cost, applied rate/override, cancellation info, or confirmation code (required by the booking-confirmation NFR).
- `BIKE`: `condition_status` as a string with undefined values; no inventory-status field matching the "service/ready/checked out" goal.
- `TRANSACTION`: no amount authorized (only `final_amount`), no auth status/timestamp, no late-fee/damage breakdown, no type (auth vs. capture vs. refund).
- No audit/history tables, although "history and summary reports" and "reservation/maintenance history" are stated goals and the Database component claims to store them.
- No `rate override` log, although Interface 6 says the reason is logged.
- No pricing/rate-rule entity to support "dynamic price adjustments".

### 2.3 ER diagram vs. class diagram mismatches
| Item | ER Diagram | Class Diagram |
|---|---|---|
| Customer name | `first_name`, `last_name` | single `name` |
| Customer contact | `phone_number`, `email` | `phone` only (no email, though confirmations are a goal) |
| Bike price field | `hourly_rate` | `baseRate` |
| Bike condition | `condition_status` (string) | `condition` (`BikeCondition`) |
| Bike attributes | `size` | missing |
| Transaction | `TRANSACTION` entity | no class |
| Staff | none | none |

### 2.4 Pricing
- Rates are defined per bike (`hourly_rate`), but `overrideRate` takes a single `newRate: Float` per *reservation*. How does a single rate apply to a multi-bike reservation with different bike rates?
- Floating-point (`float`) for money is a correctness risk. Use fixed-point/decimal or integer minor units.
- Time zone handling for `datetime` is unspecified. This matters for 24-hour and 30-minute rules and for DST transitions.

---

## 3. Class Diagram Issues

- **Missing classes** for entities elsewhere in the document: `Transaction`/`Payment`, `Employee`/`Manager`/`Owner` (or a `User`/`Staff` role hierarchy), and any pricing/late-fee component.
- `InventoryManager` is the only place with availability search, but `Bike.isAvailable(start, end)` duplicates it. Bikes shouldn't need to know about reservations; the availability logic location is unclear.
- `Reservation` has no association with a payment or transaction class, and `completeRental()` / `markAsActive()` overlap with the interface operations `returnBikes` / `pickupBikes` without clear mapping.
- `Reservation "1" --> "1..*" Bike` has the same many-to-many error as the ER diagram. Reverse multiplicity is missing (a bike has `0..*` reservations over time).
- `createReservation()` and `cancelReservation()` are modeled on `Customer`, but Interface 1 is parameterized with `customerId` as an external function, suggesting a service-layer operation rather than a customer behavior. Interface 1 also doesn't use `InventoryManager`, which would perform the locking.
- `removeBikeFromService` exists but no counterpart (e.g. `returnBikeToService`) exists, mirroring the repair gap in 1.5.
- Class diagram has `Customer` as the only actor. Staff, the kiosk, and the payment gateway aren't modeled (acceptable if intentionally scoped, but it should be stated).

---

## 4. Interface Specification Issues

### General
- Interfaces lack **error/exception behavior** (invalid input, not-found, unauthorized). Only `Bool` returns are used for failure, which loses the reason (e.g. declined card vs. gateway timeout), which is needed to drive the failure-mode behaviors.
- Parameter and type names are inconsistent: `paymentDetails`, `bikeCondition` vs. `BikeCondition`, `List < String >`, and `endTime` has no type in `createReservation`. `returnTime`, `condition`, etc. use inconsistent casing conventions.
- Several "requires" clauses are only partially specified; none specify **authorization** consistently (see below).
- `notes:` in Interface 4 is empty. This is a clear unfinished item.
- There is no **cancellation** interface, **search/availability** interface, **kiosk session** interface, **report** interface, or **confirmation code** generation, despite these being goals or NFRs.

### Interface 1: `createReservation`
- "Requires: startTime has to be in the future" prevents kiosk "reserve now" rentals where the start is *now* (the Actors section says the kiosk reserves "now").
- The `customerId` precondition says "must be assigned" with no definition of what that means (exists? authenticated?).
- No mechanism is specified for the "lock" duration or release. See 1.3.
- The concurrency guarantee ("bikes won't be double booked") is stated as a guarantee, but no mechanism is described apart from a reference in the Failure Modes table. Atomicity of multi-bike reservations (all-or-nothing) is not stated.
- No upper bound on the reservation duration or number of bikes.

### Interface 2: `authPayment`
- "iff successful" is the only outcome described. The failure outcome is missing: what is the reservation state after a failed auth, and does the lock release? What about the three retries?
- Pre-auth amount is "expected amount", but the calculation (`calculateEstimatedCost`) is not tied to this interface.
- No handling for idempotency (duplicate calls produce duplicate authorizations).
- Kiosk fallback (manual card entry) in Failure Modes implies card-not-present entry on kiosk hardware. This has PCI-compliance implications that aren't mentioned (see 6).
- The invariant requires a valid `paymentToken` before pickup, but the interface never says it stores the token.

### Interface 3: `pickupBikes`
- Requires `confirmed` but doesn't check that the **current time is within the rental window**. Early or very late pickup is undefined, as is a no-show.
- "Only employees can successfully call this function" is only a note, not a precondition. The requires clause only says the `employeeId` "must be associated to a staff member". Whether managers and owners may call it is unspecified.
- Returns `Bool` with no failure details.
- Identity verification of the customer at handoff (e.g. confirmation code or ID) is not specified.
- Inspecting bike condition at pickup isn't covered, while return inspection is. This leaves no baseline for damage disputes.

### Interface 4: `returnBikes`
- Precondition checks reservation status but not employee identity. Returns are an employee action per the Actors section, yet no `employeeId` parameter exists, so there is no accountability and no authorization check.
- Return of a **subset** of bikes in a multi-bike reservation is not supported.
- Outcome says "final amount charged" but doesn't say what happens if the capture fails (declined, expired authorization). The reservation would be `completed` with no payment. The ordering (charge then complete, or the reverse) and atomicity are not defined.
- Damage handling: `damages` is a `List<String>`, and "damage is flagged", but there is no link to `updateBikeCondition`, no damage fee, and no owner of the flow that moves the bike out of availability.
- Early returns: is the customer charged the booked amount or the actual time used? Unspecified.
- Return type `float` is used for money (see 2.4) and doesn't distinguish a failed charge from a zero charge.

### Interface 5: `updateBikeCondition`
- No authorization check (who may call it?). The purpose says "staff", but the Staff Interface says managers handle stock admin access and employees handle returns/handoffs.
- The note says a manager is alerted but no mechanism (notification channel, record) is specified.
- See 1.5 for additional contradictions.

### Interface 6: `overrideRate`
- `requires` allows "active or pending", yet `confirmed` reservations (the state between `pending` and `active`) are excluded. A manager can't adjust a confirmed reservation, which is an apparent omission or a bug.
- It doesn't say what happens if the new rate exceeds the authorized amount (see 1.2) or if the reservation is a multi-bike one (see 2.4).
- Interface "notes" says "standard employees can't use this function", but the "requires" also lets the **owner** use it. This should be consistent with the access-tier statements.
- Rate override audit: "reason is logged", but no log entity or retention is defined.
- No upper/lower bounds on `newRate` (negative or zero rate possible).

---

## 5. Requirements, Goals & Scope Issues

### 5.1 Goals not supported anywhere in the design
| Goal | Gap |
|---|---|
| Easy online booking with confirmations | Confirmation code mentioned in NFR only; no generation or delivery (email/SMS) interface; `Customer` class lacks email |
| Tier-based system access | Only noted ad hoc in interface preconditions; no role model, authentication, or authorization design |
| Inventory status management (service, ready, checked out) | No mapping to `BikeCondition`; "checked out" has no representation |
| Dynamic price adjustments | No rate-rule model; only manual `overrideRate` exists. "Dynamic" suggests automated rules (demand, season) that aren't designed |
| History and summary reports | No report interface, no owner-facing query design, no history tables |

### 5.2 Non-goal vs. design tension
- **"Automatic stock reassignment when bikes are inoperable" is a non-goal**, but the actors section says the manager "helps with overbooking due to damaged returns". The manager's tools for this (finding substitute bikes, rebooking, notifying the customer) are not defined. The alert alone is not a resolution path.
- **"Unattended bike handoffs"** is a non-goal, and is consistent with the constraint, but the kiosk text ("reserve different bikes now") doesn't say how the customer proceeds to an employee handoff.

### 5.3 Non-functional requirements are thin or misclassified
- The "Non-Functional Requirements" table lists **functional** behaviors (confirmation display, card reader) rather than measurable qualities. The table header "Function" is misnamed.
- No NFRs for performance (booking latency), security, privacy, data retention, scalability, accessibility, or recovery. "99.9 percent uptime" is listed under Assumptions rather than as a requirement, and there are no offline/degraded-mode expectations for the kiosk or staff dashboard.
- The kiosk idle timeout is vague: what's reset (the session, the cart, a pending lock)? What about card data entered but not submitted, and bikes held for the in-progress session?

### 5.4 Constraints/assumptions
- "Third party payment authorizations" is a fragment, with no stated gateway, auth hold duration, or fee expectations.
- "Web based" is too vague to serve as an assumption. It should say what the kiosk and staff dashboards run on (a browser in kiosk mode?).
- The assumption of 99.9% uptime for "the online system" conflicts with nothing directly, but the dependence on the third-party gateway availability (which could be lower) isn't reflected.
- Constraint "credit cards pre-authorized when booking but no charges until the bikes are returned" conflicts with common needs for deposits or no-show fees, and with the late-fee and damage-fee paths that need charge authority beyond the pre-auth. (See 1.2.)

---

## 6. Security, Privacy & Compliance (Cross-cutting Gaps)

- **PCI-DSS**: Manual card entry at kiosks and "employees can process payment in store" imply handling card data. Nothing says card numbers must never reach the Application Server or database (tokenization via the gateway is only implied by `payment_token`).
- **Authentication/authorization**: Tiered access is a goal, yet no authentication for customers, staff, or kiosks is described. There are no session or credential details, and the manager/owner/employee permission matrix exists only implicitly across the Staff Interface component and scattered preconditions.
- **PII handling**: Customer name, phone, and email are stored with no retention, privacy, or deletion policy.
- **Audit logging**: Rate overrides, condition changes, and returns are sensitive operations needing an audit trail with actor and timestamp.
- **Abuse cases**: No rate limiting on booking (inventory-hoarding via pending reservations; see 1.3), no fraud considerations for kiosk walk-ups.

---

## 7. Diagrams & Component Section

### Component diagram
- The Staff Dashboard serves three distinct roles (employee, manager, owner) as a single component. It's fine as a simplification, but the role-based access enforcement location (UI vs. app server) isn't stated.
- No notification component exists (email/SMS confirmations, manager alerts), although several behaviors depend on notification: booking confirmation, manager alerts for conflicts, and overdue-return alerts.
- No scheduler/background job component, although the "Rental Forgotten" resolution ("system checks for overdue returns") and pending-reservation expiry both require one.
- Customers' and staff's access to the **Payment Gateway** for "employees can process payment in store" isn't shown. Do staff use the kiosk reader or a separate terminal?
- Component table lists "Kiosk Interface" and "Staff Interface" while the diagram uses `KioskUI`/`AdminUI`/"Staff Dashboard". Names are inconsistent across the two.
- The component table says the Web Interface "sends reservation and payment data to the server". That implies card data passes through the app, which conflicts with a tokenized, gateway-hosted flow and aligns with the PCI concern above.
- The Payment Gateway is shown with a circle node `(( ))` (typically meaning a circle or start/end node), while the database uses a cylinder. This is stylistic, but the shape choice for an external system is not consistent with the stated convention.

### Actor section vs. design
- Actors list **Customer online**, **Customer kiosk**, **Employee**, **Manager**, **Owner**; the goals call these "tiers" with four levels (customer, employee, manager, owner), so the two lists are inconsistent in structure.
- The owner's description ("maybe helps if they're cool") is informal and non-specific. The Staff Interface component says "owner (data reports)", which is the only usable definition.
- The manager "oversees employees", but no function in the document performs employee management (accounts, scheduling, etc.).

---

## 8. Failure Modes Issues

| Row | Issue |
|---|---|
| **Payment Gateway Timeout** | "retries 3 times" has no backoff or idempotency spec; a retried auth may double-authorize the card. The state of the inventory lock during retries is undefined. "Employees can process payment in-store" has no matching interface. |
| **Kiosk Card Reader Failure** | Message text "swipe Unavailable" mixes technology terms (modern cards are chip/tap). The manual-entry fallback is a PCI and security concern (see 6), and the failure also breaks the NFR that kiosks have a card reader attached. |
| **Double Booking** | The resolution claims the first request wins, but it doesn't describe the mechanism (transaction isolation, row locking, unique constraint on bike+time range). Also, the failure mode says "bike assigned to two reservations" as the *impact*, yet the stated resolution prevents it, so the table describes prevention, not recovery. Multi-bike partial conflicts aren't covered. |
| **Rental Forgotten** | The detection resolution (overdue check) doesn't address a **late-fee dispute** (the customer returned on time, the employee forgot to process). `returnBikes` takes `returnTime` as a parameter, so a retroactive return can be recorded, but the policy for waiving or recomputing fees isn't stated. |
| **Missing failure modes** | Database outage; app-server crash mid-booking (lock without auth); gateway auth succeeds but the DB write fails (orphaned authorization); capture declined at return; expired authorization; bike damaged during rental; customer no-show; clock skew between kiosk and server; double submission/duplicate requests; payment gateway down at *return* time (charge deferred?). |

---

## 9. Document Structure & Quality Issues

- **Heading typos / inconsistencies**: "Class Diagam", "Bend Bike Shop" vs. file naming, mixed casing across headings (`overview`, `actors`, `Goals & Non-Goals`, `Constraints`).
- **Heading levels**: "Goals & Non-Goals" has subsections (`###`), but other sections like Interfaces/Invariants use numbered lists with inconsistent bold/bullet usage.
- **Pervasive spelling errors** that hurt clarity and searchability (e.g. "availablilty", "retunrs", "reasignment", "adjustiments", "guaruntees", "overwritter", "reservaation", "accues", "mantinence", "refrences", "iff"). A pass with a spell-checker is warranted. "Iff" appears to be an intentional logic shorthand, but it should be spelled "if and only if" in prose.
- **Inconsistent terminology**: `Staff Interface` / `Admin UI` / `Staff Dashboard`; `Store Staff / Mgmt`; "bike condition" / "inventory status" / "condition_status"; "booked rate" / "baseRate" / "hourly_rate"; "reservation status" values in mixed case (`pending`/`PENDING`/`confirmed`/`CONFIRMED`).
- **Informal or non-professional language** in a technical document ("maybe helps if they're cool").
- **Inconsistent interface formatting**: some entries capitalize labels ("Purpose:"), others don't ("purpose:"); one interface has an empty `notes:`; markdown for generics (`List < String >`) is inconsistent (`List< String >`, `List~Bike~` in Mermaid is correct, but not in prose).
- **Table formatting**: The Non-Functional Requirements table's column "Function" is wrong (should be "Description"/"Target"). The Failure Modes table is missing its leading pipe on the header row (renders inconsistently in some Markdown parsers).
- **Missing front matter**: no version, author, date, status, or glossary, and no stated scope of "partial" sections (acceptable for a draft, but a "TBD" or placeholder heading for each missing section would aid review).
- **No traceability**: Goals, constraints, interfaces, and invariants aren't cross-referenced. For example, there is no link from each goal to the interface or component that satisfies it.
- **Mermaid**: Diagrams are syntactically plausible, but the ER diagram's `PK`/`FK` usage is consistent while the class diagram uses mixed visibility notation and unmatched types (`BikeType`, `BikeCondition`, `ReservationStatus` are used but not defined as enums).

---

## 10. Summary of Highest-Priority Fixes

1. **Fix the ER cardinalities** (Reservation↔Bike must be many-to-many; Reservation↔Transaction should be zero-to-many) and add the missing entities (Staff, join table, audit/log, rate rules).
2. **Define the reservation lifecycle** (full status enum, transitions, expiry of pending locks, cancellation, no-show, overdue).
3. **Resolve the pre-authorization vs. final-charge gap** (late fees, overrides, damages, expired authorizations, failed capture).
4. **Reconcile Invariants 3 and 4** with the behaviors they conflict with (damage fees and overrides; out-of-service bikes with existing reservations).
5. **Specify the bike condition/status model** (separate condition from availability/rental state, add the repair-to-ready path).
6. **Add the missing interfaces** (cancellation, search availability, reporting, confirmation delivery, notifications) and **error semantics** for all interfaces.
7. **Define authorization** consistently (who may call each interface, role model) and add `employeeId` to `returnBikes`.
8. **Address PCI/security** implications of kiosk manual entry and in-store payment fallback.
9. **Clarify the cancellation and late-fee rules** (24-hour direction, grace period semantics, fee formula).
10. **Clean up terminology, naming, typos, and table formatting**, and align the ER, class, and component diagrams with each other.