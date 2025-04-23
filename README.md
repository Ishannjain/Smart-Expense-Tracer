
# BudgetWise

BudgetWise is a personal finance web application built with Django that allows users to track their income, expenses, and budgets. The application is designed to be user-friendly while providing powerful features such as monthly/annual financial summaries, category-based budget tracking, and dynamic filters for viewing records.

## Distinctiveness and Complexity

This project is distinct in the following ways:
- It provides an integrated dashboard that displays real-time budget health and financial summaries per user.
- It includes pagination, filtering, and querying features across all core modules: income, expense, and budgets.
- The budget system supports dynamic alerts when a budget is low (below 25%) or exhausted.
- User authentication is implemented to allow personal tracking of data.
- CRUD operations are implemented for all core models: Income, Expense, Category, and Budget.
- Data visualization and organization make it intuitive for users to interpret financial health over different periods.

The complexity lies in the business logic handling financial summaries, budget tracking based on start dates, and category-specific aggregation of expenses. Additionally, query filtering (search, date ranges) across multiple views adds to the application’s interactivity and robustness.

## File Descriptions

- `views.py`: Contains all view logic including authentication, dashboard summaries, CRUD operations for income, expenses, categories, and budgets.
- `models.py`: Defines the database schema for Income, Expense, Category, and Budget models.
- `urls.py`: Maps URL paths to views.
- `templates/record/`: Contains all HTML templates for the views.
- `requirements.txt`: Lists Python packages required to run the application.
- `admin.py`: Registers models for Django admin interface.

## How to Run the Application

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ishannjain/BudgetWise.git
   cd BudgetBuddy
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Open the browser and go to** `http://127.0.0.1:8000/`

## Additional Information

- Authentication features include login, logout, and user registration.
- Each user’s financial data is securely stored and separated from other users.
- The dashboard provides monthly and yearly insights, and budget alerts notify when spending nears limits.
- The system also supports editing and deleting of all financial records.

