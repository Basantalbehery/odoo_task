# Porcelia Equipment Loan (`porcelia_equipment_loan`)

![Odoo Version](https://img.shields.io/badge/Odoo-19.0-purple.svg)
![License](https://img.shields.io/badge/License-LGPL--3-blue.svg)

## Overview

**Porcelia Equipment Loan** is a full-featured Odoo 19 module designed to manage equipment inventory, track loan requests, calculate late penalties, and streamline equipment returns via an interactive wizard. Built with strict record-level security, automated background tasks (Cron), comprehensive unit tests, and custom OWL JavaScript components.

---

## Key Features

- **Equipment & Category Management**:
  - Categorize equipment items with custom daily rental rates and condition scores (0–100%).
  - Integrated condition gauge and condition tracking.

- **Loan Lifecycle Workflow**:
  - Complete state transitions: `Draft` $\rightarrow$ `Confirmed` $\rightarrow$ `Returned` / `Cancelled`.
  - Automated reference sequence generation (`LOAN/YYYY/XXXXX`).

- **Overlap Validation**:
  - Python model constraints to prevent double-booking or scheduling conflicting loan periods for the same equipment item.

- **Return Wizard**:
  - Dedicated `equipment.loan.return.wizard` to handle equipment returns.
  - Automatically computes late return days (`days_late`) and total late penalties (`penalty_amount`).
  - Allows updating equipment condition scores upon return.

- **Automated Cron Job**:
  - Daily automated scheduled action (`ir.cron`) to evaluate active loans, mark overdue statuses, and recompute penalty balances.

- **Security & Access Control**:
  - **Equipment User**: Can view and manage only their own loans where `borrower_id == user`.
  - **Equipment Manager**: Has full administrative access to all equipment, categories, wizard actions, and system configurations.

- **Reporting & UI Widgets**:
  - PDF Loan Receipts and summary reports for borrowers.
  - Kanban, Pivot, and Graph dashboard views.
  - Custom OWL Systray notification counter for tracking overdue loans in real-time.

---

## Module Structure

```text
porcelia_equipment_loan/
├── models/
│   ├── equipment_category.py
│   ├── equipment_item.py
│   ├── equipment_loan.py
│   └── res_users.py
├── wizard/
│   ├── equipment_loan_return_wizard.py
│   └── equipment_loan_return_wizard_views.xml
├── views/
│   ├── equipment_category_views.xml
│   ├── equipment_item_views.xml
│   ├── equipment_loan_views.xml
│   ├── equipment_dashboard_views.xml
│   ├── res_users_views.xml
│   └── menus.xml
├── security/
│   ├── equipment_groups.xml
│   └── ir.model.access.csv
├── data/
│   ├── sequence_data.xml
│   ├── equipment_loan_cron.xml
│   └── demo_data.xml
├── report/
│   └── equipment_loan_report.xml
├── static/src/components/
│   ├── condition_gauge/
│   ├── dashboard/
│   └── overdue_systray/
├── tests/
│   ├── __init__.py
│   └── test_equipment_loan.py
├── __manifest__.py
└── README.md


## Screenshots
static/description