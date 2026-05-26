# Behaviors of the Component: User Service

This document defines the generic business operations (behaviors) exposed and handled by the User Microservice within the E-Learning platform.

---

## 1. Synchronous Operations

These are direct, request-response operations invoked by end-users or administrators via the API Gateway.

### 1.1. Register New User Account

| Attribute | Description |
| :--- | :--- |
| **Description** | Creates a unique platform account for a guest user using an email and password. |
| **Actor** | End User (via API Gateway). |

#### Behavior
Validates incoming payload syntax using Pydantic schemas to ensure data integrity. Queries the database to prevent duplicate registration of the same email address. If the email is unique, it applies a strong, salted cryptographic hashing algorithm (`bcrypt`) to the raw password to resist brute-force attacks. Finally, it fetches the default `'Student'` role identifier and atomically commits a new row to the `users` table along with a paired empty record in the `profiles` table within a single database transaction.

---

### 1.2. Authenticate User and Issue JWT

| Attribute | Description |
| :--- | :--- |
| **Description** | Verifies user credentials and generates secure, short-lived tokens for protected resource access. |
| **Actor** | End User (via API Gateway). |

#### Behavior
Performs a user lookup in the PostgreSQL database using the provided email address. If the user is found, it evaluates the account status flag (`is_active`); if it is set to `false`, the system immediately aborts and returns a `403 Forbidden` error. If the account is active, it cryptographically matches the plaintext password with the stored hash using the hashing utility. Upon successful authentication, it packages the unique `user_id` and the assigned `Role` (enforcing Role-Based Access Control — RBAC) into a signed, stateless JWT Access Token alongside a corresponding Refresh Token.

---

### 1.3. Update Personal Profile Data

| Attribute | Description |
| :--- | :--- |
| **Description** | Allows an authenticated user to modify their personal details like name, bio, or avatar. |
| **Actor** | End User (via API Gateway). |

#### Behavior
Extracts and validates the authenticated user's context (`user_id`) directly from the incoming JWT bearer token claims via security dependencies. It executes an asynchronous update query using SQLAlchemy 2.0 against the `profiles` table for rows linked to that verified identifier. It mutates the specified profile attributes (e.g., `full_name`, `bio`, `avatar_url`), updates the automatic tracking timestamps (`updated_at`), commits the changes to the database, and returns the updated profile object.

---

### 1.4. Administrative Account Lockout (Ban)

| Attribute | Description |
| :--- | :--- |
| **Description** | Enforces strict platform access control by allowing administrators to deactivate malicious or inactive accounts. |
| **Actor** | Admin (via API Gateway). |

#### Behavior
Evaluates the client token claims to ensure the caller possesses the explicit `'Admin'` role assignment (RBAC enforcement guard). If verified, it fetches the targeted user entity by its unique ID from the database and mutates the `is_active` state attribute to `False`. The transaction is committed to the database, instantly invalidating the account and preventing any subsequent successful logins or protected resource requests for that specific account.

---

## 2. Asynchronous Operations

This section describes the reactive behavior of the microservice, which ensures synchronization of user state with other platform subsystems without blocking the main transactional cycle.

### 2.1. Event-Driven User Provisioning

| Attribute | Description |
| :--- | :--- |
| **Description** | Facilitates the automatic granting of access rights and the creation of a working environment for a new user within the platform ecosystem. |
| **Trigger** | Successful database commit of a new user record in the `users` table. |

#### Behavior
Upon successfully committing the new account creation transaction, the service automatically generates and emits a domain registration event (`UserRegistered`) via the message broker client. This decoupled message allows the broader platform ecosystem to perform a sequence of business operations asynchronously without introducing latency to the registration response:

1. **Onboarding Communication:** Dispatching a welcome email with personalized onboarding instructions to the user's inbox (handled by the *Notification Service*).
2. **Resource Allocation:** Automatic provisioning of initial resources and workspace configurations based on the assigned system role, separating paths for a *Student* or an *Instructor* (handled by the *Course/Content Services*).

This event-driven approach ensures high system responsiveness to user registration, isolates system failures, and guarantees the atomic delivery of essential integration data (`user_id`, `email`, `role`) to all relevant platform modules, ensuring robust eventual consistency.