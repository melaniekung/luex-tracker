from flask import Flask, render_template, request, redirect, jsonify
import pandas as pd
import logging
import os

# Set up logging
# Call with app.logger.info()
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

EXPENSE_FILE = "expenses.csv"

# Ensure file exists
if not os.path.exists(EXPENSE_FILE):
    pd.DataFrame(columns=["Date", "Purchase", "Amount", "Notes"]).to_csv(EXPENSE_FILE, index=False)

# Route: Home (Display expenses)
@app.route("/")
def index():
    df = pd.read_csv(EXPENSE_FILE)

    # Calculate total amount
    total = df["Amount"].sum() if not df.empty else 0.00

    return render_template("index.html", expenses=df.to_dict(orient="records"), total=total)

# Route: Add expense
@app.route("/add", methods=["POST"])
def add_expense():
    date = request.form.get("date")
    purchase = request.form.get("purchase")
    amount = request.form.get("amount")
    notes = request.form.get("notes")

    # Convert to float and format to 2 decimal places
    if amount:
        try:
            amount = "{:.2f}".format(float(amount))
        except ValueError:
            amount = "0.00"

    if purchase and amount:
        amount = float(amount)
        if (date == ""):
            date = pd.Timestamp.today().strftime('%m-%d-%Y')
        try:
            df = pd.read_csv(EXPENSE_FILE, keep_default_na=True)
            df['ID'] = df.index + 1
            new_data = pd.DataFrame({"Date": [date],
                                     "Purchase": [purchase],
                                     "Amount": [amount],
                                     "Notes": [notes]})
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(EXPENSE_FILE, index=False)
        except ValueError:
            pass  # Ignore invalid input

    return redirect("/")

@app.route("/delete-expense/<int:id>", methods=["POST"])
def delete_expense(id):
    try:
        df = pd.read_csv(EXPENSE_FILE)
        if id in df['Id'].values:
            df = df[df['Id'] != id]
            df.to_csv(EXPENSE_FILE, index=False)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "ID not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/update-expense/<int:id>", methods=["POST"])
def update_expense(id):
    try:
        df = pd.read_csv(EXPENSE_FILE)

        if id in df['Id'].values:
            # Get the updated data from the request
            updated_data = request.json  # Expecting JSON with the updated fields

            # Find the row and update the values
            df.loc[df['Id'] == id, 'Date'] = updated_data.get('Date', df.loc[df['Id'] == id, 'Date'].values[0])
            df.loc[df['Id'] == id, 'Purchase'] = updated_data.get('Purchase', df.loc[df['Id'] == id, 'Purchase'].values[0])
            df.loc[df['Id'] == id, 'Amount'] = updated_data.get('Amount', df.loc[df['Id'] == id, 'Amount'].values[0])
            df.loc[df['Id'] == id, 'Notes'] = updated_data.get('Notes', df.loc[df['Id'] == id, 'Notes'].values[0])

            # Save the updated DataFrame
            df.to_csv(EXPENSE_FILE, index=False)

            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "ID not found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
