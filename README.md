# Sports Logistics Management System

## Project Overview
This is a Django-based Sports Logistics Management System designed to streamline the booking and management of sports facilities for both students and staff. It provides robust authentication, facility management, and a comprehensive booking system with email notifications.

## Features

### User Authentication and Profiles
*   **User Roles:** Supports three distinct user roles:
    *   `Student`: Can register, log in, view available facilities, book slots, and manage their own bookings.
    *   `Staff`: Can register, log in, add new facilities, block time slots, manage all bookings (approve, deny, update, cancel), and view staff-specific dashboards.
    *   `Admin`: (Implied by Django Admin) Full control over all data and users.
*   **OTP-based Signup:** New users register by requesting an OTP (One-Time Password) sent to their email for verification.
*   **Secure Login:** Uses JWT (JSON Web Tokens) with HTTP-only cookies for secure authentication.
*   **User Profiles:** Dedicated profile views for students (showing their bookings) and staff (showing blocked slots).

### Facility Management
*   **Add Facilities:** Staff users can add new sports facilities to the system.
*   **View Facilities:** All users can view a list of available facilities.


### Booking System
*   **Calendar View:** Students can view a 14-day calendar summary of facility availability (green for available, orange for moderately booked, red for heavily booked).
*   **Hourly Slot Availability:** Users can check detailed hourly availability for a specific facility on a given date.
*   **Student Bookings:** Students can book available time slots for facilities, with automatic conflict checking.
*   **Staff Blocking:** Staff can block specific time slots in facilities for maintenance, events, or other administrative purposes.
*   **Booking Management:** Staff can view, approve, deny, update, and cancel any booking made by students.
*   **Email Notifications:** Automated email confirmations for:
    *   Booking confirmation
    *   Booking cancellation (by student or staff)
    *   Booking updates

## Installation

To set up the project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Sports-Logistics-Management-System.git
    cd Sports-Logistics-Management-System
    ```
    *(Replace `your-username` with the actual GitHub username or repository URL)*

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create a Superuser (Admin):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

6.  **Configure Email Settings:**
    Open `sportmanage/settings.py` and update the email configuration for sending OTPs and booking notifications.
    ```python
    # ... existing code ...

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'YOUR_EMAIL_ADDRESS'  # e.g., 'youremail@gmail.com'
    EMAIL_HOST_PASSWORD = 'YOUR_APP_PASSWORD'  # Generate an App Password if using Gmail

    # ... existing code ...
    ```
    *   **Note for Gmail users:** You might need to generate an App Password from your Google Account security settings if you have 2-Step Verification enabled. Regular Gmail passwords won't work directly for SMTP.

## Running the Project

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The application will typically run on `http://127.0.0.1:8000/`.

## Usage

### Accessing the Application
Open your web browser and navigate to `http://127.0.0.1:8000/`.

### User Flow

1.  **Registration:**
    *   Click on the "Sign Up" or "Register" link.
    *   Provide your desired username, email, phone number, and age.
    *   An OTP will be sent to your registered email address.
    *   Enter the OTP to complete the registration.
    *   Your role (student or staff) will be automatically assigned based on your email address format (though this is a simplified logic, it can be customized).

2.  **Login:**
    *   Use your registered username and password to log in.
    *   Upon successful login, you will be redirected to your respective dashboard (Student Dashboard or Staff Dashboard).

3.  **Student Dashboard:**
    *   View available sports facilities.
    *   Check calendar status for facilities (shows overall availability for the next 14 days).
    *   View hourly slots for a specific facility on a chosen date.
    *   Book available time slots.
    *   View and cancel your own bookings.

4.  **Staff Dashboard:**
    *   View all facilities.
    *   Add new facilities.
    *   Block specific time slots in facilities (e.g., for maintenance).
    *   View and manage all bookings (approve, deny, update status, cancel).

### Core Functionalities (API Endpoints)

The application exposes various API endpoints for interaction, primarily used by the frontend:

*   **Authentication:**
    *   `/api/request-otp/` (POST): Request OTP for signup.
    *   `/api/verify-otp/` (POST): Verify OTP and create user.
    *   `/api/login/` (POST): User login (sets JWT cookies).
    *   `/api/logout/` (POST): User logout (clears JWT cookies).
    *   `/api/user-info/` (GET): Get authenticated user's details.

*   **Facility Operations:**
    *   `/api/facilities/` (GET): List all facilities.
    *   `/api/add-facility/` (POST): Staff only - Add a new facility.
    *   `/api/facilities/<int:facility_id>/edit/` (PUT/PATCH): Staff only - Edit a facility.
    *   `/api/facilities/<int:facility_id>/delete/` (DELETE): Staff only - Delete a facility.

*   **Booking Operations:**
    *   `/api/calendar-status/<int:facility_id>/` (GET): Get 14-day availability status for a facility.
    *   `/api/slots-for-day/<int:facility_id>/` (GET): Get hourly availability for a facility on a specific date.
    *   `/api/book-slot/` (POST): Student only - Book a time slot.
    *   `/api/block-slot/` (POST): Staff only - Block a time slot.
    *   `/api/bookings/` (GET): List all bookings (staff) or user's bookings (student).
    *   `/api/bookings/<int:pk>/` (GET, PUT, PATCH, DELETE): Retrieve, update, or delete a specific booking.
    *   `/api/cancel-booking/<int:booking_id>/` (POST): Cancel a booking.
    *   `/api/update-booking-status/<int:booking_id>/` (PUT): Staff only - Update booking status.
    *   `/api/all-facilities-calendar-status/` (GET): Calendar status for all facilities.

## Project Structure (High-Level)

*   `authenticate/`: Handles user authentication, registration, login, and user profile management.
    *   `models.py`: Defines the `CustomUser` model.
    *   `views.py`: Contains API views for authentication and user-specific logic.
    *   `templates/`: HTML templates for user-related pages (e.g., `index.html`, `student_profile.html`, `staff_profile.html`).
*   `booksystem/`: Manages sports facilities and the booking system.
    *   `models.py`: Defines `Facility` and `Booking` models.
    *   `views.py`: Contains API views for facility and booking operations.
    *   `serializers.py`: Defines serializers for API data.
    *   `templates/`: HTML templates for dashboards and email notifications.
        *   `email/`: Contains email templates for various notifications.
*   `sportmanage/`: The main Django project configuration.
    *   `settings.py`: Project settings, including database, installed apps, and email configurations.
    *   `urls.py`: Main URL routing for the project.
*   `manage.py`: Django's command-line utility for administrative tasks.
*   `requirements.txt`: Lists all Python dependencies. 