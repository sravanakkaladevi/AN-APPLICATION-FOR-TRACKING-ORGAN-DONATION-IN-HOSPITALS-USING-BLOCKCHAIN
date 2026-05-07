# Database Schema Documentation

This folder contains the database schema for the **Organ Donation Tracking System** project. 
The schema uses MySQL as the backend.

## Schema File
- `schema.sql`: Contains the raw Data Definition Language (DDL) queries used to create the tables, relationships, and constraints in the MySQL database.

## Entity-Relationship (ER) Diagram
Below is an overview of the core entities and their relationships.

```mermaid
erDiagram
    USER ||--o| DONOR_PROFILE : "1:1"
    USER ||--o| HOSPITAL_PROFILE : "1:1"
    USER ||--o{ FEEDBACK : "1:N"
    DONOR_PROFILE ||--o{ ORGAN_RECORD : "1:N"
    DONOR_PROFILE ||--o{ DEATH_CERTIFICATE : "1:N"
    HOSPITAL_PROFILE ||--o{ ORGAN_RECORD : "registers (1:N)"
    HOSPITAL_PROFILE ||--o{ ORGAN_RECORD : "receives (1:N)"
    HOSPITAL_PROFILE ||--o{ DEATH_CERTIFICATE : "issues (1:N)"

    USER {
        int id PK
        string username
        string email
        boolean is_donor
        boolean is_hospital
    }
    DONOR_PROFILE {
        int user_id PK, FK
        string blood_group
        string gender
        boolean is_deceased
    }
    HOSPITAL_PROFILE {
        int user_id PK, FK
        string hospital_name
        string registration_number
    }
    ORGAN_RECORD {
        int id PK
        int blockchain_id
        string organ_type
        string status
        int donor_id FK
    }
    DEATH_CERTIFICATE {
        int id PK
        string certificate_number
        date date_of_death
    }
    FEEDBACK {
        int id PK
        string subject
        int rating
    }
```
