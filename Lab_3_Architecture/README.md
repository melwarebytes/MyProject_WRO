# Lab 3: Component Modelling and Architectural Pattern Selection

Merull Shah, PES1UG24CS270, Section E. Scenario: Self-Service Coffee Kiosk.

| File | What it is |
|---|---|
| `Component_Diagram_Coffee_Kiosk.pdf` / `.png` | UML component diagram |
| `Lab3_Architecture_Justification.docx` / `.pdf` | One-page written justification |
| `Lab_3_Handout.pdf` | Lab handout |

## Summary

**Architecture:** layered. Presentation (Touch Screen UI), business logic (Order Manager, Payment Service, Receipt Service) and data (Menu & Pricing Repository), plus two hardware devices (card reader, receipt printer).

**Interfaces** (ball = provided, socket = required, joined by assembly connectors):

| Interface | Provided by | Required by | Technology |
|---|---|---|---|
| IOrder | Order Manager | Touch Screen UI | API calls |
| IPayment | Payment Service | Order Manager | API call |
| IReceipt | Receipt Service | Order Manager | API call |
| IMenu | Menu & Pricing Repository | Order Manager | database queries (SQL) |
| ICardTerminal | Card Reader | Payment Service | hardware: EMV over USB |
| IPrinter | Receipt Printer | Receipt Service | hardware: ESC/POS over USB |
