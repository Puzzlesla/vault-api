# Vault Secure – Notes API

Link: <https://myvaultsecure.up.railway.app>

Vault Secure is a containerized, full-stack backend application designed to securely manage encrypted user notes.

Built with FastAPI, PostgreSQL, Docker, and SQLAlchemy


### Features

**End-to-End Encryption:** Notes are stored as ciphertext in the database using Fernet (AES-256) symmetric encryption

**Robust Authentication:** Secure JWT-based authentication system for user registration, login and token verification

**Password Recovery Workflow:** Secure backend background tasks for automated password reset links using SMTP templates

**Containerized Infrastructure:** Fully Dockerized environment supporting reproducible builds and deployment.



### Tech Stack

**Framework:** FastAPI (Python)  
**Database:** PostgreSQL (Production) / SQLite (Testing)  
**ORM:** SQLAlchemy  
**Security & Auth:** PyJWT, Passlib (Bcrypt), Cryptography (Fernet)  
**Containerization:** Docker & Docker Compose


### Prerequisites

Docker and Docker Compose 
Python 3.10+

### Installation & Local Setup
1. Clone the repository:

    ```git clone https://github.com/Puzzlesla/vault-api.git```

    ```cd vault-api```

2. Create a `.env` file in the root directory based on your configuration requirements:

    See `.env.example` for required environmental variables

3. Build and spin up the containers using Docker Compose:
  `docker compose up --build

4. Running Tests
   
     Run
    
       pytest tests/ -v
   



