# Expense Tracker Web Application

A full-stack expense management web application that allows users to track income, expenses, savings, and visualize financial data using interactive graphs. Built using **Flask**, **SQLite**, and **Matplotlib**, it offers insights and spending suggestions based on user input.

## Features

- ✅ User authentication (login/register)
- ➕ Add income, expenses, and savings transactions
- 📊 Real-time dashboard with financial metrics
- 📅 Date and category-based statistics
- 📈 Interactive financial graphs
- 🤖 Smart spending analyzer with advice
- 👤 User profile management
- 💳 Balance tracking (Income - Expenses - Savings)

## Tech Stack

| Component          | Technology   |
|--------------------|--------------|
| Frontend           | HTML5, CSS3  |
| Backend            | Python Flask |
| Database           | SQLite3      |
| Data Visualization | Matplotlib   |

## Project Structure

```
        EXPENSE_TRACKER/ 
            │ ├── static/ 
                │ ├── css/ 
                │ │ └── style.css 
                │ └── graphs/ 
                │ │ └── graph_X.png (auto-generated) 
            │ ├── templates/ 
                │ ├── base.html 
                │ ├── index.html 
                │ ├── dashboard.html 
                │ ├── add_expense.html 
                │ ├── statistics.html 
                │ └── stats_result.html 
            │ ├── utils/ 
                │ ├── analyzer.py 
                │ ├── filters.py 
                │ └── graph.py 
            │ ├── app.py 
            ├── expense_data.db (auto-gemerated)
            ├── requirements.txt 
            ├── .env
            └── .gitignore
```
## Getting Started

### Prerequisites
- Python 3.6+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jeslipriya/EXPENSE_TRACKER.git
cd EXPENSE_TRACKER
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the application:
```
python app.py
```

4. Access the application at: ```http://127.0.0.1:5000/```

## Configuration

The .gitignore file include:
```
<!-- graph images -->
/static/graphs/ 
*.png

<!-- database -->
*.db

<!-- complied files -->
__pycache__/
*.pyc

<!-- Ignore virtual environment -->
venv/
.env

```

## Future Improvements

- Data export (PDF/CSV)
- Monthly budget goals
- Recurring transactions
- Email notifications
- Mobile-responsive design

## License

This project is not licensed and for **educational purpose**, **do not modify this code.**

## Author
### Jesli
Computer Science Student
