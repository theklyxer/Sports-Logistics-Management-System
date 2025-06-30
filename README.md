# Sports Logistics Management System

## Project Overview
This Django-based Sports Logistics Management System is a robust solution designed to efficiently manage and streamline the booking of sports facilities. It caters to the needs of educational institutions or sports complexes, enabling seamless interaction between students and staff for facility reservations and administrative oversight. The system ensures secure user authentication, provides intuitive facility management tools, and automates the booking process with real-time availability checks and email notifications.

## Features

### User Authentication and Profiles
*   **Comprehensive User Roles:** The system defines clear roles to manage access and functionalities:
    *   `Student`: Students can easily register, securely log in, browse available facilities, book time slots for their activities, and keep track of their personal booking history.
    *   `Staff`: Staff members are empowered to register, log in, add new sports facilities, designate blocked time slots for maintenance or events, and oversee all bookings (approving, denying, updating, and canceling as needed). They also have access to staff-specific dashboards for administrative tasks.
    *   `Admin`: (Managed via Django Admin Interface) Administrators possess full control over all system data, user accounts, and configurations, ensuring smooth operation and data integrity.
*   **Secure OTP-based Signup:** New users initiate registration by requesting a One-Time Password (OTP), which is sent to their email address for verification. This method enhances security and ensures legitimate user registration.
*   **JWT-powered Secure Login:** The system employs JSON Web Tokens (JWT) combined with HTTP-only cookies for secure and persistent user sessions, protecting sensitive authentication information.
*   **Personalized User Profiles:** Dedicated profile pages are available for each user type. Students can view their upcoming and past bookings, while staff can easily see the slots they have blocked.

### Facility Management
*   **Add New Facilities:** Staff users have the capability to easily add new sports facilities (e.g., basketball courts, swimming pools, gyms) to the system, making them available for booking.
*   **View Available Facilities:** All authenticated users can browse a comprehensive list of all sports facilities managed by the system.


### Dynamic Booking System
*   **Intuitive Calendar View:** Students can view a 14-day calendar displaying the general availability status of each facility. This visual guide uses a color-coded system: `green` for ample availability, `orange` for moderately booked periods, and `red` for heavily booked or unavailable times.
*   **Detailed Hourly Slot Availability:** Users can drill down to check the precise hourly availability for any specific facility on a chosen date, allowing for meticulous planning.
*   **Seamless Student Bookings:** Students can effortlessly book available time slots for their desired facilities. The system includes an automatic conflict-checking mechanism to prevent double-bookings.
*   **Staff Slot Blocking:** Staff can efficiently block specific time intervals in any facility. This feature is crucial for scheduling maintenance, organizing special events, or managing administrative closures, ensuring these times are not available for regular bookings.
*   **Comprehensive Booking Management:** Staff members have a centralized interface to view, approve, deny, update the status of, and cancel any booking made by students, providing complete administrative control over facility usage.
*   **Automated Email Notifications:** The system sends automated email alerts to users for various booking-related events, ensuring they are always informed:
    *   **Booking Confirmation:** Sent upon successful booking.
    *   **Booking Cancellation:** Notifies users if their booking is cancelled by either themselves or a staff member.
    *   **Booking Updates:** Informs users of any changes made to their existing bookings.

## Technologies Used
*   **Backend:** Python, Django 5.2.3
*   **API:** Django REST Framework
*   **Authentication:** Django REST Framework Simple JWT, PyJWT
*   **Database:** SQLite3 (default, configurable for others)
*   **CORS Management:** Django CORS Headers
*   **Email:** SMTP (e.g., Gmail SMTP)

## Installation

To set up the project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Sports-Logistics-Management-System.git
    cd Sports-Logistics-Management-System
    ```
    *(Replace `your-username` with the actual GitHub username or repository URL if different)*

2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Install all required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Database Migrations:**
    Set up the database schema by running migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a Superuser (Admin Account):**
    To access the Django admin panel and manage initial data, create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set up your administrator username, email, and password.

6.  **Configure Email Settings:**
    Email functionality is crucial for OTP-based signup and booking notifications. Open `sportmanage/settings.py` and update the email configuration with your SMTP details. For Gmail, you'll likely need an App Password.

    ```python
    # ... existing code ...

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'  # Or your SMTP server
    EMAIL_PORT = 587             # Or your SMTP port
    EMAIL_USE_TLS = True         # Use TLS for secure connection
    EMAIL_HOST_USER = 'YOUR_EMAIL_ADDRESS'  # e.g., 'youremail@gmail.com'
    EMAIL_HOST_PASSWORD = 'YOUR_APP_PASSWORD'  # Use an App Password for Gmail

    # ... existing code ...
    ```
    *   **Note for Gmail users:** If you have 2-Step Verification enabled on your Google Account, you *must* generate an "App password" and use that instead of your regular Gmail password. You can do this in your Google Account security settings.

## Running the Project

1.  **Start the Django development server:**
    Once all configurations are set, you can run the application:
    ```bash
    python manage.py runserver
    ```
    The application will typically be accessible in your web browser at `http://127.0.0.1:8000/`.

## Usage

### Accessing the Application
Open your preferred web browser and navigate to the application's URL: `http://127.0.0.1:8000/`.

### User Flow Walkthrough

