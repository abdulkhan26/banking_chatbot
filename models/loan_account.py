from database import get_db_connection
import logging

class LoanAccount:
    @staticmethod
    def create_loan_account(name, pin, account_number, loans):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO loan_accounts (name, pin, account_number, loans)
                VALUES (?, ?, ?, ?)
            ''', (name, pin, account_number, loans))
            conn.commit()
            logging.info(f"✅ Loan account {account_number} created successfully!")
        except Exception as e:
            logging.error(f"❌ Error creating loan account: {e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_loan_options():
        """
        Simulate available loan options without retrieving from the database.
        """
        return {
            "1": ("Personal Loan", "For personal expenses like travel, education, or emergencies."),
            "2": ("Home Loan", "For purchasing or renovating a house."),
            "3": ("Car Loan", "For buying a new or used vehicle."),
            "4": ("Business Loan", "For expanding or starting a business.")
        }

    @staticmethod
    def determine_loan_eligibility(status, loan_type, salary=0, business_turnover=0):
        """
        Determines loan eligibility based on employment type and income details.
        """
        loan_multipliers = {
            "Personal Loan": 6,  # 6x salary or 6% of turnover
            "Home Loan": 25,  # 25x salary or 12% of turnover
            "Car Loan": 12,  # 12x salary or 8% of turnover
            "Business Loan": 18  # 18x salary or 15% of turnover
        }

        if loan_type not in loan_multipliers:
            return {"status": "Error", "message": "❌ Invalid loan type selected."}

        if status == "employed":
            if salary < 10000:
                return {"status": "Rejected", "loan_amount": 0, "message": "❌ Minimum salary must be ₹10,000 to qualify."}
            max_loan_amount = salary * loan_multipliers[loan_type]

        elif status == "self-employed":
            if business_turnover < 500000:
                return {"status": "Rejected", "loan_amount": 0, "message": "❌ Business turnover must be at least ₹5L."}
            max_loan_amount = business_turnover * (loan_multipliers[loan_type] / 100)

        else:
            return {"status": "Error", "message": "❌ Invalid employment status."}

        return {
            "status": "✅ Approved",
            "loan_type": loan_type,
            "loan_amount": round(max_loan_amount, 2),
            "message": f"🎉 Congratulations! You are eligible for a {loan_type}. Max loan: ₹{round(max_loan_amount, 2)}."
        }


