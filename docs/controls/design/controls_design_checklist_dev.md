<div align="center">

# Controls Software Design Checklist (Fillable)

**A comprehensive internal checklist and design guide for controls automation engineers**

![Version](https://img.shields.io/badge/version-1.00.00-blue.svg)

[Project Summary & Scope](#1-project-summary--scope) • [Stakeholders & communication](#13-stakeholders--communication) • [Customer Standards](#2-customer-software-standards--templates-end-customer-specifications) • [Blockpoint](#3-blockpoint-specifications-software-hardware-firmware-revisions) • [Hardware Drawings](#5-hardware-drawings--documents-received-and-dates) • [Hardware Span](#6-hardware-span-of-controls-operational-equipment-scope) • [Safety Span](#7-safety-span-of-controls-system-wide)

</div>

**Document ID:**                                                 ____________________  
**Project Name:**                                                ____________________  
**System Name:**                                                 ____________________  
**Customer / End User:**                                         ____________________  
**Site / Location:**                                             ____________________  
**System Type:** ☐ New system ☐ Retrofit ☐ Expansion ☐ Other:  ____________________  
**Project Manager:**                                             ____________________  
**Project Engineer:**                                            ____________________  
**Date: (yyyy-mm-dd)**                                           ______ - ____ - ____  
**Revision:**                                                    ____________________  
**Document Revision:** *v1.00.00*  

---

## 0) How to use this checklist

- Fill this out during design and keep it updated through FAT/SAT.
- If a section is not applicable, mark it **N/A** and briefly explain why.
- Attach/Link supporting documents (customer standards, drawings, network diagrams, safety docs, etc.).

---

## 1) Project Summary & Scope

### 1.1 System overview

- Process / cell description:                                         ________________________________________________
- Primary objectives (throughput, quality, traceability, etc.):       ________________
- Key constraints (downtime window, change control, plant standards): __________
- Logical 'Cell' count:                                               __________
- Logical 'Station' count:                                            __________
- Logical 'HMI' count:                                                __________
- Interlocked # of systems:                                           __________

### 1.2 In-scope equipment / areas

- Equipment list or reference: _____________________________________________
- Out-of-scope items (explicit): ____________________________________________

### 1.3 Stakeholders & communication

#### 1.3.1 Customer Contacts

| Roll        | Personnel Name (Last, First) | Personnel Phone # | Personnel Email Address | Notes |
| ----------- | ---------------------------- | ----------------- | ----------------------- | ----- |
| Operations  |                              |                   |                         |       |
| Maintenance |                              |                   |                         |       |
| IT          |                              |                   |                         |       |
| Safety      |                              |                   |                         |       |

#### 1.3.2 Integrator Contacts

| Roll            | Personnel Name (Last, First) | Personnel Phone # | Personnel Email Address | Notes |
| --------------- | ---------------------------- | ----------------- | ----------------------- | ----- |
| Project Manager |                              |                   |                         |       |
| Controls        |                              |                   |                         |       |
| Robotics        |                              |                   |                         |       |
| Mechanical      |                              |                   |                         |       |
| Electrical      |                              |                   |                         |       |
| Pneumatic       |                              |                   |                         |       |

#### 1.3.3 Misc Contacts

> Note💡 Include vendors, integrators, etc. for interlocks or job specific needs.

| Roll                     | Personnel Name (Last, First) | Personnel Phone # | Personnel Email Address | Notes |
| ------------------------ | ---------------------------- | ----------------- | ----------------------- | ----- |
| ________________________ |                              |                   |                         |       |
| ________________________ |                              |                   |                         |       |
| ________________________ |                              |                   |                         |       |
| ________________________ |                              |                   |                         |       |
| ________________________ |                              |                   |                         |       |
| ________________________ |                              |                   |                         |       |

---

## 2) Customer software standards & templates (End-customer specifications)

### 2.1 Customer standards

- ☐ Customer blockpoint received
- ☐ Customer naming convention received
- ☐ Customer alarm / factory information philosophy received
- ☐ Customer programming standard received
- ☐ Customer HMI standards received (colors, navigation, faceplates)
- ☐ Customer network / cybersecurity standard received
- ☐ Customer plc->plc interlocking standards received

### 2.2 Customer-provided templates (attach/link paths)

- Design documentation (Excel, Word, PDF, PPT): _____________________________
- Blockpoint Schedule: _____________________________
- Template PLC code (AOIs, UDTs, base project): _____________________________
- Template HMI project: ____________________________________________________
- Template drive configuration files: _______________________________________
- Other templates (safety, robot, vision, historian): ________________________

### 2.3 Template gaps / deviations

- Deviations required? ☐ No ☐ Yes (detail): _________________________________
- Customer approval required? ☐ No ☐ Yes (who/when): ________________________

---

## 3) Blockpoint specifications (software, hardware, firmware revisions)

> Goal: lock the “known-good” baseline for PLCs, HMIs, drives, and key components.

### 3.1 PLC baseline

| Item                     | Manufacturer | Model | Hardware Rev | Firmware Rev | Software / IDE Version | Options / Notes |
| ------------------------ | ------------ | ----- | ------------ | ------------ | ---------------------- | --------------- |
| Primary PLC              |              |       |              |              |                        |                 |
| Safety PLC (if separate) |              |       |              |              |                        |                 |
| Remote I/O Adapter(s)    |              |       |              |              |                        |                 |
| Comms Module(s)          |              |       |              |              |                        |                 |

### 3.2 HMI / SCADA baseline

| Item       | Platform | Model / Runtime | Hardware Rev | Firmware Rev | Dev Software Version | Runtime Version | Notes |
| ---------- | -------- | --------------- | ------------ | ------------ | -------------------- | --------------- | ----- |
| Panel HMI  |          |                 |              |              |                      |                 |       |
| SCADA Node |          |                 |              |              |                      |                 |       |

### 3.3 Drives baseline

| Item          | Manufacturer | Model | Frame / HP | Firmware Rev | Config Tool Version | Config File Name/ID | Notes |
| ------------- | ------------ | ----- | ---------- | ------------ | ------------------- | ------------------- | ----- |
| VFD           |              |       |            |              |                     |                     |       |
| VFD           |              |       |            |              |                     |                     |       |
| VFD           |              |       |            |              |                     |                     |       |
| VFD           |              |       |            |              |                     |                     |       |
| VFD           |              |       |            |              |                     |                     |       |
| Motor Starter |              |       |            |              |                     |                     |       |
| Motor Starter |              |       |            |              |                     |                     |       |
| Motor Starter |              |       |            |              |                     |                     |       |
| Motor Starter |              |       |            |              |                     |                     |       |
| Motor Starter |              |       |            |              |                     |                     |       |

## 3.4 Robots baseline

| Item             | Manufacturer | Model | Hardware Rev | Firmware Rev | Software / IDE Version | Options / Notes |
| ---------------- | ------------ | ----- | ------------ | ------------ | ---------------------- | --------------- |
| Material Handler |              |       |              |              |                        |                 |
| Material Handler |              |       |              |              |                        |                 |
| Material Handler |              |       |              |              |                        |                 |
| Material Handler |              |       |              |              |                        |                 |
| Welder           |              |       |              |              |                        |                 |
| Welder           |              |       |              |              |                        |                 |
| Sealer           |              |       |              |              |                        |                 |
| Sealer           |              |       |              |              |                        |                 |
| Special          |              |       |              |              |                        |                 |
| Special          |              |       |              |              |                        |                 |

## 3.5 Vision baseline

| Item                          | Manufacturer | Model | Hardware Rev | Firmware Rev | Software / Runtime Version | Config / Project File Name/ID | Notes                                 |
| ----------------------------- | ------------ | ----- | ------------ | ------------ | -------------------------- | ----------------------------- | ------------------------------------- |
| Smart camera / sensor         |              |       |              |              |                            |                               |                                       |
| Vision controller / IPC       |              |       |              |              | OS: ____ / Image: ____     |                               |                                       |
| Vision software package       |              |       | N/A          | N/A          |                            |                               |                                       |
| Camera lens                   |              |       |              | N/A          | N/A                        | N/A                           | Focal length: ____ / Filter: ____     |
| Light / illuminator           |              |       |              |              | N/A                        | N/A                           | Color/wavelength: ____ / Driver: ____ |
| Trigger / strobe controller   |              |       |              |              |                            |                               | If separate from camera/controller    |
| Encoder / timing source       |              |       |              |              | N/A                        | N/A                           | PPR: ____                             |
| Network switch / PoE injector |              |       |              |              | N/A                        | N/A                           | VLAN/QoS notes: ____                  |

### 3.6 Other critical baselines (as applicable)

- Motion / servos: ________________________________________________________
- Barcode / RFID: _________________________________________________________
- Safety devices (relays, scanners): _______________________________________
- Other: __________________________________________________________________

### 3.7 Baseline verification

- ☐ Baselines match purchased hardware BOM
- ☐ Baselines match plant standards
- ☐ Any mismatches documented & approved

---

## 5) Hardware drawings & documents received (and dates)

> Record exactly what drawings were received and which revisions were used.

| Document                   | Rev | Date Received | Source (Customer/OEM/ECAD) | Used For (IO, panel, network, etc.) | Notes |
| -------------------------- | --- | ------------- | -------------------------- | ----------------------------------- | ----- |
| Electrical schematics      |     |               |                            |                                     |       |
| Panel layout               |     |               |                            |                                     |       |
| Network diagram            |     |               |                            |                                     |       |
| Instrument list            |     |               |                            |                                     |       |
| P&IDs                      |     |               |                            |                                     |       |
| Safety documents (RA / SR) |     |               |                            |                                     |       |

---

## 6) Hardware span of controls (operational equipment scope)

### 6.1 Control architecture summary

- PLC count: ____  
- Remote I/O count: ____  
- HMI/SCADA nodes: ____
- Networks (e.g., EtherNet/IP, Profinet, Modbus, etc.): ______________________
- Time sync method (NTP/PTP/GPS/none): _____________________________________

### 6.2 Equipment span table

| Equipment / Area | Control Owner (PLC/Panel) | Local Controls (PBs, selectors) | Sensors / Actuators Summary | Special Notes |
| ---------------- | ------------------------- | ------------------------------- | --------------------------- | ------------- |
|                  |                           |                                 |                             |               |

### 6.3 IO summary (approx.)

- DI: ____  DO: ____  AI: ____  AO: ____
- Specialty IO (HSI, encoder, safety IO, motion): ___________________________

### 6.4 Field device assumptions

- Sensor types / ranges: _________________________________________________
- Valve types / fail positions: ___________________________________________
- Motor starters / VFD control method (IO, fieldbus): _______________________

---

## 7) Safety span of controls (system-wide)

> This section should align with the project’s risk assessment / safety requirement specification.

### 7.1 Safety basis

- Safety documentation reference(s): _______________________________________
- Target standard(s) / approach: ___________________________________________
- Required Performance Level / SIL targets: _________________________________

### 7.2 Safety architecture

- Safety controller(s) / relay(s): _________________________________________
- Safety networks (if any): ________________________________________________
- Safety zones / boundaries: _______________________________________________

### 7.3 Safety devices inventory

| Device Type   | Location / Zone | Tag / ID | Reset Method | Notes |
| ------------- | --------------- | -------- | ------------ | ----- |
| E-Stop        |                 |          |              |       |
| Gate switch   |                 |          |              |       |
| Light curtain |                 |          |              |       |
| Area scanner  |                 |          |              |       |

### 7.4 Safety functions list (high-level)

| Safety Function ID | Description | Inputs | Outputs | PL/SIL Target | Validation Method |
| ------------------ | ----------- | ------ | ------- | ------------- | ----------------- |
|                    |             |        |         |               |                   |

### 7.5 Safety validation & documentation

- ☐ Safety IO checkout plan defined
- ☐ Safety function test procedure defined
- ☐ Safety acceptance criteria defined
- ☐ Safety validation results captured and archived

---

## 8) Interlock specifications & details

> Capture all process, equipment, and safety-related interlocks. This becomes your implementation and test source-of-truth.

### 8.1 Interlock philosophy

- Interlock types used: ☐ permissive ☐ inhibit ☐ trip ☐ warning-only
- Bypass policy: ☐ none allowed ☐ key-switch ☐ password ☐ maintenance mode
- Reset philosophy: ☐ auto ☐ manual reset ☐ fault acknowledge then reset

### 8.2 Interlock matrix (summary)

| Interlock ID | Applies To | Condition / Inputs | Action / Outputs | Reset Requirement | Bypass Allowed | HMI Indication | Test / Verification |
| ------------ | ---------- | ------------------ | ---------------- | ----------------- | -------------- | -------------- | ------------------- |
|              |            |                    |                  |                   |                |                |                     |

### 8.3 Interlock implementation notes

- Standard pattern used (AOI/FB/state machine): _____________________________
- Where interlocks are enforced (PLC vs drive vs safety): ____________________
- Latched vs non-latched criteria: _________________________________________

---

## 9) Controls software design (PLC)

### 9.1 Project structure

- Program organization (tasks/programs/routines): ___________________________
- AOI/FB strategy (faceplates, diagnostics, simulation hooks): ______________
- Data structures (UDTs/DBs) naming and versioning approach: ________________

### 9.2 Tagging & naming

- Naming convention reference: _____________________________________________
- IO naming mapping strategy (per schematics): ______________________________

### 9.3 State models & sequencing

- Modes supported: ☐ Auto ☐ Manual ☐ Jog ☐ Maintenance ☐ Simulation
- Sequence description / reference: ________________________________________
- Fault handling strategy (stop category, recovery): _________________________

### 9.4 Diagnostics & maintainability

- ☐ Standard device diagnostics implemented
- ☐ Clear fault text and corrective actions defined
- ☐ “First out” / root-cause capture where applicable

### 9.5 Simulation / offline testing

- Simulation approach: ☐ built-in sim tags ☐ emulation ☐ test harness
- Sim boundaries & assumptions: ____________________________________________

---

## 10) HMI / SCADA design

### 10.1 HMI scope

- Screen list / navigation map reference: __________________________________
- User roles / security levels: ____________________________________________

### 10.2 Standards

- ☐ Alarm colors conform to customer standards
- ☐ Faceplates/objects conform to customer templates
- ☐ Units, ranges, and scaling defined

### 10.3 Alarm management

- Alarm philosophy reference: _____________________________________________
- Alarm priorities defined: ☐ Yes ☐ No
- Shelving / suppression requirements: _____________________________________

### 10.4 Data logging / historian (if applicable)

- Tags to log + rates: _____________________________________________________
- Batch/lot/traceability requirements: _____________________________________

---

## 11) Drive configuration & integration

### 11.1 Control method

- ☐ Hardwired IO control
- ☐ Fieldbus control
- ☐ Safety integration (STO, SS1, etc.) details: ____________________________

### 11.2 Standard parameters

- Speed limits, accel/decel, torque limits: _________________________________
- Motor nameplate data source: _____________________________________________

### 11.3 Config management

- Config file naming convention: ___________________________________________
- Storage location / version control location: ______________________________

---

## 12) Communications, networking, and cybersecurity

### 12.1 Network inventory

| Network | Subnet/VLAN | Devices | Managed By (IT/OT/Controls Integrator) | Notes |
| ------- | ----------- | ------- | -------------------------------------- | ----- |
|         |             |         |                                        |       |

### 12.2 IP addressing & naming

- IP plan reference: ______________________________________________________
- Hostname/device name plan: ______________________________________________

### 12.3 Cybersecurity baseline (project-appropriate)

- ☐ Accounts/roles defined
- ☐ Backup/restore procedure defined
- ☐ Remote access method approved
- ☐ Antivirus / whitelisting expectations aligned with customer

---

## 13) Timeline & milestones (planned vs actual)

| Milestone                          | Planned Date | Actual Date | Owner | Notes / Blockers |
| ---------------------------------- | ------------ | ----------- | ----- | ---------------- |
| Design kickoff complete            |              |             |       |                  |
| Drawings baseline received         |              |             |       |                  |
| Software architecture complete     |              |             |       |                  |
| First functional simulation        |              |             |       |                  |
| FAT ready                          |              |             |       |                  |
| FAT complete                       |              |             |       |                  |
| Site install / commissioning start |              |             |       |                  |
| SAT complete                       |              |             |       |                  |
| Handover complete                  |              |             |       |                  |

---

## 14) Testing, FAT/SAT, and acceptance criteria

### 14.1 Test scope & strategy

- IO checkout plan reference: _____________________________________________
- Interlock test procedure reference: ______________________________________
- Sequence / recipe test plan reference: ___________________________________

### 14.2 Acceptance criteria

- Customer acceptance criteria document: ___________________________________
- Punchlist process and closure criteria: ___________________________________

---

## 15) Deliverables, backups, and handover

### 15.1 Deliverables

- ☐ PLC source + compiled artifact as required
- ☐ HMI/SCADA project source + runtime package
- ☐ Drive configuration backups
- ☐ Network/IP plan
- ☐ Operator and maintenance documentation
- ☐ As-built drawings (or redlines)

### 15.2 Backup & restore

- Backup location: ________________________________________________________
- Restore validation performed: ☐ Yes ☐ No (notes): _________________________

---

## 16) Open items / risks / decisions

| Item | Owner | Due Date | Risk Level (L/M/H) | Mitigation / Notes |
| ---- | ----- | -------- | ------------------ | ------------------ |
|      |       |          |                    |                    |

---

## 17) Approvals / Sign-off

- Pre-Design: Before development begins, this document has been filled to satisfy internal quality control members to continue with design.
- Functional Design Check: Midway check to verify development is progressing in the correct direction. This is performed before customers get any design documentations.
- Post Desgin Check: Final off-site check to validate the structure of the software matches what is expetected by this documentation, internal QC engineers, and the customer.
- Integration Motion and Safety Check: Integration of controls equipment successful. This check occurs before automatic motion occurs in a system.
- Site Acceptance (optional): If the system is built on the floor of an integrator to test before shipping to production facilities, this check is to ensure the integrating mechanical company is satisfied with the equipment.
- Factory Acceptance: The final system check. All previous checks complete, system ready for purchase by customer. All issues closed and ready to sell.

### 17.1 Pre-Design

| Role                               | Name | Date | Signature / Initials |
| ---------------------------------- | ---- | ---- | -------------------- |
| Controls Lead                      |      |      |                      |
| Project Manager                    |      |      |                      |
| Safety (optional)                  |      |      |                      |
| Customer Representative (optional) |      |      |                      |

### 17.2 Functional Design Check (50%)

| Role                               | Name | Date | Signature / Initials |
| ---------------------------------- | ---- | ---- | -------------------- |
| Controls Lead                      |      |      |                      |
| Project Manager                    |      |      |                      |
| Safety (optional)                  |      |      |                      |
| Customer Representative (optional) |      |      |                      |

### 17.3 Post Design Check (90%)

| Role                               | Name | Date | Signature / Initials |
| ---------------------------------- | ---- | ---- | -------------------- |
| Controls Lead                      |      |      |                      |
| Project Manager                    |      |      |                      |
| Safety (optional)                  |      |      |                      |
| Customer Representative (optional) |      |      |                      |

### 17.4 Integration Motion and Safety Check

| Role                               | Name | Date | Signature / Initials |
| ---------------------------------- | ---- | ---- | -------------------- |
| Controls Lead                      |      |      |                      |
| Project Manager                    |      |      |                      |
| Safety (optional)                  |      |      |                      |
| Customer Representative (optional) |      |      |                      |

### 17.5 Site Acceptance (optional)

| Role                               | Name | Date | Signature / Initials |
| ---------------------------------- | ---- | ---- | -------------------- |
| Controls Lead                      |      |      |                      |
| Project Manager                    |      |      |                      |
| Safety (optional)                  |      |      |                      |
| Customer Representative (optional) |      |      |                      |

### 17.6 Factory Acceptance

| Role                               | Name | Date | Signature / Initials |
| ---------------------------------- | ---- | ---- | -------------------- |
| Controls Lead                      |      |      |                      |
| Project Manager                    |      |      |                      |
| Safety (optional)                  |      |      |                      |
| Customer Representative (optional) |      |      |                      |

---

## 18) Appendix (links / references)

- Customer standards: _________________________________________________
- Drawings folder: ____________________________________________________
- Code repository / tag: ______________________________________________
- FAT/SAT reports: ____________________________________________________
