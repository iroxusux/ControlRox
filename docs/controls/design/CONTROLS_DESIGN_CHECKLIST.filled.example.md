<div align="center">

# Controls Software Design Checklist (Fillable)

**A comprehensive internal checklist and design guide for controls automation engineers**

![Version](https://img.shields.io/badge/version-1.00.00-blue.svg)

[Project Summary & Scope](#1-project-summary--scope) • [Stakeholders & communication](#13-stakeholders--communication) • [Customer Standards](#2-customer-software-standards--templates-end-customer-specifications) • [Blockpoint](#3-blockpoint-specifications-software-hardware-firmware-revisions) • [Hardware Drawings](#5-hardware-drawings--documents-received-and-dates) • [Hardware Span](#6-hardware-span-of-controls-operational-equipment-scope) • [Safety Span](#7-safety-span-of-controls-system-wide)

</div>

**Document ID:** EX-001  
**Project Name:** Example Project  
**System Name:** Cell A  
**Customer / End User:** Example Customer  
**Site / Location:** Example Site  
**System Type:** New system  
**Project Manager:** ____________________  
**Project Engineer:** ____________________  
**Date: (yyyy-mm-dd)** 2025-12-31  
**Revision:** A  
**Document Revision:** *v1.00.00*  

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 0) How to use this checklist

</div>

- Fill this out during design and keep it updated through FAT/SAT.
- If a section is not applicable, mark it **N/A** and briefly explain why.
- Attach/Link supporting documents (customer standards, drawings, network diagrams, safety docs, etc.).

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 1) Project Summary & Scope

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 1.1 System overview

</div>

- **Process / cell description:** An example process cell for demonstration.
- **Primary objectives:** Filling and packaging products.
- **Key constraints:** Engineers understanding this example and document
- **Logical 'Cell' count:** 1
- **Logical 'Station' count:** 2
- **Logical 'HMI' count:** 1
- **Interlocked # of systems:** 2

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 1.2 In-scope equipment / areas

</div>

- **Equipment list or reference:** 2
- **Out-of-scope items:** 1

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 1.3 Stakeholders & communication

</div>

<div style="background-color: darkred; padding: 2px; border-radius: 5px;">

#### 1.3.1 Customer Contacts

</div>

| Role | Name | Phone | Email | Notes |
| --- | --- | --- | --- | --- |
| Operations | Smith, Jordan | +1 (260) 555-0101 | jordan.smith@customer.com | Day shift lead; approves downtime windows |
| Maintenance | Lee, Morgan | +1 (260) 555-0123 | lee.morgan@customer.com |  |
| IT | Patel, Asha | +1 (260) 555-0199 | asha.patel@customer.com | VLANs, firewall rules, remote access |
| Safety | Garcia, Luis | +1 (260) 555-0177 | luis.garcia@customer.com |  |

<div style="background-color: darkred; padding: 2px; border-radius: 5px;">

#### 1.3.2 Integrator Contacts

</div>

| Role | Name | Phone | Email | Notes |
| --- | --- | --- | --- | --- |
| Project Manager | Taylor, Alex | +1 (260) 555-0144 | alex.taylor@integrator.com | Primary PM contact for scheduling and changes |
| Controls Lead | Jordan, Casey | +1 (260) 555-0166 | casey.jordan@integrator.com | Don't talk to, spooks easily. |
| Robotics Lead | Davis, Riley | +1 (260) 555-0188 | riley.davis@robots.com | Sometimes barks like a dog, but for real. |
| Mechanical Lead | Morgan, Jamie | +1 (260) 555-0155 | jamie.morgan@hammer.com | Loves to talk about wrenches. |
| Electrical Lead | Carter, Taylor | +1 (260) 555-0133 | taylor.cater@zappy.com | Always shocked to hear from you. |
| Pneumatics Lead | Jordan, Avery | +1 (260) 555-0111 | avery.jordan@hiss.com | Hisses when stressed. |

<div style="background-color: darkred; padding: 2px; border-radius: 5px;">

#### 1.3.3 Misc Contacts

</div>

> Note💡 Include vendors, integrators, etc. for interlocks or job specific needs.

| Role | Name | Phone | Email | Notes |
| --- | --- | --- | --- | --- |
| Safety Standards Consultant | Nguyen, Kim | +1 (260) 555-0198 | kim.nguyen@safe.com | Helps with safety standards interpretation. |

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 2) Customer software standards & templates (End-customer specifications)

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 2.1 Customer standards

