## WBS
* Bend Bike Shop System(100%)
    * frontend (40%)
        * Customer interface
            * homepage
            * accounts
            * reservations
            * inventory
        * employee interface 
            * reservation handoff
            * reservation checkin
            * bike condition report
        * manager interface
            * reservation adjustments
            * price adjustments
            * employee managing
        * owner interface
            * sales overveiw/preformance
    * backend(60%)
        * DataBase
        * Inventory allocation
            * bike statuses
            * reservation dates
                * overlap managment
        * Reservation API
        * Return API
        * Staff API
        * Payment API
            * communication with outisde payment portal
        * Kiosk interaction

## PERT
- Frontend: 114.7 hrs
- Backend: 169.0 hrs 
- Total: 283.7

## P90
- 303.5 hours

## CPM
| Task ID | Task Description | Duration (D) | Dependencies | ES | EF | LS | LF | Slack | Critical? |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **REQ-01** | System Requirements & Constraints | 8 | None | 0 | 8 | 0 | 8 | 0 | Yes |
| **REQ-02** | Component Diagram | 6 | REQ-01 | 8 | 14 | 10 | 16 | 2 | No |
| **REQ-03** | ER Diagram | 8 | REQ-01 | 8 | 16 | 11 | 19 | 3 | No |
| **REQ-04** | User Scenarios & Use Cases | 8 | REQ-01 | 8 | 16 | 8 | 16 | 0 | Yes |
| **API-01** | Account Roles API Outline | 4 | REQ-04 | 16 | 20 | 27 | 31 | 11 | No |
| **API-02** | Reservation Creation API Outline | 8 | REQ-02, REQ-04 | 16 | 24 | 16 | 24 | 0 | Yes |
| **API-03** | Outside Credit Auth Interactions | 6 | REQ-02, REQ-04 | 16 | 22 | 24 | 30 | 8 | No |
| **API-04** | Bike Handoffs API Outline | 6 | REQ-04 | 16 | 22 | 131 | 137 | 115 | No |
| **API-05** | Web Interaction with DB Outline | 6 | REQ-02, REQ-03 | 16 | 22 | 79 | 85 | 63 | No |
| **DB-01** | Accounts & Roles Schema | 4 | REQ-03, API-01 | 20 | 24 | 31 | 35 | 11 | No |
| **DB-02** | Inventory Schema | 5 | REQ-03 | 16 | 21 | 19 | 24 | 3 | No |
| **DB-03** | Bike Statuses Schema | 4 | DB-02 | 21 | 25 | 31 | 35 | 10 | No |
| **DB-04** | Reservation Data Schema | 6 | DB-02, API-02 | 24 | 30 | 24 | 30 | 0 | Yes |
| **DB-05** | Transaction Data Schema | 5 | API-03, DB-04 | 30 | 35 | 30 | 35 | 0 | Yes |
| **DB-06** | Current Pricing Schema | 6 | DB-02 | 21 | 27 | 29 | 35 | 8 | No |
| **BE-01** | Database Implementation | 24 | DB-01, DB-03, DB-05, DB-06 | 35 | 59 | 35 | 59 | 0 | Yes |
| **BE-02** | Reservation Overlap Handling | 26 | BE-01, API-02 | 59 | 85 | 59 | 85 | 0 | Yes |
| **BE-03** | Interfaces: DB, Frontend & Payment API | 32 | BE-02, API-05 | 85 | 117 | 85 | 117 | 0 | Yes |
| **BE-04** | Employee Leveled Permissions | 18 | BE-01, API-04 | 59 | 77 | 137 | 155 | 78 | No |
| **BE-05** | Owner Data Reports | 20 | BE-01 | 59 | 79 | 135 | 155 | 76 | No |
| **FE-01** | Web Interface (Customer Portal) | 40 | BE-03 | 117 | 157 | 117 | 157 | 0 | Yes |
| **FE-02** | Kiosk Interface with Card Reader | 24 | FE-01 | 157 | 181 | 157 | 181 | 0 | Yes |
| **FE-03** | Employee, Manager, Owner Homepages | 26 | BE-04, BE-05 | 79 | 105 | 155 | 181 | 76 | No |

## Gantt
```mermaid
gantt
    title Bend Bike Shop System - CPM Schedule & Critical Path
    dateFormat YYYY-MM-DD-HH
    axisFormat Day %j

    section Phase 1 Requirements
    REQ-01 System Requirements and Constraints    :crit, active, req1, 2026-11-01-00, 8h
    REQ-02 Component Diagram                     :active, req2, after req1, 6h
    REQ-03 ER Diagram                            :active, req3, after req1, 8h
    REQ-04 User Scenarios and Use Cases          :crit, active, req4, after req1, 8h

    section Phase 2 API Outline
    API-01 Account Roles API Outline             :active, api1, after req4, 4h
    API-02 Reservation Creation API Outline      :crit, active, api2, after req4, 8h
    API-03 Outside Credit Auth Interactions      :active, api3, after req4, 6h
    API-04 Bike Handoffs API Outline             :active, api4, after req4, 6h
    API-05 Web Interaction with DB Outline       :active, api5, after req3, 6h

    section Phase 3 Database Layout
    DB-01 Accounts and Roles Schema              :active, db1, after api1, 4h
    DB-02 Inventory Schema                       :active, db2, after req3, 5h
    DB-03 Bike Statuses Schema                   :active, db3, after db2, 4h
    DB-04 Reservation Data Schema                :crit, active, db4, after api2, 6h
    DB-05 Transaction Data Schema                :crit, active, db5, after db4, 5h
    DB-06 Current Pricing Schema                 :active, db6, after db2, 6h

    section Phase 4 Backend
    BE-01 Database Implementation                :crit, active, be1, after db5, 24h
    BE-02 Reservation Overlap Handling           :crit, active, be2, after be1, 26h
    BE-03 Interfaces DB Frontend and Payment API :crit, active, be3, after be2, 32h
    BE-04 Employee Leveled Permissions           :active, be4, after be1, 18h
    BE-05 Owner Data Reports                     :active, be5, after be1, 20h

    section Phase 5 Frontend
    FE-01 Web Interface Customer Portal          :crit, active, fe1, after be3, 40h
    FE-02 Kiosk Interface with Card Reader       :crit, active, fe2, after fe1, 24h
    FE-03 Staff and Owner Homepages              :active, fe3, after be5, 26h
```