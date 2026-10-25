\# Review Report: Bend Bike Shop Software Technical Design Document



\*\*Document reviewed:\*\* `techdoc.md`

\*\*Scope:\*\* Logical, structural, consistency, and quality issues. Sections known to be incomplete are noted but not penalized, except where the gaps cause contradictions or block understanding.



\---



\## 1. Summary



The document has a sensible overall skeleton (Overview, Actors, Goals, Constraints, Assumptions, NFRs, Component Diagram). The main problems are:



\- Several goals have no supporting component, constraint, or requirement.

\- Some requirements contradict each other or are ambiguous.

\- The component diagram and component table don't fully match.

\- The "Non-Functional Requirements" section mostly contains functional requirements.

\- Unprofessional or placeholder text, plus many spelling errors.

\- The requested \*\*examples\*\* are absent.



| Severity | Count |

|---|---|

| High | 6 |

| Medium | 9 |

| Low | 6 |



\---



\## 2. High Severity Issues



\### H1. Cancellation constraint contradicts same-day and kiosk bookings

\- \*\*Location:\*\* Constraints, "reservations can be canceled 24 hours before the rental time"

\- \*\*Issue:\*\* Kiosk customers reserve bikes "now," so they can never meet a 24-hour cancellation window. The doc doesn't say whether kiosk rentals are cancellable, or what happens to bookings made less than 24 hours ahead.

\- \*\*Also:\*\* The wording is ambiguous. It could mean "at least 24 hours before" or "within the 24 hours before." Most likely the former.

\- \*\*Recommendation:\*\* State "cancellable up to 24 hours before start time," define behavior for bookings made inside that window, and state the refund/pre-auth release policy.



\### H2. Payment flow is under-specified and inconsistent

\- \*\*Location:\*\* Constraints, Assumptions, Component table

\- \*\*Issues:\*\*

&#x20; - "Pre-authorized when booking but no charges until the bikes are returned" ignores that card pre-authorizations typically expire (often 7 to 30 days depending on the network and issuer). Far-future reservations may outlive the authorization.

&#x20; - No handling for failed authorization, declined final charge, or damage charges exceeding the pre-auth amount.

&#x20; - Late fees and damage fees are charged after return, but the process is not described. This matters because an employee inspects damage on return.

&#x20; - The \*\*Payment Gateway\*\* row says it "sends final billing," which is inaccurate. The gateway processes charges; the application server initiates billing.

&#x20; - The pre-auth amount is never defined (deposit? estimated rental cost?).

&#x20; - "Automated cancellation compensation" is a Non-Goal, but there is nothing about how cancellation affects the pre-auth hold (release vs. fee).

\- \*\*Recommendation:\*\* Add a payment lifecycle (authorize, hold, capture, release, fee adjustment) and state the pre-auth amount and expiry-handling policy.



\### H3. Core goal "avoid over/double booking" has no mechanism

\- \*\*Location:\*\* Goals vs. Component table

\- \*\*Issue:\*\* This is the headline goal, but nothing describes how it is achieved: transactional locking, atomic reservation, handling concurrent web and kiosk requests, or how time-slot availability is computed.

\- \*\*Related contradiction:\*\* The Manager actor "helps with overbooking due to damaged returns," which implies overbooking can occur, while the Non-Goal says "automatic stock reassignment when bikes are inoperable" is out of scope. The doc never explains how the overbooking from a damaged return is resolved manually, or what the customer experience is.

\- \*\*Recommendation:\*\* Define the availability model (per bike vs. per category/type), the concurrency strategy, and a manual overbooking-resolution workflow.



\### H4. Unclear Actor / role model and access tiers

\- \*\*Location:\*\* Actors, Goals ("tier based system access"), Staff Interface

\- \*\*Issues:\*\*

&#x20; - Goals list four tiers (customer, employee, manager, owner); the Component table's Staff Interface describes only manager, employee, and owner, and the diagram groups "Store Staff / Mgmt" together while omitting the Owner.

&#x20; - Role permissions are described only loosely. Does the manager inherit employee permissions? Can the owner see/modify inventory? Who adjusts pricing?

&#x20; - \*\*Dynamic pricing\*\* is a goal, but no actor owns it and no component implements it.