</div>

- Customer blockpoint received: ☑
- Customer naming convention received: ☑
- Customer alarm / factory information philosophy received: ☑
- Customer programming standard received: ☑
- Customer HMI standards received: ☑
- Customer network / cybersecurity standard received: ☑
- Customer plc->plc interlocking standards received: ☑

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 2.2 Customer-provided templates (paths)

</div>

- Design documentation: [Design Document](https://duckduckgo.com/?q=design+document&atb=v510-1&ia=web)
- Blockpoint Schedule: [Blockpoint Document](https://duckduckgo.com/?q=blockpoint+document&atb=v510-1&ia=web)
- Template PLC code: [Template PLC Project](https://duckduckgo.com/?q=template+plc+document&atb=v510-1&ia=web)
- Template HMI project: [Template HMI Project](https://duckduckgo.com/?q=template+hmi+document&atb=v510-1&ia=web)
- Template drive configuration files: [Drive Config Files](https://duckduckgo.com/?q=template+drive+document&atb=v510-1&ia=web)
- Other templates:
	- [Network Diagram Template](https://duckduckgo.com/?q=network+diagram+document&atb=v510-1&ia=web)

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 2.3 Template gaps / deviations

</div>

- Deviations required: ☐
- Deviation details: 
- Customer approval required: ☐
- Who/when: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 3) Blockpoint specifications (software, hardware, firmware revisions)

</div>

> Goal: lock the “known-good” baseline for PLCs, HMIs, drives, and key components.

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.1 PLC baseline

</div>

| Item | Manufacturer | Model | Hardware Rev | Firmware Rev | Software / IDE Version | Options / Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Primary PLC | ExamplePLCCo | ExPLC-1000 | A | 1.0.0 | v1.00.00 | Base model with standard I/O |
| Safety PLC | SafePLCInc | SafePLC-2000 | B | 2.1.0 | v2.00.00 | Includes safety I/O modules |
| Remote I/O | RemoteIOLtd | RemIO-500 | C | 3.2.1 | v3.00.00 | Distributed I/O modules |
| Comm Module | CommModulesInc | CommMod-300 | D | 4.0.0 | v4.00.00 | Ethernet communication module |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.2 HMI / SCADA baseline

</div>

| Item | Platform | Model / Runtime | Hardware Rev | Firmware Rev | Dev Software Version | Runtime Version | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HMI Panel | ExampleHMIOS | ExHMI-1500 / v5.0 | E | 5.1.0 | v5.00.00 | v5.0 | 15-inch touchscreen panel |
| SCADA Server | ExampleSCADAOS | ExSCADA-Server / v10.0 | F | 10.2.0 | v10.00.00 | v10.0 | Central SCADA server |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.3 Drives baseline

</div>

| Item | Manufacturer | Model | Frame / HP | Firmware Rev | Config Tool Version | Config File Name/ID | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Main Drive | DriveMakersCo | DriveX-4000 |  | 6.0.0 |  |  |  |
| Auxiliary Drive | SpeedyDrivesInc | SpeedDrive-2500 |  | 7.1.0 |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.4 Robots baseline

</div>

| Item | Manufacturer | Model | Hardware Rev | Firmware Rev | Software / IDE Version | Options / Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Articulated Robot | RoboMation | RoboArt-6Axis | I | 8.0.0 |  | 6-axis robot for assembly tasks |
| SCARA Robot | FastBots | FastSCARA-300 | J | 9.1.0 |  | SCARA robot for pick-and-place operations |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.5 Vision baseline

</div>

| Item | Manufacturer | Model | Hardware Rev | Firmware Rev | Software / Runtime Version | Config / Project File Name/ID | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Vision System | VisionTech | VisionSys-1000 | K | 1.0.0 |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.6 Other critical baselines (as applicable)

</div>

- Motion / servos: 
- Barcode / RFID: 
- Safety devices (relays, scanners): 
- Other: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 3.7 Baseline verification

</div>

- Baselines match purchased hardware BOM: ☐
- Baselines match plant standards: ☐
- Any mismatches documented & approved: ☐

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 4) Hardware drawings & documents received (and dates)

</div>

> Record exactly what drawings were received and which revisions were used.

| Document | Rev | Date Received | Source | Used For | Notes |
| --- | --- | --- | --- | --- | --- |

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 5) Hardware span of controls (operational equipment scope)

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 5.1 Control architecture summary

</div>

- PLC count: 
- Remote I/O count: 
- HMI/SCADA nodes: 
- Networks: []
- Time sync method: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 5.2 Equipment span table

</div>

| Equipment / Area | Control Owner (PLC/Panel) | Local Controls (PBs, selectors) | Sensors / Actuators Summary | Special Notes |
| --- | --- | --- | --- | --- |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 5.3 IO summary (approx.)

</div>

- DI:   DO:   AI:   AO: 
- Specialty IO: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 5.4 Field device assumptions

</div>

- Sensor types / ranges: 
- Valve types / fail positions: 
- Motor starters / VFD control method: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 6) Safety span of controls (system-wide)

</div>

> This section should align with the project’s risk assessment / safety requirement specification.

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 6.1 Safety basis

</div>

- Safety documentation reference(s): 
- Target standard(s) / approach: 
- Required Performance Level / SIL targets: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 6.2 Safety architecture

</div>

- Safety controller(s) / relay(s): 
- Safety networks (if any): 
- Safety zones / boundaries: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 6.3 Safety devices inventory

</div>

| Device Type | Location / Zone | Tag / ID | Reset Method | Notes |
| --- | --- | --- | --- | --- |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 6.4 Safety functions list (high-level)

</div>

| Safety Function ID | Description | Inputs | Outputs | PL/SIL Target | Validation Method |
| --- | --- | --- | --- | --- | --- |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 6.5 Safety validation & documentation

</div>

- Safety IO checkout plan defined: ☐
- Safety function test procedure defined: ☐
- Safety acceptance criteria defined: ☐
- Safety validation results captured and archived: ☐

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 7) Interlock specifications & details

</div>

> Capture all process, equipment, and safety-related interlocks. This becomes your implementation and test source-of-truth.

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 7.1 Interlock philosophy

</div>

- Interlock types used: []
- Bypass policy: 
- Reset philosophy: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 7.2 Interlock matrix (summary)

</div>

| Interlock ID | Applies To | Condition / Inputs | Action / Outputs | Reset Requirement | Bypass Allowed | HMI Indication | Test / Verification |
| --- | --- | --- | --- | --- | --- | --- | --- |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 7.3 Interlock implementation notes

</div>

- Standard pattern used: 
- Where interlocks are enforced: 
- Latched vs non-latched criteria: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 8) Controls software design (PLC)

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 8.1 Project structure