1.  **Registration:**
    *   Click on the "Sign Up" or "Register" link on the homepage.
    *   Fill in the required details: a unique username, your email address, phone number, and age.
    *   An OTP will be immediately dispatched to your provided email address.
    *   Enter the received OTP in the designated field to finalize your registration.
    *   Based on a simplified logic (which can be customized in `authenticate/views.py`), your role (Student or Staff) will be automatically assigned based on your email address format.

2.  **Login:**
    *   Return to the login page and enter your registered username and password.
    *   Upon successful authentication, you will be automatically redirected to your role-specific dashboard (either the Student Dashboard or the Staff Dashboard).

3.  **Student Dashboard Features:**
    *   **Browse Facilities:** View a list of all sports facilities available for booking.
    *   **Check Calendar Status:** Get a quick overview of facility availability for the next two weeks via a color-coded calendar.
    *   **View Hourly Slots:** Select a facility and a date to see precise hourly availability, identifying open slots.
    *   **Book Time Slots:** Reserve an available time slot for your desired facility. The system will prevent conflicting bookings.
    *   **Manage My Bookings:** Review your current and past bookings, and cancel any that are no longer needed.

4.  **Staff Dashboard Features:**
    *   **Manage Facilities:** View, add, edit, and delete sports facilities as needed.
    *   **Block Time Slots:** Mark specific periods as unavailable for booking (e.g., for facility maintenance, special events, or staff-only use).
    *   **Oversee All Bookings:** Gain a comprehensive view of all bookings made across all facilities. Staff can approve, deny, modify the status of, or cancel any booking as required.

### Core Functionalities (Key API Endpoints)

The application leverages a set of well-defined API endpoints for its functionalities, facilitating interaction between the frontend and backend:

*   **Authentication & User Management:**
    *   `POST /api/request-otp/`: Initiates the signup process by sending an OTP to the user's email.
    *   `POST /api/verify-otp/`: Validates the OTP and completes the user registration, creating a new user account.
    *   `POST /api/login/`: Handles user login, setting secure JWT access and refresh tokens as HTTP-only cookies.
    *   `POST /api/logout/`: Clears the authentication cookies, effectively logging out the user.
    *   `GET /api/user-info/`: Retrieves details of the currently authenticated user, including their role.

*   **Facility Operations (Staff Access Primarily):**
    *   `GET /api/facilities/`: Fetches a list of all sports facilities available in the system.
    *   `POST /api/add-facility/`: Allows staff to add a new facility.
    *   `PUT/PATCH /api/facilities/<int:facility_id>/edit/`: Enables staff to update details of an existing facility.
    *   `DELETE /api/facilities/<int:facility_id>/delete/`: Permits staff to remove a facility from the system.

*   **Booking Operations:**
    *   `GET /api/calendar-status/<int:facility_id>/`: Provides a 14-day summary of booking density for a specific facility.
    *   `GET /api/slots-for-day/<int:facility_id>/`: Returns detailed hourly availability for a facility on a given date.
    *   `POST /api/book-slot/`: Allows students to book an available time slot.
    *   `POST /api/block-slot/`: Allows staff to block time slots for administrative purposes.
    *   `GET /api/bookings/`: Lists all bookings (for staff) or the current user's bookings (for students).
    *   `GET, PUT, PATCH, DELETE /api/bookings/<int:pk>/`: Enables retrieval, modification, or deletion of a specific booking.
    *   `POST /api/cancel-booking/<int:booking_id>/`: Initiates the cancellation of a booking.
    *   `PUT /api/update-booking-status/<int:booking_id>/`: Allows staff to change the status of a booking (e.g., approve, deny).
    *   `GET /api/all-facilities-calendar-status/`: Provides a calendar overview of availability across all facilities.

## Project Structure (High-Level)

*   `authenticate/`: This Django app manages all aspects of user authentication and profiles.
    *   `models.py`: Defines the `CustomUser` model, extending Django's default user model with additional fields like phone, age, and role.
    *   `views.py`: Contains the API views that handle user registration (including OTP logic), login, logout, and user profile information retrieval.
    *   `templates/`: Stores HTML templates related to user interactions, such as the homepage (`index.html`), student profile, and staff profile pages.
*   `booksystem/`: This Django app is responsible for managing sports facilities and the core booking functionalities.
    *   `models.py`: Defines the `Facility` model (for sports facilities) and the `Booking` model (for reservations), detailing their attributes and relationships.
    *   `views.py`: Implements the API views for creating, retrieving, updating, and deleting facilities and bookings. It also includes logic for availability checks and staff-specific booking management.
    *   `serializers.py`: Defines how Django models are converted into JSON format for API responses and vice-versa, ensuring data consistency.
    *   `templates/`: Contains HTML templates for dashboards (`student_dashboard.html`, `staff_dashboard.html`) and, crucially, a dedicated `email/` sub-directory for email notification templates (e.g., `booking_confirmation.html`).
*   `sportmanage/`: This is the main Django project directory, containing global configurations.
    *   `settings.py`: The central configuration file for the entire Django project, including database settings, installed applications, middleware, and email server configurations.
    *   `urls.py`: The root URL routing file that dispatches requests to the appropriate Django apps.
*   `manage.py`: A command-line utility provided by Django for performing administrative tasks such as running the development server, making migrations, and creating superusers.
*   `requirements.txt`: A plain text file listing all Python package dependencies required to run the project, enabling easy environment setup.