&#x20; - Customers have no stated authentication or account model. Are they guests, or do they have accounts? How do they retrieve or cancel a reservation (confirmation code only)?

\- \*\*Recommendation:\*\* Add a role/permission matrix and define the customer identity model.



\### H5. Missing functional behavior for the inventory status model

\- \*\*Location:\*\* Goals, "management of inventory status (service, ready, checked out)"

\- \*\*Issues:\*\*

&#x20; - There is no state diagram or transition rules. "Reserved" is absent, even though future reservations exist. Is a reserved-but-not-picked-up bike "ready"?

&#x20; - No status for "returned, pending inspection," even though the Employee actor inspects returns.

&#x20; - Who can change status, and what triggers each transition?

\- \*\*Recommendation:\*\* Add a state machine (e.g., Ready, Reserved, Checked Out, Pending Inspection, In Service) with allowed transitions and actors.



\### H6. "Non-Functional Requirements" section contains mostly functional items and lacks real NFRs

\- \*\*Location:\*\* Non-Functional Requirements

\- \*\*Issues:\*\*

&#x20; - "Booking confirmation," "Card reader," and "Kiosk idle timeout" are functional or hardware requirements.

&#x20; - The table's second column is labeled "Function," which is incorrect for a requirements table (and reinforces the confusion). It should likely be "Description" or "Requirement."

&#x20; - True NFRs are missing: performance, concurrency/scalability, security, PCI compliance, data retention/privacy, accessibility, backup/recovery, browser support, and logging/audit.

&#x20; - The 99.9% uptime sits under Assumptions rather than as a measurable requirement. It is also phrased as an assumption about "the online system," which is the system being designed, so it's unclear whether this is a requirement on the project or an external dependency.

\- \*\*Recommendation:\*\* Rename/split into Functional vs. Non-Functional, and add measurable NFRs.



\---



\## 3. Medium Severity Issues



\### M1. Kiosk idle timeout is ambiguous

\- "Prompts the user after 60 seconds and resets after timeout" doesn't state the total timeout duration after the prompt, what is reset (session data, partially entered card data), or how card data is cleared for security.



\### M2. Component diagram and table are inconsistent

\- Diagram nodes are named \*\*Web Interface, Kiosk Touchscreen \& Card Reader, Staff Dashboard\*\*; the table uses \*\*Web Interface, Kiosk Interface, Staff Interface\*\*. Use consistent names.

\- The diagram doesn't show the Owner or separate roles, and shows the card reader as part of the kiosk UI, whereas "card reader attached to kiosk" is in the NFR table.

\- The Payment Gateway is drawn as a circle `(( ))` (a "circle" node in Mermaid) while the database is a cylinder; this is fine stylistically, but there is no legend or explanation of the shapes.

\- No notification/email component exists, even though "easy online booking with confirmations" is a goal (emailed or SMS confirmation vs. on-screen only). The NFR table only mentions an on-screen confirmation.

\- Arrows are all bidirectional (`<-->`), which obscures the actual data flow. Customer-to-interface arrows are one-directional despite the user receiving output.



\### M3. Late fee constraint is incomplete

\- "Late feed applied after 30 mins past the return time": there is no fee amount, rate structure (flat vs. hourly), cap, or grace-period behavior (is it charged retroactively from the original return time?). Also "feed" is a typo for "fee."

\- No mention of how late returns affect downstream reservations of the same bike, or how overdue (never returned) bikes are handled.



\### M4. "Timely returns" evaluation has no defined owner or process

\- The Employee "evaluates timely returns," but the system role in calculating lateness vs. manual judgment is unclear (manual vs. automatic late fee).



\### M5. No data model

\- A database is listed, but there is no outline of core entities (Bike, Reservation, Customer, Staff, Payment, MaintenanceRecord, PricingRule) or relationships. This is acceptable for a partial doc but should be flagged as a required section.



\### M6. "Dynamic price adjustments" is undefined

\- Is this time-based, demand-based, or manually set by managers? How are existing reservations affected when prices change?



\### M7. "History and summary reports" lacks scope

\- No list of required reports or metrics, though the Owner actor "evaluates performance numbers." Define the reports (utilization, revenue, damage rate, late rate).