</div>

- Program organization: 
- AOI/FB strategy: 
- Data structures naming/versioning: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 8.2 Tagging & naming

</div>

- Naming convention reference: 
- IO naming mapping strategy: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 8.3 State models & sequencing

</div>

- Modes supported: []
- Sequence description / reference: 
- Fault handling strategy: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 8.4 Diagnostics & maintainability

</div>

- Standard device diagnostics implemented: ☐
- Clear fault text and corrective actions defined: ☐
- First-out / root-cause capture: ☐

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 8.5 Simulation / offline testing

</div>

- Simulation approach: 
- Sim boundaries & assumptions: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 9) HMI / SCADA design

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 9.1 HMI scope

</div>

- Screen list / navigation map reference: 
- User roles / security levels: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 9.2 Standards

</div>

- Alarm colors conform: ☐
- Faceplates/objects conform: ☐
- Units/ranges/scaling defined: ☐

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 9.3 Alarm management

</div>

- Alarm philosophy reference: 
- Alarm priorities defined: ☐
- Shelving/suppression requirements: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 9.4 Data logging / historian (if applicable)

</div>

- Tags to log + rates: 
- Batch/lot/traceability requirements: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 10) Drive configuration & integration

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 10.1 Control method

</div>

- Hardwired IO control: ☐
- Fieldbus control: ☐
- Safety integration details: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 10.2 Standard parameters

</div>

- Speed/accel/decel/torque limits: 
- Motor nameplate data source: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 10.3 Config management

</div>

- Config file naming convention: 
- Storage / version control location: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 11) Communications, networking, and cybersecurity

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 11.1 Network inventory

</div>

| Network | Subnet/VLAN | Devices | Managed By | Notes |
| --- | --- | --- | --- | --- |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 11.2 IP addressing & naming

