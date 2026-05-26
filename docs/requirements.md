# Requirements Specification: User Service

This document aggregates the Functional Requirements (FR) and Non-Functional Requirements (NFR) governing the E-Learning platform ecosystem, with an explicit architectural focus on the **User Service** boundary.

---

## 1. Functional Requirements (FR)

### 1.1. Core Service Domain (Identity & Users)
These requirements are directly handled, executed, and owned by the User Microservice.

| ID | As a... | I want to... | So that... |
| :--- | :--- | :--- | :--- |
| **FR-1.1** | Unregistered user | Create an account using email and password | I can access the platform. |
| **FR-1.2** | Registered user | Log in and receive a secure JWT token | I can access protected resources securely. |
| **FR-1.3** | Registered user | View and update my personal profile data | My information stays up to date. |
| **FR-1.4** | Administrator | Manage (lock, unlock, de-authenticate) user accounts | I can control platform access and maintain security. |

### 1.2. External Domains (Ecosystem Integration Scope)
These operations are executed by sister microservices but rely on the User Service for identity verification, claims propagation, or event triggers.

#### Courses & Content (Course/Content Services)
* **FR-2.1:** As an instructor, I want to create a course with modules and lessons, so that students can learn structured content.
* **FR-2.2:** As an instructor, I want to upload learning materials (video, files, links), so that students can access content.
* **FR-2.3:** As a user, I want to browse available courses, so that I can select what to learn.
* **FR-2.4:** As a user, I want to view detailed course information, so that I can decide whether to enroll.

#### Progress Tracking (Progress Service)
* **FR-3.1:** As a student, I want the system to track my lesson completion, so that I can monitor my progress.
* **FR-3.2:** As a student, I want to see my course progress percentage, so that I know how much I completed.
* **FR-3.3:** As a student, I want my progress to be updated automatically upon lesson completion, so that my status is always accurate.

#### Certificates & Verification (Certification Service)
* **FR-4.1:** As a student, I want to receive a digital certificate upon 100% course completion, so that I have proof of my achievement.
* **FR-4.2:** As a student, I want my certificate to include a unique verification ID, so that its authenticity can be officially confirmed.
* **FR-4.3:** As a third party, I want to verify a certificate's validity by its unique ID, so that I can ensure the document is legitimate.

#### Payments (Payment Service)
* **FR-5.1:** As a user, I want to pay for a course online, so that I can access premium content.
* **FR-5.2:** As a student, I want to receive immediate access to a course after successful payment, so that I can start learning without delay.
* **FR-5.3:** As a user, I want to view my payment history, so that I can track transactions.

#### Notifications (Notification Service)
* **FR-6.1:** As a user, I want to receive notifications after successful enrollment (triggered asynchronously by user events).
* **FR-6.2:** As a student, I want to receive reminders about unfinished lessons.
* **FR-6.3:** As a user, I want to receive quiz result notifications.

---

## 2. Non-Functional Requirements (NFR)

These quality attributes define system constraints, performance characteristics, and architectural paradigms enforced within the platform.

### 2.1. Performance Efficiency
* **NFR-P1:** Respond to API requests within 1 second under normal load (up to 200 concurrent users).
* **NFR-P2:** Lesson progress updates must be reflected within 5 seconds after completion.
* **NFR-P3:** Certificate generation must be completed within 5 minutes.

### 2.2. Scalability & Capacity
* **NFR-SC1:** Support horizontal scaling using Docker-based container replication.
* **NFR-SC2:** Handle a 3x sudden increase in baseline user traffic without requiring structural architectural architectural updates.
* **NFR-SC3:** Microservices must be independently scalable based on localized load characteristics.

### 2.3. Reliability & Fault Tolerance
* **NFR-R1:** Enrollment and payment operations must be strictly atomic.
* **NFR-R2:** Guarantee a Recovery Point Objective (RPO) of 0 minutes for financial transactions and less than 5 minutes for user progress/state data.
* **NFR-R3:** The system must ensure a Recovery Time Objective (RTO) of less than 1 hour in case of a critical service or database crash.
* **NFR-R4 / NFR-D3:** Ensure "at-least-once" delivery for critical domain events during inter-service communication via broker publisher confirmations.
* **NFR-R5:** The system must remain partially operational if a non-critical component fails (graceful degradation).

### 2.4. Security, Confidentiality & Integrity
* **NFR-S1:** All non-public API endpoints must require secure, industry-standard token-based authentication (OAuth2 with JWT Bearer).
* **NFR-S2:** Enforce Role-Based Access Control (RBAC) supporting explicit assignments for `Student`, `Instructor`, and `Admin`.
* **NFR-S3:** User credentials must be stored using a strong, salted cryptographic hashing algorithm (`bcrypt`) resistant to brute-force and rainbow table attacks.
* **NFR-S4:** Sensitive data (passwords, raw payment instrumentation) must be strictly hidden or masked in logging outputs and API responses.

### 2.5. Maintainability, Modularity & Observability
* **NFR-M1:** Follow a rigid layered architecture design pattern within the service internals (Controller $\rightarrow$ Service $\rightarrow$ Domain/Repository $\rightarrow$ Infrastructure).
* **NFR-M2:** Microservices must be independently deployable, testable, and maintainable.
* **NFR-M3:** Rigid separation of concerns; zero core business or database persistence logic allowed within the routing controller layer.
* **NFR-O1:** Expose a standardized `/health` liveness/readiness endpoint for infrastructure monitoring.
* **NFR-O2:** Implement structured logging format for all incoming requests capturing HTTP status, latency, errors, and runtime metadata.
* **NFR-O3:** Collect operational telemetry metrics (request rates, error rates, core transaction rates).
* **NFR-O4:** Enable Distributed Tracing (via OpenTelemetry and Jaeger) to trace critical business lifecycles and transactions across isolated service boundaries using contextual trace propagation.

### 2.6. Portability & Deployability
* **NFR-D1:** Application components must be platform-independent and fully support containerized native execution environments (Docker, Kubernetes).
* **NFR-D2:** The infrastructure must support zero-downtime deployment capabilities (rolling updates) for individual architectural components.
* **NFR-D4:** The database architecture must ensure low logical coupling between separate functional sub-domains, strictly favoring a database-per-service pattern.