\### M8. Missing key sections for a technical design document

\- Not present: data model, API/interface definitions, sequence diagrams for core flows (online booking, kiosk booking, handoff, return), error handling, security design, deployment/infrastructure, technology stack, testing strategy, risks, open questions, glossary, and revision history/authorship.

\- The Overview doesn't describe the problem statement, scope, or success criteria.



\### M9. Unattended handoff Non-Goal vs. Constraint overlap

\- "Unattended bike handoffs" (Non-Goal) and "Bike handoffs must be facilitated by an employee" (Constraint) are redundant. Consolidate, and note that this drives the kiosk design (kiosk can only reserve and pay, not release bikes).

\- Related: after a kiosk "reserve now," the doc never says how the customer and employee connect (confirmation code scan? employee dashboard lookup?).



\---



\## 4. Low Severity / Style Issues



\### L1. Unprofessional / placeholder wording

\- Owner actor: \*"evaluates performance numbers and maybe helps if they're cool"\*. This is informal, non-committal, and not a valid responsibility description. Replace with a concrete role (e.g., reviews performance reports, manages pricing policy, approves staff).



\### L2. Spelling and typographical errors

The following should be corrected:



| Found | Correct |

|---|---|

| aswell | as well |

| availablilty | availability |

| acess | access |

| managment | management |

| adjustiments | adjustments |

| retunrs | returns |

| feed (late feed) | fee |

| reservaion | reservation |

| overveiw | overview |

| attatched | attached |

| availible | available |

| bases on | based on |

| mantinence | maintenance |

| reasignment | reassignment |



\### L3. Inconsistent capitalization and formatting

\- Mixed capitalization in headings ("component diagram" lowercase vs. "Goals \& Non-Goals") and bullet items (some lowercase, some capitalized).

\- Inconsistent spacing in "(customer, employee, manager, owner)" and missing spaces before parentheses, e.g. `inventory status(service...)`, `manager(stock admin acess)`.

\- Trailing space in the "component diagram" heading.

\- Table descriptions have inconsistent casing and punctuation.

\- "Bend bike shop" should be capitalized consistently as a proper noun ("Bend Bike Shop").



\### L4. Grammar and clarity

\- "Handles handoff of bikes from the system to customers and stocks in bike returns": unclear. Suggest: "Hands bikes off to customers and restocks returned bikes."

\- "Customer online: reserve different bikes and time slot based on online stock availability": clarify that customers choose bike type and a time slot.

\- "Assumptions: web based" is a sentence fragment and is a design decision, not an assumption. "Third party payment authorizations" is also a fragment.



\### L5. Bullet and list conventions

\- Constraints and Goals use unpunctuated, inconsistent-length fragments. Use a consistent style (e.g., "The system shall...").

\- Requirements have no IDs, which makes traceability and review difficult. Suggest IDs such as FR-01, NFR-01, C-01.



\### L6. "Examples" are missing

\- You noted you were instructed to include examples, but the document contains none. Suggested places for examples:

&#x20; - A sample reservation record and confirmation code format.

&#x20; - A worked late-fee scenario (e.g., return due 3:00 PM; returned at 3:45 PM; late fee applied).

&#x20; - A worked overbooking scenario (damaged return makes a reserved bike unavailable; manager resolves).

&#x20; - A booking sequence diagram (customer to web to app server to payment gateway to DB).



\---



\## 5. Known-Incomplete Sections (Informational)



These gaps are acknowledged as incomplete and are listed only so they are tracked:



\- Data model and schemas

\- API/interface specifications

\- Sequence/flow diagrams

\- Security and compliance (PCI-DSS scope in particular, since kiosks have card readers)

\- Deployment and infrastructure

\- Error handling and edge cases

\- Testing approach



\---



\## 6. Recommended Next Steps (Prioritized)



1\. Resolve the cancellation, payment, and overbooking logic (H1 to H3).

2\. Define roles/permissions and the inventory state machine (H4, H5).

3\. Split and rewrite the requirements section into functional vs. non-functional, with measurable targets (H6).

4\. Align diagram and table naming; add a notification component and the Owner role (M2).

5\. Add the requested examples (L6).

6\. Clean up wording, spelling, and formatting (L1 to L5).