</div>

- IP plan reference: 
- Hostname/device name plan: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 11.3 Cybersecurity baseline (project-appropriate)

</div>

- Accounts/roles defined: ☐
- Backup/restore procedure defined: ☐
- Remote access method approved: ☐
- Antivirus/whitelisting aligned: ☐

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 12) Timeline & milestones (planned vs actual)

</div>

| Milestone | Planned Date | Actual Date | Owner | Notes / Blockers |
| --- | --- | --- | --- | --- |

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 13) Testing, FAT/SAT, and acceptance criteria

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 13.1 Test scope & strategy

</div>

- IO checkout plan reference: 
- Interlock test procedure reference: 
- Sequence / recipe test plan reference: 

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 13.2 Acceptance criteria

</div>

- Customer acceptance criteria document: 
- Punchlist closure criteria: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 14) Deliverables, backups, and handover

</div>

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 14.1 Deliverables

</div>

- PLC source + compiled artifact: ☐
- HMI/SCADA source + runtime package: ☐
- Drive configuration backups: ☐
- Network/IP plan: ☐
- Operator/maintenance documentation: ☐
- As-built drawings (or redlines): ☐

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 14.2 Backup & restore

</div>

- Backup location: 
- Restore validation performed: ☐
- Notes: 

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 15) Open items / risks / decisions

</div>

| Item | Owner | Due Date | Risk Level (L/M/H) | Mitigation / Notes |
| --- | --- | --- | --- | --- |

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 16) Approvals / Sign-off

</div>

- Pre-Design: Before development begins, this document has been filled to satisfy internal quality control members to continue with design.
- Functional Design Check: Midway check to verify development is progressing in the correct direction. This is performed before customers get any design documentations.
- Post Desgin Check: Final off-site check to validate the structure of the software matches what is expetected by this documentation, internal QC engineers, and the customer.
- Integration Motion and Safety Check: Integration of controls equipment successful. This check occurs before automatic motion occurs in a system.
- Site Acceptance (optional): If the system is built on the floor of an integrator to test before shipping to production facilities, this check is to ensure the integrating mechanical company is satisfied with the equipment.
- Factory Acceptance: The final system check. All previous checks complete, system ready for purchase by customer. All issues closed and ready to sell.

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 16.1 Pre-Design

</div>

| Role | Name | Date | Signature / Initials |
| --- | --- | --- | --- |
| Controls Lead |  |  |  |
| Project Manager |  |  |  |
| Safety (optional) |  |  |  |
| Customer Representative (optional) |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 16.2 Functional Design Check (50%)

</div>

| Role | Name | Date | Signature / Initials |
| --- | --- | --- | --- |
| Controls Lead |  |  |  |
| Project Manager |  |  |  |
| Safety (optional) |  |  |  |
| Customer Representative (optional) |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 16.3 Post Design Check (90%)

</div>

| Role | Name | Date | Signature / Initials |
| --- | --- | --- | --- |
| Controls Lead |  |  |  |
| Project Manager |  |  |  |
| Safety (optional) |  |  |  |
| Customer Representative (optional) |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 16.4 Integration Motion and Safety Check

</div>

| Role | Name | Date | Signature / Initials |
| --- | --- | --- | --- |
| Controls Lead |  |  |  |
| Project Manager |  |  |  |
| Safety (optional) |  |  |  |
| Customer Representative (optional) |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 16.5 Site Acceptance (optional)

</div>

| Role | Name | Date | Signature / Initials |
| --- | --- | --- | --- |
| Controls Lead |  |  |  |
| Project Manager |  |  |  |
| Safety (optional) |  |  |  |
| Customer Representative (optional) |  |  |  |

<div style="background-color: darkgreen; padding: 2px; border-radius: 5px;">

### 16.6 Factory Acceptance

</div>

| Role | Name | Date | Signature / Initials |
| --- | --- | --- | --- |
| Controls Lead |  |  |  |
| Project Manager |  |  |  |
| Safety (optional) |  |  |  |
| Customer Representative (optional) |  |  |  |

---

<div style="background-color: darkblue; padding: 2px; border-radius: 5px;">

## 17) Appendix (links / references)

</div>

- Customer standards: 
- Drawings folder: 
- Code repository / tag: 
- FAT/SAT reports: 